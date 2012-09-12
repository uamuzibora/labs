import psycopg2
import psycopg2.extras
import MySQLdb
import MySQLdb.cursors



class DB:
    """
    a custom made database wrapper class
    Functions:
    __init__(self,host,user,password,database): Set up database connection
    insert(self,table,dictionary): Insert dictinary of values into table
    in_db(self,table,column,entry): determines if entry of column in table extists
    query_list(self,query,variables): Queries the database, variables hold input variables to avoid sql-injection. Returns a list of results
    query_dict(self,query,variables): Queries the database, variables hold input variables to avoid sql-injection. Returns a dictionary of results

    """
    def __init__(self,host=None,user=None,password=None,database=None,driver="pg"):
        """
        Initialising the database connection
        """
        if driver=="pg":
            if password:
                self.connection=psycopg2.connect(host=host,user=user,password=password,database=database)
            else:#for ident
            
                self.connection=psycopg2.connect(user=user,database=database)
            self.cursor=self.connection.cursor()
        elif driver=="mysql":
            if password:
                self.connection=MySQLdb.connect(host=host,user=user,passwd=password,db=database)
            else:#for ident
            
                self.connection=MySQLdb.connect(user=user,database=database)
            self.cursor=self.connection.cursor()
        self.driver=driver
    def insert(self,table,dictionary):
        """ Inserts a dictinoary into the table, if the dictinoary is a list of dictinonaries it inserts them all"""
        cursor=self.connection.cursor()
        if type(dictionary)==dict:
            statement= "INSERT INTO %s " % table
            statement += "( %s ) " % ','.join(dictionary.keys())
            statement+= "VALUES (%("+ ")s,%(".join(dictionary.keys())+")s)"
           
            cursor.execute(statement,dictionary)
        else:            
            statement= "INSERT INTO %s " % table
            statement += "( %s ) " % ','.join(dictionary[0].keys())
            statement+= "VALUES (%("+ ")s,%(".join(dictionary[0].keys())+")s)"

            cursor.executemany(statement,dictionary)
        insert_id= self.connection.insert_id()
        self.connection.commit()
        cursor.close()
        return insert_id
    def in_db(self,table,column,entry):
        """
        determines if entry of column in table extists
        """
        cursor=self.connection.cursor()
        ret=False
       
        cursor.execute('SELECT %s FROM %s where %s='%(column,table,column)+"%s",(entry,))

        if len(cursor.fetchall())>0:
            ret=True
        cursor.close()
        return ret
    def query_list(self,query,variables=None):
        """
         Queries the database, variables hold input variables to avoid sql-injection. Returns a list of results
         Example:
         result= db.query_list("SELECT * from table where id=%s",(1,)
         
         """
        cursor=self.connection.cursor()
        if variables!=None:
            if type(variables)!=tuple:
                cursor.execute(query,(variables,))
            else:
                   cursor.execute(query,variables)
        else:
            cursor.execute(query)
        ret =cursor.fetchall()
        cursor.close()
        return ret
    def query_dict(self,query,variables=None):
        """
        Queries the database, variables hold input variables to avoid sql-injection. Returns a list of results
         Example:
         result= db.query_dict("SELECT * from table where id=%s",(1,)
        """
        if self.driver=="pg":
            cursor=self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else: 
            cursor=MySQLdb.cursors.DictCursor(self.connection)
        if variables!=None:
            if type(variables)!=tuple:
                cursor.execute(query,(variables,))
            else:
                   cursor.execute(query,variables)
            
        else:
            cursor.execute(query)
        ret =cursor.fetchall()
        cursor.close()
        return ret
if __name__=='__main__':
    db=DB()
    
    print db.query_dict("SELECT * from email where mail_number=%s",(1,))
    print db.query_list('SELECT last_value from patients_pid_seq')[0][0]

