#Importing need modules
#import os
import numpy
from datetime import date
import datetime
import sys
import time,calendar
#importing dbConfig
import db
try:
    from dbConfig import *
    import config
except:
    print "config.py and dbConfig.py are needed. Fill out a copy of the config-default and dbConfig-default and make a copy as config.py and dbConfig.py"
    sys.exit(0)
path=config.path
#functions

def db_connect():
    """
    Retunrs a connection to the database
    """
    
    return db.DB(user=login,password=password,database=database,host=host)


def query(fields):
    
    """
        Queries the database for the information in fields(an array of tuples(field,db_table)).
        Also gets pid, location_id and hiv_clinic_start_date
        If the fields are from the results table, the result, and the date of the result is returned.
        The Dictionary is formatted as follows:
            {pid:{date:hiv_clinic_start_date,'location_id':location_id,field:value,field_results:{date:test_performed,values:[val1,val2...]}}}


    """
    #limit to number of patients
    l=6000
    db=db_connect();
    
    pat_fields={};
    med_info_fields={};
    result_fields={};
    
    data={};
    #Sort out the strings need for the sql queries based on tables
    variables={}
    for f in fields:
        variables[f]=variable(f)
        if variables[f]['table']== 'patients':
            pat_fields[f]=variables[f]['field'];
        elif variables[f]['table'] =='medical_informations':
            med_info_fields[f]=variables[f]['field'];
        elif variables[f]['table']  =='results':
            result_fields[f]=variables[f]['field'];
            
    # Find all the information from Patients
   
    res= db.query_dict('Select '+','.join(['pid','location_id']+pat_fields.values())+ ' from patients order by pid')
   
    patients=[i['pid'] for i in res];
    for r in res:
        data[r['pid']]={'location':r['location_id']};
        for f in pat_fields.keys():
            if variables[f]['type']=='numeric_expression' and r[pat_fields[f]]:
                expression=variables[f]['expression'];
                final_expression=expression.replace('$var',"r[pat_fields[f]]")
                if r[pat_fields[f]] !=None:
                    r[pat_fields[f]]=eval(final_expression)
            data[r['pid']][f]=r[pat_fields[f]];
   

    # Find information from medical_informations
    res=db.query_dict("Select "+' , '.join(['pid','hiv_positive_clinic_start_date']+med_info_fields.values())+" from medical_informations order by pid")
    for r in res:
        data[r['pid']]['date']=r['hiv_positive_clinic_start_date'];
        for f in med_info_fields.keys():
            data[r['pid']][f]=r[med_info_fields[f]];
    # Find informations from results
    for f in result_fields:

        id=db.query_dict("Select id from tests where name=%s",result_fields[f])[0]['id']
        if variables[f]['type']=='numeric_multiple':
            res=db.query_dict("SELECT p.pid,avg(r.value_decimal),first(r.value_decimal),last(r.value_decimal),regr_slope(r.value_decimal,extract(epoch from res.test_performed)) from patients p LEFT JOIN results res on res.pid=p.pid LEFT JOIN (SELECT value_decimal, result_id from result_values LEFT JOIN results on results.id=result_values.result_id order by test_performed) r on r.result_id=res.id where res.test_id= %s group by p.pid",id)
            for r in res:
                data[r["pid"]][f]={'Mean':r['avg'],'First':r['first'], 'Last':r['last'],'Regression':r['regr_slope']};
                if data[r["pid"]][f]['Regression'] !=None:
                   data[r["pid"]][f]['Regression']*= (3600*24*30.41)
        elif variables[f]['type']=='numeric_occurrence':

            res=db.query_dict("SELECT pid,count(id),min(test_performed),max(test_performed) FROM results WHERE test_id= %s GROUP BY pid",id)
            
            for r in res:

                #find numer of days between min and max
                data[r["pid"]][f]={'Count':int(r['count']),'Interval':None}
                if r['count'] !=0:
                    days=(r['max']-r["min"]).days
                    if days!=0:
                        data[r['pid']]['Interval']=days/float(r['count'])
               

                    
                    
        else:

            for p in patients:
                values=db.query_dict("Select result_values.id,result_id,value_decimal,value_text,value_lookup,results.test_performed from result_values LEFT JOIN results on result_values.result_id=results.id where results.pid=%s and results.test_id=%s",(p,id))                      		
                
                for v in values:
                    if v['value_decimal']!=None:
                        val=v['value_decimal'];
                    elif v['value_text']!=None:
                        val=v['value_text'];
                    elif v['value_lookup']!=None:
                        val=v['value_lookup'];
                    data[p][f]={'date':v['test_performed'],'values':val};
    

    #Put in the lookup values
    lookups={}
    for v in variables:
        if variables[v]['type']=='lookup':
            lookups[v]={}
            res=db.query_dict("SELECT id, name FROM %s" % variables[v]['lookup_table'])
            for r in res:
                lookups[v][r['id']]=r['name']
    for d in data:
        
        for f in result_fields:
            if f not in data[d].keys():
                if variables[f]['type']=='numeric_multiple':
                    data[d][f]={'Mean':None,'First':None, 'Last':None,'Regression':None};
                if variables[f]['type']=='numeric_occurrence':
                    
                    data[d][f]={'Count':0,'Interval':None}
        for val in data[d].keys():
            if val in lookups.keys():
                numb=data[d][val];
                if numb:
                    name=lookups[val][numb];
                else:
                    name='None'
                data[d][val]=name
                data[d][val+'_numeric']=numb

    


    return data
def first_patient():
    """
    Returns the hiv_positive_clinic_start_date for the first patient
    """
    db=db_connect()
    return db.query_list('SELECT min(hiv_positive_clinic_start_date) from medical_informations')[0][0]

def distinct_values(name):
    """
        Returns the number of distinct values(Including null) of a field in table
    """
    v=variable(name)
    db=db_connect();
    distinct=int(db.query_dict('SELECT count(Distinct '+v['field']+') FROM '+v['table'])[0]['count'])
    m=int(db.query_dict('SELECT count('+v['field']+') FROM '+v['table'])[0]['count'])
    tot=int(db.query_dict('SELECT count(*) FROM '+v['table'])[0]['count'])
    if tot>m:# We had Nulls. Want to include this in the count
        distinct+=1
    
    return distinct

def has_none(name):
    """
    Returns 1 if the column name has any None values, otherwise returns zero.
    """
    db=db_connect();
    v=variable(name)
    ret=0
    m=int(db.query_dict('SELECT count('+v['field']+') FROM '+v['table'])[0]['count'])
    tot=int(db.query_dict('SELECT count(*) FROM '+v['table'])[0]['count'])
    if tot>m:# We had Nulls. Want to include this in the count
        ret=1
    
    return ret


def variable(name):
    """
        Returns a dictionary with information about the variable name.
        {'name':name,'table':table,'type':type,'lookup_table':lookup_table}
    """
    f=open(path+'variables.txt');
    ret=None;
    for line in f:
        line_array=line.strip().split('&');
        if line_array[0]==name:
            ret={};
            ret['name']=name;
            ret['field']=line_array[1]
            ret['pretty_name']=line_array[2];
            ret['table']=line_array[3];
            ret['type']=line_array[4];
            if ret['type']=='lookup':
                ret['lookup_table']=line_array[5];
            if ret['type']=='numeric_expression':
                ret['expression']=line_array[5];
    f.close();
    return ret
def list_variables():
    """
        Returns a list of all the avaiable variables
    """
    f=open(path+'variables.txt');
    ret=[];
    for line in f:
        line_array=line.strip().split('&');
        ret.append([line_array[0],line_array[2],line_array[4]]);
    return ret


if __name__=='__main__':
    print list_variables()
    print query(['cd4'])



