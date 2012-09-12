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

    def total(self):
       """
       Return total"
       """
       return self.data['total']



if __name__=="__main__":
    s=Single_query('admissions')
    print s.monthly()
