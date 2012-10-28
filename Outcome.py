from core import *
from Count import *
from Distribute import *
from Scatter import *
from Compare import *
from operator import itemgetter
import numpy
import scipy.stats as stat
class Outcome:
    """
    Class for a data set for counting statistics.
    Has the following methods:
        __init__(self,groups): set up the class and query the database
        _res(self): private method the proccess the data into a count stat
        results(self): Returns a dictionary of results
        numbers(self): returns only the numerical values
        labels(self): returns only the labels
    """
    def __init__(self,outcome,dependent_variable,outcome_calculation=[],dep_var_cutoff=[],dep_var_calculation=[]):
        """
            Initialize the class and query the database for data. Also gets the information about the different variables in goups
        """
        self.variables={}
        i=0;
        c=0
        
        outcome_variable=variable(outcome[0]);
        dep_var_variable=variable(dependent_variable[0])
        # Find types of stats we want to use.
        types=self.determine_stats(outcome_variable['type'],dep_var_variable['type'])
        data={}
        if 'counting' in types:
            data['counting']=Count([outcome[0],dependent_variable[0]],dep_var_cutoff,outcome_calculation+dep_var_calculation)
        else:
            if 'distribution' in types:
                if outcome_calculation==[]:
                    oc=''
                else:
                    oc=outcome_calculation[0]
                if 'numeric' not in dep_var_variable['type'] or ('numeric' in dep_var_variable['type'] and dep_var_cutoff!=[]):
                    data['distribution']=Distribute(outcome[0],dependent_variable,oc,dep_var_calculation,dep_var_cutoff)
                else:
                    data['distribution']=Distribute(outcome[0],[])
            if 'comparisson' in types:
                if 'numeric' not in dep_var_variable['type'] or ('numeric' in dep_var_variable['type'] and dep_var_cutoff!=[]):
                    data['comparisson']=Compare(outcome[0],dependent_variable,outcome_calculation[0],dep_var_calculation,dep_var_cutoff)
            if 'scatter' in types:
                print (outcome[0],dependent_variable[0]),(outcome_calculation[0],dep_var_calculation[0])
                data['scatter']=Scatter((outcome[0],dependent_variable[0]),(outcome_calculation[0],dep_var_calculation[0]))
        self.data=data
        self.outcome=outcome_variable
        self.outcome_pretty=self.outcome['pretty_name']
        self.dependent_variable=dep_var_variable
        self.dependent_pretty=dep_var_variable['pretty_name']
        

    def determine_stats(self,outcome_type,dep_var_type):
        types=[]
        if 'numeric' in outcome_type:
            # We want comparisson or scatter plot
            types.append('comparisson')
            if 'numeric' in dep_var_type:
                #Scatter plot + comparisson if cutoff
                types.append('scatter')
            types.append('distribution')
        else: 
            types.append('counting')
        return types

if __name__=='__main__':
    o=Outcome('cd4_count','height',outcome_calculation="last",dep_var_calculation=["first"],dep_var_cutoff=[100])
    print o.data
    
