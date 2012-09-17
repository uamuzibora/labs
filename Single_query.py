from core import *
class Single_query:
    """
    Class for executing single gueries
    Functions:
        __init__(self,field): set class up and query database 
        monthly(self)
        yearly(self)
        total(self)
        Returns the corresponding stat
    """
    def __init__(self,field):
        """
        Set up the class and query the database
        """

        self.data=single_query(field)
        

        self.field=variable(field)
           
    def monthly(self):
        """
        Returns monthly stats.
        """
        months=[]
        data=[]
        for month in sorted(self.data['monthly'].keys()):
            months.append(month)
            data.append(self.data['monthly'][month])
        return (months,data)

    def monthly_cumulative(self):
        """
        Returns monthly stats.
        """
        if 'monthly_N' in self.data.keys(): 
            months=[]
            data=[]
            N=[]
            for month in sorted(self.data['monthly'].keys()):
                months.append(month)
                previous=0
                previous_N=0

                if len(data)>=1:
                    previous=data[-1]
                    previous_N+=sum(N[:-1])
                N.append(self.data['monthly_N'][month])
                data.append((self.data['monthly'][month]*self.data['monthly_N'][month]+previous*previous_N)/sum(N))
        else:
            months=[]
            data=[]
            for month in sorted(self.data['monthly'].keys()):
                months.append(month)
                previous=0
                if len(data)>=1:
                    previous=data[-1]
                data.append(self.data['monthly'][month]+previous)


        return (months,data)
    def yearly(self):
        """
        Returns yearly stats.
        """
        years=[]
        data=[]
        for year in sorted(self.data['yearly'].keys()):
            years.append(year)
            data.append(self.data['yearly'][year])

        return (years,data)
    def yearly_cumulative(self):
        """
        Returns yearly cumulative stats.
        """

        if 'yearly_N' in self.data.keys(): 
            years=[]
            data=[]
            N=[]
            for year in sorted(self.data['yearly'].keys()):
                years.append(year)
                previous=0
                previous_N=0
                if len(data)>=1:
                    previous=data[-1]
                    previous_N=sum(N)

                N.append(self.data['yearly_N'][year])
                data.append((self.data['yearly'][year]*self.data['yearly_N'][year]+previous*previous_N)/sum(N))
        else:
            years=[]
            data=[]
            for year in sorted(self.data['yearly'].keys()):
                years.append(year)
                previous=0
                if len(data)>=1:
                    previous=data[-1]
                data.append(self.data['yearly'][year]+previous)

        return (years,data)     
        
    def total(self):
       """
       Return total"
       """
       return self.data['total']



if __name__=="__main__":
    s=Single_query('admissions')
    print s.yearly()
