import scipy.stats as stats
from core import *
class Compare:
    """
    Class for comparing numerical value for different groups
    Functions:
        __init__(self,xy,calculation=[]): set class up and query database for all nescesary fields
        _res(self): Calculates the means, and p-values for all groups
        numbers(sefl): Returns all the calculated numbers 
        labels(self): Returns labels
    """
    def __init__(self,var,groups,calcvariable='',calculation=[],cutoff=[]):
        """
        Set up the class and query the database
select p.pid, first(k.value_decimal),last(k.value_decimal),avg(k.value_decimal) from patients p LEFT JOIN results r on p.pid=r.pid JOIN (SELECT value_decimal, result_id from result_values JOIN results on results.id=result_id order by test_performed) k on k.result_id=r.id where r.test_id=2 group by p.pid;



        """
        self.variables={}
        c=0
        i=0
        self.data=query(groups+[var])
        self.groups=groups
        for g in groups:
            v=variable(g);
            if v['type']=='numeric_multiple':
                v['calculation']=calculation[c]
                v['cutoff']=int(cutoff[i])
                i+=1
                c+=1
            elif 'numeric' in v['type']:
                v['cutoff']=int(cutoff[i])
                i+=1

            self.variables[g]=v
        # If variable is the same field as one of the groups
        if var in self.variables:
            postfix='*'
        else:
            postfix=''
        self.variables[var+postfix]=variable(var)
        self.var_post=var+postfix
        if calcvariable !='':
            self.variables[self.var_post]['calculation']=calcvariable
        self.var=var
        self.var_pretty=self.variables[var]['pretty_name']
        self.stat={}

    def _res(self):
        """
        Workhorse of the class. The function identifies the different subgroups and then calculates means and p-values for all subgroups.
        Fills the stat dictinoary according to the following format:
            {subgroup:{'mean':mean,'p-value':p-value,'N': N}}
        """
        tot=[]
        temp_stat={}
        for d in self.data.values():
            subgroup=''
            #identify subgroups 
            for g in self.groups:
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
            #extracting value
            if  type(self.variables[self.var_post])==dict and type(d[self.var])==dict and type(d)==dict and type(self.variables)==dict and 'calculation' in self.variables[self.var_post].keys():
                value=d[self.var][self.variables[self.var_post]['calculation']]
            else:
                value=d[self.var]
            if subgroup in temp_stat.keys():
                if value != None:
                    temp_stat[subgroup].append(value)
            else:
                if value != None:
                    temp_stat[subgroup]=[value]
            if value!=None:
                tot.append(value)
        #calculate mean, and standard deviation 
        tot_mean=numpy.mean(tot)
        tot_std=numpy.std(tot)
        tot_new=[]
        l=tot_mean-5*tot_std
        u=tot_mean+5*tot_std
        # We choose to not include values that are more than 4 STD from the mean.
        # Mainly to not include wrongly inputed variables
        for t in tot:
            if(t>l and t<u):
                tot_new.append(t)
        tot=tot_new
        for sg in temp_stat.keys():
            tmp=[]
            for n in temp_stat[sg]:
                if(n>l and n<u):
                    tmp.append(n)
            temp_stat[sg]=tmp
        #Calculate mean, std for each sub group

        for subgroup in temp_stat.keys():
            if subgroup !='':
                mean=numpy.mean(temp_stat[subgroup])
                total=[]
                for sg in temp_stat.keys():
                    if sg!=subgroup:
                        total+=temp_stat[sg]
                # Perform t-test to see if a if difference is significant
                if len(temp_stat[subgroup])>0:
                    p_value=stats.ttest_ind(temp_stat[subgroup],total)[1]
                else:
                    p_value=1
                    mean=0
                self.stat[subgroup]={'mean':mean,'p_value':p_value,'N':len(temp_stat[subgroup])}
        self.stat['Total']={'mean':numpy.mean(tot),'p_value':1,'N':len(tot)}
        #Numbers in each group
    def numbers(self):
        """
        Returns  lists. One with means, the other with p-values and one with N
        
        """
        if len(self.stat)==0:
            self._res()
        mean=[]
        p_value=[]
        N=[]
        for s in sorted(self.stat.keys()):
            mean.append(self.stat[s]['mean'])
            p_value.append(self.stat[s]['p_value'])
            N.append(self.stat[s]['N'])
        return (mean,p_value,N)
    def labels(self):
        """
        Returns all the subgroups
        """
        if len(self.stat)==0:
            self._res()

        return (sorted(self.stat.keys()))


if __name__=="__main__":
    d=Compare('age',[])
    d._res()
    print d.stat
