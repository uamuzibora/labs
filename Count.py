from core import *
from operator import itemgetter
import numpy
import scipy.stats as stat
class Count:
    """
    Class for a data set for counting statistics.
    Has the following methods:
        __init__(self,groups): set up the class and query the database
        _res(self): private method the proccess the data into a count stat
        results(self): Returns a dictionary of results
        numbers(self): returns only the numerical values
        labels(self): returns only the labels
    """
    def __init__(self,groups,cutoff=[],calculation=[],start='',end=''):
        """
            Initialize the class and query the database for data. Also gets the information about the different variables in goups
        """
        
        self.variables={}
        i=0;
        c=0
	
        for g in groups:
            self.variables[g]=variable(g);
            if self.variables[g]['type']=='numeric_expression':
                self.variables[g]['cutoff']=int(cutoff[i])
                i+=1
            if self.variables[g]['type']=='numeric_multiple':
                self.variables[g]['cutoff']=int(cutoff[i])
                i+=1
                self.variables[g]['calculation']=calculation[c]
                c+=1
        if start != '':
            self.start=calendar.timegm(time.strptime(start,"%Y-%m-%d"))
        else:
            self.start=calendar.timegm(time.strptime('1900-01-01',"%Y-%m-%d"))
        if end != '':
            self.end=calendar.timegm(time.strptime(end,"%Y-%m-%d"))
        else:
            self.end=time.time()
        self.groups=groups
         
        self.data=query(groups)
        self.months=[]
        self.stat={}
        self.probs={}
        
    def _res(self):
        """
        Procces the data from the database so it can be displayed as counting stats
        Saves the results to self.stat in the following format:
        self.stat={x-value1:{subgroup1:value,subgroup2:value},...}
        """
        
        number={}
        #Find the number of distinct values for each of the variables.
        # Then we make the variable with the highest number the xaxis

        for g in self.variables:
            if self.variables[g]['type']=='numeric_multiple':
                number[g]=2
            elif 'cutoff' in self.variables[g].keys():
                
                number[g]=2+has_none(g)
            
            else:
                number[g]=distinct_values(g)
        sort=sorted(number.items(),key=itemgetter(1), reverse=True)
        xaxis=sort[0][0]
        #Go thourgh all the values to put them in the right subgroups
        n=0
        for d in self.data.values():
            if d['date']!=None:
                date=calendar.timegm(d['date'].timetuple())
            else:
                date=self.start-1
            if date>=self.start and date<=self.end:
                
                if 'cutoff' in self.variables[xaxis].keys():
                    c=self.variables[xaxis]['cutoff']
                    if 'calculation' in self.variables[xaxis].keys():
                        
               	        if d[xaxis][self.variables[xaxis]['calculation']]==None:
                    	    x='None'
                        elif d[xaxis][self.variables[xaxis]['calculation']] <= c:
                            x=self.variables[xaxis]['calculation']+' '+self.variables[xaxis]['pretty_name']+'<'+str(c)
                        elif d[xaxis][self.variables[xaxis]['calculation']]>c:
                            x=self.variables[xaxis]['calculation']+' '+self.variables[xaxis]['pretty_name']+'>'+str(c)



                    else:
                        if d[xaxis]==None or d[xaxis]=='':
                            x='None'
                        elif d[xaxis]<c:
                            x=self.variables[xaxis]['pretty_name']+'<'+str(c)
                        elif d[xaxis]>=c:
                            x=self.variables[xaxis]['pretty_name']+'>'+str(c)
                else:
                    if d[xaxis]==None:
                        x="None"
                    else:
                        x=d[xaxis];
                # Make the subgroup name from all the combinations of values
                subgroup=''
                for s in sort[1:]:
                
                    if 'cutoff' in self.variables[s[0]].keys():

                    
                        c=self.variables[s[0]]['cutoff']
                        if 'calculation' in self.variables[s[0]].keys():
                       
                            if d[s[0]][self.variables[s[0]]['calculation']]==None:
                                subgroup+='None, '
                            elif d[s[0]][self.variables[s[0]]['calculation']] <= c:
                                subgroup+=self.variables[s[0]]['calculation']+' '+self.variables[s[0]]['pretty_name']+'<'+str(c)+', '
                            elif d[s[0]][self.variables[s[0]]['calculation']]>c:
                                subgroup+=self.variables[s[0]]['calculation']+' '+self.variables[s[0]]['pretty_name']+'>'+str(c)+', '

                        else:
                            if d[s[0]]==None:
                                subgroup+='None, '

                            elif d[s[0]]<=c:
                                subgroup+=self.variables[s[0]]['pretty_name']+'<'+str(c)+', '
                            elif d[s[0]]>=c:
                                subgroup+=self.variables[s[0]]['pretty_name']+'>'+str(c)+', '
                    else:
                        subgroup+=str(d[s[0]])+', '
                subgroup=subgroup[:-2]
                if len(sort)==1:
                    subgroup=self.variables[sort[0][0]]['pretty_name']
            
            
                if x in self.stat.keys():
                    if subgroup in self.stat[x].keys():
                        self.stat[x][subgroup]+=1
                    else:
                        self.stat[x][subgroup]=1
                else:

                    self.stat[x]={subgroup:1}

       #CHI-SQUARED TEST:
       # If we have exactly two variables, we perform a Chi-squared test.

        if len(self.variables)==2:
            probs={}

            nu=len(self.stat[self.stat.keys()[0]])
            
            rows=numpy.zeros(nu)
            cols=numpy.zeros(nu)
            
            for x in self.stat:                    

                rows=numpy.zeros(2)
                cols=numpy.zeros(nu)
                
                others=numpy.zeros(nu)
                this=numpy.zeros(nu)
                for y in self.stat:
                    i=0
                    if x!=y:
                        
                        for k in self.stat[y].values():
                           
                            others[i]+=k
                            i+=1
                        
                    
                i=0    
                for val in self.stat[x].values():
                    this[i]=val
                    cols[i]=val+others[i]
                    i+=1
                    
                rows[0]=sum(this)
                rows[1]=sum(others)
                chi=0
                N=float(sum(rows))
                exp_t=rows[0]*cols/N
                exp_o=rows[1]*cols/N
                
                
                
                chi=sum((this-exp_t)**2/exp_t)+sum((others-exp_o)**2/exp_t)
                deg_of_free=len(cols)-1
                #print chi, deg_of_free
                p=stat.chisqprob(chi,deg_of_free)
                probs[x]=p
            
            #print self.stat
            self.probs=probs
            #print probs
                        
    
    
    def timeline(self):
        """
        Uses up  to two variables
        Function that saves time series data for the counting statistics, in monthly an yearly batches
        {year:{year1:number,...},month:{month1:number,....}}
        """
        #Find the number of distinct values for each of the variables.
        # Then we make the variable with the highest number the xaxis
        timeline={}
        months=[]
        #Go thourgh all the values to put them in the right subgroups
	
        for d in self.data.values():               
            
            # Make the subgroup name from all the combinations of values
            subgroup=''
            for g in self.groups[0:2]:# Only use the first two variables in the timeline.
                
                if 'cutoff' in self.variables[g].keys():
                    c=self.variables[g]['cutoff']

                    if 'calculation' in self.variables[g].keys():
                        
                        if d[g][self.variables[g]['calculation']]==None:
                            subgroup+='None, '
                        elif d[g][self.variables[g]['calculation']] <= c:
                            subgroup+=self.variables[g]['calculation']+' '+self.variables[g]['pretty_name']+'<'+str(c)+', '
                        elif d[g][self.variables[g]['calculation']]>c:
                            subgroup+=self.variables[g]['calculation']+' '+self.variables[g]['pretty_name']+'>'+str(c)+', '

                    else:                                             
                       if d[g]==None:
                            subgroup+='None, '

                       elif d[g]<=c:
                           subgroup+=self.variables[g]['pretty_name']+'<'+str(c)+', '
                       elif d[g]>=c:
                           subgroup+=self.variables[g]['pretty_name']+'>'+str(c)+', '
                else:

                    subgroup+=str(d[g])+', '
            subgroup=subgroup[:-2]
            if d['date']!=None:
                month=(d['date'].year,d['date'].month,1,0,0,0)

                 #Use d['date'][0:7] as we are only intrested in the year and month
                if subgroup in timeline.keys():
                
                    if month in timeline[subgroup].keys():
                       timeline[subgroup][month]+=1
                    else:
                        timeline[subgroup][month]=1
                else:
                 timeline[subgroup]={month:1}

                if month not in months:
                  months.append(month)
        
        self.months=sorted(months)
        self.timeline=timeline
            

    def timeline_numbers(self):
        """
        Returns data_month of format: {group:[value1,value2..]}
        """
        if len(self.months)==0:
            self.timeline()
        data={}
        for group in self.timeline:
            data[group]=[]
            for m in self.months:
                if m in self.timeline[group]:
                    data[group].append(self.timeline[group][m])
                else:
                    data[group].append(0)
        
        return data
           

    def timeline_xaxis(self):
        """
        Returns a list of all the months and years
        """
        if len(self.months)==0:
            self.timeline()
        
        return self.months

    def results(self):
        """
        Returns the stat dictionary in the following format:
        {x-value1:{subgroup1:value,subgroup2:value},...}
        """
        if len(self.stat)==0:
            self._res()
        
        return self.stat
    def numbers(self):
        """
        Proccesses the stat dictionary and returns a dictionary with the dataseries to be plotted
        format:
        {Serie1:[data],serie2:[data]}
        """
        ret={}
        if len(self.stat)==0:
            self._res()
        # Create an empty array in ret for each key in stat
        for k in self.stat.keys():
            for key in self.stat[k].keys():
                if key not in ret.keys():
                    ret[key]=[]
        # Populate ret with the y values for each x value for each subgroup(adding a zero if no value is found for that subgroup)
        for k in sorted(self.stat.keys()):
            for key in ret.keys():
                if key in self.stat[k].keys():
                    ret[key].append(self.stat[k][key])
                else:
                    ret[key].append(0)
        return ret
    def probability(self):
        
        """
        Returns the chi-squared p-values
        """
        if len(self.stat)==0:
            self._res()
        if len(self.probs)>0:
            return self.probs
        else: 
            return False
    def xaxis(self):
        """
        Returns the xaxis vales
        """
        ret=[]
        if len(self.stat)==0:
            self._res()


        return sorted(self.stat.keys())




if __name__=='__main__':

    c=Count(['sex'])#'age'],calculation=["First"],cutoff=[30])
    print c.data
    print c.numbers().keys()
    n,p= c.numbers(),c.xaxis()
    c.timeline()
    print c.timeline
