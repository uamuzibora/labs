#Importing need modules
#import os
import numpy
from scipy import stats
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
    
    return db.DB(user=login,password=password,database=database,host=host,driver="mysql")



def single_query(field):
    """
    Query the database for a single query not a query for each patient. Eg How many patient are enrolled.
    The variable will contain the exact query to the database and we will return the following data
    {'total':current_total,'monthly':{'Jan 2012':number that month,...},'yearly':{2012:number that year'...}}

    """
    

    db=db_connect();
    field=variable(field)
    if field['table'] !='single_query':
        return None
    if field['type']=="single_query_date":
        query=field['query']
        result=db.query_list(query) # Should be a list of dates
        total=len(result)# Current total
    # Go through dates and create montly and yearly stats
        monthly={}
        yearly={}
        for r in result:
            r=r[0]

            month=r.replace(day=1,hour=0,minute=0,second=0)
            year=r.replace(month=1,day=1,hour=0,minute=0,second=0)
        
            if month in monthly.keys():
                monthly[month]+=1
            else:
                monthly[month]=1
            if year in yearly.keys():
                yearly[year]+=1
            else:
                yearly[year]=1
        return {'total':total,'monthly':monthly,'yearly':yearly}
    elif field['type']=="single_query_date_difference":
        res=db.query_dict("Select patient_id as id,date_enrolled as date from patient_program where program_id=1")
        admission={}
        for r in res:
            admission[r['id']]=r['date']

        query1={}
        query2={}
        data={}

        res=db.query_dict(field['query1'])

        for r in res:
            query1[r['id']]=r['date']
        res=db.query_dict(field['query2'])
        for r in res:
            query2[r['id']]=r['date']
        monthly={}
        monthly_N={}
        yearly={}
        yearly_N={}
        tot=[]
        i=0
        for p in query1.keys():
            if p in query2.keys():
                date=admission[p]
                month=date.replace(day=1,hour=0,minute=0,second=0)
                year=date.replace(month=1,day=1,hour=0,minute=0,second=0)
        
                ans=(query2[p]-query1[p]).days
                if ans > 0 and 5*365:
                    i+=1
                    tot.append(ans)
                    
                    if month in monthly.keys():
                        monthly[month].append(ans)
                        monthly_N[month]+=1
                    else:
                        monthly[month]=[ans]
                        monthly_N[month]=1
                    if year in yearly.keys():
                        yearly[year].append(ans)
                        yearly_N[year]+=1
                    else:
                        yearly[year]=[ans]
                        yearly_N[year]=1
                    
        
        for month in monthly.keys():
            monthly[month]=numpy.average(monthly[month])
        for year in yearly.keys():
            yearly[year]=numpy.average(yearly[year])
        total=numpy.average(tot)
#print len(tot),len(query1),len(query2),len(admission)
        return {'total':total,'monthly':monthly,'yearly':yearly,'yearly_N':yearly_N,'monthly_N':monthly_N}


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
    
    #We need to determine which tables we need to query
    # and encoutners/observations
    
    patient_fields={};
    person_fields={}
    person_attribute_fields={}
    observation_fields={};
    
   

    data={};
    #Sort out the strings need for the sql queries based on tables
    variables={}
    for f in fields:
        variables[f]=variable(f)
        if variables[f]['table']== 'patient':
            patient_fields[f]=variables[f]['field'];
        elif variables[f]['table'] =='person':
            person_fields[f]=variables[f]['field'];
        elif variables[f]['table']  =='person_attribute':
            person_attribute_fields[f]=variables[f]['field'];
        elif variables[f]['table']  =='observation':
            observation_fields[f]=variables[f]['field'];
    # Find all the information from Patients
   
    res=db.query_dict('Select '+','.join(['patient_id']+patient_fields.values())+ ' from patient order by patient_id')
#    print res
    patients=[i['patient_id'] for i in res];
   
    for r in res:
        data[r['patient_id']]={};
   
        for f in patient_fields.keys():
            if variables[f]['type']=='numeric_expression' and r[patient_fields[f]]:
                expression=variables[f]['expression'];
                final_expression=expression.replace('$var',"r[patient_fields[f]]")
                if r[patient_fields[f]] !=None:
                    r[patient_fields[f]]=eval(final_expression)
            data[r['patient_id']][f]=r[patient_fields[f]];
   

    # Need start date for each patient. 

    res=db.query_dict("Select "+'patient_id,date_enrolled '+" from patient_program where program_id=1")
    for r in res:
        data[r['patient_id']]['date']=r['date_enrolled'];

    # Find information from person
    res=db.query_dict("Select "+' , '.join(['person_id']+person_fields.values())+" from person order by person_id")
    for r in res:
        #data[r['pid']]['date']=r['hiv_positive_clinic_start_date'];
        if r['person_id'] in data.keys():
            for f in person_fields.keys():
                if variables[f]['type']=='numeric_expression' and r[person_fields[f]]:
                    expression=variables[f]['expression'];
                    final_expression=expression.replace('$var',"r[person_fields[f]]")
                    if r[person_fields[f]] !=None:
                        r[person_fields[f]]=eval(final_expression)
                data[r['person_id']][f]=r[person_fields[f]];


            
    # Find informations from results
    for f in observation_fields:

        #id=db.query_dict("Select id from tests where name=%s",result_fields[f])[0]['id']
        if variables[f]['type']=='numeric_multiple':
            res=db.query_dict("SELECT obs.person_id,obs.value_numeric,enc.encounter_datetime from obs LEFT JOIN encounter as enc on enc.encounter_id=obs.encounter_id where obs.concept_id = %s ",variables[f]['concept'])

            temp={}

            for r in res:
#                print r
                if r['person_id'] in temp.keys():
                    temp[r['person_id']][r['encounter_datetime']]=r['value_numeric']
                else:
                    temp[r['person_id']]={r['encounter_datetime']:r['value_numeric']}
            for key in temp.keys():
                avg=numpy.average(temp[key].values())
                sorted_keys=sorted(temp[key].keys())
                t=[]
                y=[]
                for i in sorted_keys:
                    d=i-sorted_keys[0]
                    t.append(d.total_seconds()/(2548800)) # Seconds per month
                    y.append(temp[key][i])
                slope, intercept, r_value, p_value, std_err = stats.linregress(t,y)
                if slope!=slope:
                    slope=None
                data[key][f]={'Mean':avg,'First':temp[key][sorted_keys[0]], 'Last':temp[key][sorted_keys[-1]],'Regression':slope}; # SORT OUT REGRESSION
                #if data[r["pid"]][f]['Regression'] !=None:
                #   data[r["pid"]][f]['Regression']*= (3600*24*30.41)


        elif variables[f]['type']=='boolean':
            require_answer='concept_answer' in variables[f].keys()
            if require_answer:
                res=db.query_dict("SELECT obs.person_id from obs where obs.concept_id = %s and voided=0 and value_coded=%s",(variables[f]['concept'],variables[f]['concept_answer']))
            else:
                res=db.query_dict("SELECT obs.person_id from obs where obs.concept_id = %s and voided=0",variables[f]['concept'])
            patients_with_observation=[]
            for r in res:
                patients_with_observation.append(r['person_id'])
            for key in data.keys():
                if key in patients_with_observation:
                    data[key][f]=variables[f]['yes']
                else:
                    data[key][f]=variables[f]['no']
        elif variables[f]['type']=='text_multiple':
            if 'no_encounter' in variables[f].keys():
                res=db.query_dict("SELECT obs.person_id,obs.value_coded from obs where obs.concept_id = %s and obs.voided=0",variables[f]['concept'])
                temp={}
                lookup={}
                for r in res:
                
                    concept=r['value_coded']
                    if concept in lookup.keys():
                        text=lookup[concept]
                    else:
                        lo=db.query_dict("SELECT name from concept_name where concept_id=%s",concept)
                        text=lo[0]['name']
                        lookup[concept]=text
                    data[r['person_id']][f]=text
            else:

                res=db.query_dict("SELECT obs.person_id,obs.value_coded,enc.encounter_datetime from obs JOIN encounter as enc on enc.encounter_id=obs.encounter_id where obs.concept_id = %s and obs.voided=0 order by enc.encounter_datetime",variables[f]['concept'])

                temp={}
                lookup={}
                for r in res:
                    if r['person_id'] in temp.keys():
                        temp[r['person_id']][r['encounter_datetime']]=r['value_coded']
                    else:
                        temp[r['person_id']]={r['encounter_datetime']:r['value_coded']}
                for key in temp.keys():
                    dates=sorted(temp[key].keys())
                    if variables[f]['which']=="last":
                        date=dates[-1]
                    elif variables[f]['which']=="first":
                        date=dates[0]
                    concept=temp[key][date]
                    if concept in lookup.keys():
                        text=lookup[concept]
                    else:
                        lo=db.query_dict("SELECT name from concept_name where concept_id=%s",concept)
                        text=lo[0]['name']
                        lookup[concept]=text
                    data[key][f]=text

    #Deal with date difference
    for f in fields:
        if variables[f]['type']=="numeric_date_difference":
            query1={}
            query2={}
            if variables[f]['query1'] !=':admission:':
                res=db.query_dict(variables[f]['query1'])
                for r in res:
                    query1[r['id']]=r['date']
            else:
                for p in data.keys():
                    if 'date' in data[p].keys():
                        query1[p]=data[p]['date']
            if variables[f]['query2'] !=':admission:':
                res=db.query_dict(variables[f]['query2'])
                for r in res:
                    query2[r['id']]=r['date']
            else:
                for p in data.keys():
                    if 'date' in data[p].keys():
                        query2[p]=data[p]['date']
            for p in data.keys():

                if p in query1.keys() and p in query2.keys():
                    ans=(query2[p]-query1[p]).days
                    if ans > 0 and ans < 5*365:
                        data[p][f]=ans
                    else:
                        data[p][f]=None

                else:
                    data[p][f]=None
        elif variables[f]['type']=="boolean_sql":
             res=db.query_dict(variables[f]['sql'])
             patients_in_query=[]
             for r in res:
                 patients_in_query.append(r['patient_id'])
             for p in data.keys():
                 if p in patients_in_query:
                     data[p][f]=variables[f]['yes']
                 else:
                     data[p][f]=variables[f]['no']
    for d in data:
        
        for f in observation_fields:
            if f not in data[d].keys():
                if variables[f]['type']=='numeric_multiple':
                    data[d][f]={'Mean':None,'First':None, 'Last':None,'Regression':None};
                if variables[f]['type']=='numeric_occurrence':
                    data[d][f]={'Count':0,'Interval':None}
                if variables[f]['type']=='text_multiple':
                    data[d][f]=variables[f]['none']
                if variables[f]['type']=='boolean':
                    data[d][f]=variables[f]['no']


    return data
def first_patient():
    """
    Returns the hiv_positive_clinic_start_date for the first patient
    """
    db=db_connect()
    return db.query_list('SELECT min(date_enrolled) from patient_program where program_id=1')[0][0]

def distinct_values(name):
    """
        Returns the number of distinct values(Including null) of a field in table
    """
    v=variable(name)
    db=db_connect();
    if v['type']=="text_multiple":
        distinct=int(db.query_dict('SELECT count(Distinct value_coded) as count from obs where concept_id='+v['concept'])[0]['count'])+1
        
    else:
        distinct= int(db.query_dict('SELECT count(Distinct '+v['field']+') as count FROM '+v['table'])[0]['count'])

        m=int(db.query_dict('SELECT count('+v['field']+') as count FROM '+v['table'])[0]['count'])
        tot=int(db.query_dict('SELECT count(*) as count FROM '+v['table'])[0]['count'])
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
    m=int(db.query_dict('SELECT count('+v['field']+') as count FROM '+v['table'])[0]['count'])
    tot=int(db.query_dict('SELECT count(*) as count FROM '+v['table'])[0]['count'])
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
            if ret['type']=='single_query_date':
                ret['query']=line_array[5]
            if ret['table']=='observation':
                ret['concept']=line_array[5]
            if ret['type']=='text_multiple':
                ret['which']=line_array[6]
                ret['none']=line_array[7]
                if len(line_array)>8:
                    ret['no_encounter']=True
            if ret['type']=='boolean':
                ret['yes']=line_array[6]
                ret['no']=line_array[7]
                if len(line_array)>8:
                    ret['concept_answer']=line_array[8]
            if ret['type']=="numeric_date_difference":
                ret['query1']=line_array[5]
                ret['query2']=line_array[6]
            if ret['type']=="single_query_date_difference":
                ret['query1']=line_array[5]
                ret['query2']=line_array[6] 
            if ret['type']=='boolean_sql':
                ret['sql']=line_array[5]
                ret['yes']=line_array[6]
                ret['no']=line_array[7]

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
#    print query(['cd4_count'])
#    print single_query('admissions')

#    print distinct_values('sex')



