import scipy.stats as stats
from core import *
class Distribute:
    """
    Class for computing histograms
    Functions:
        __init__(self,xy,calculation=[]): set class up and query database for all nescesary fields
        _res(self): Calculates the means, and p-values for all groups
        numbers(sefl): Returns all the calculated numbers 
        labels(self): Returns labels
    """
    def __init__(self,var,groups,calcvariable='',calculation=[],cutoff=[]):
        """
        Set up class and query the database
        """
        self.variables={}
        c=0
        i=0
        if groups==None:
            groups=[]
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
        v=variable(var)
        self.var_pretty=v['pretty_name']
        
        self.stat={}

    def _res(self):
        """
        Workhorse of the class. The function identifies the different subgroups and then calculates a histogram for each sub group
        Fills the stat dictinoary according to the following format:
            {subgroup:{'lables':labels,'values':values}
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
            #extracting values
            
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
            
        
        # Get the histograms
        for subgroup in temp_stat.keys():
            values,labels=numpy.histogram(temp_stat[subgroup])
            self.stat[subgroup]={'labels':labels,'values':values}
        
    def numbers(self):
        """
        Returns  lists of histogram values and labels.
        
        """
        if len(self.stat)==0:
            self._res()
        return self.stat
    def labels(self):
        """
        Returns all the subgroups
        """
        if len(self.stat)==0:
            self._res()

        return (sorted(self.stat.keys()))



if __name__=="__main__":
    d=Distribute('age',[''])
    d._res()
    print d.stat
