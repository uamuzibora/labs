from core import *
class Scatter:
    """
    Class for generating data for scatter plots.
    Functions:
        __init__(self,xy,calculation=[]): set class up and query database for all fields in xy
        _res(self): Extracts the x and y values 
        numbers(sefl): returns lists of x and y and also the correlation coefficent
        labels(self): Returns the xlabel and ylabel

    """
    def __init__(self,xy,calculation=[]):
        """
        Set up the class and query the database
        """
        self.variables={}
        c=0
        self.data=query(xy)
        self.xy=xy
        for i in xy:
            var=variable(i);
                
            if var['type']=='numeric_multiple':
                var['calculation']=calculation[c]
                c+=1
            # Fix for when both x and y are the same variable, but have different calculations
            if i in self.variables.keys():
                self.variables[i+'*']=var
                self.xy[1]+='*'
            else:
                self.variables[i]=var
        
        
        self.x=[]
        self.y=[]
        
    def _res(self):
        """
        Workhorse of the class. Calculates x and y values for alle the datapoints

        creates self.x,self.y with the x and y-values
        """

        x=[]
        y=[]
        xy=self.xy
        # Hack for  when both x and y are the same variable, but have different calculations
        if xy[1][-1]=='*':
            field=xy[1][0:-1]
        else:
            field=xy[1]
        for d in self.data.values():
            
            if 'calculation' in self.variables[xy[0]]:
                valx=d[xy[0]][self.variables[xy[0]]['calculation']]
            else:
                valx=d[xy[0]]
            if 'calculation' in self.variables[xy[1]]:
                valy=d[field][self.variables[xy[1]]['calculation']]
            else:
                valy=d[field]
            if valx != None and valy != None:
                x.append(valx)
                y.append(valy)
        meanx=numpy.mean(x)
        stdx=numpy.std(x)
        meany=numpy.mean(y)
        stdy=numpy.std(y)
        d=[]
        # We disregard outliers that are more than 4 std from the mean
        for i in range(min(len(x),len(y))):
            if abs(x[i]-meanx)>4*stdx or abs(y[i]-meany)>4*stdy:
                d.append(i)
	for i in sorted(d,reverse=True):
            del x[i]
            del y[i]

        self.x=x
        self.y=y
        
    def numbers(self):
        """
        Returns two lists. One of x values, one of y-values and the correlation coefficent
        
        """
        if len(self.x)==0:
            self._res()
        
        return (self.x,self.y,numpy.corrcoef(numpy.array(self.x),numpy.array(self.y))[0][1])
    def labels(self):
        """
        Returns the xlabel and ylabel
        """
        xlabel=''
        ylabel=''
        if 'calculation' in self.variables[self.xy[0]]:
            xlabel+=self.variables[self.xy[0]]['calculation']+' '
        xlabel+=self.variables[self.xy[0]]['pretty_name']
        if 'calculation' in self.variables[self.xy[1]]:
            ylabel+=self.variables[self.xy[1]]['calculation']+' '
        ylabel+=self.variables[self.xy[1]]['pretty_name']

        return (ylabel,xlabel)

