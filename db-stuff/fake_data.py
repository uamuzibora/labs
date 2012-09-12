import pg
database='uamuzibora3'
import random
from numpy.random import *
host='localhost'
login='postgres'
password='postgres'
db=pg.DB(database,host,-1,None,None,login,password)

sex=['Male','Female']
letters=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
number_of_patients=500
number_of_results=10
test_ids=[21,2,3]
decimal=[21,2,3]
pid='18'
result_id=0
for N in range(number_of_patients):
    shuffle(sex)
    shuffle(letters)
    name=''.join(letters[0:6])
    upn=''.join([str(i) for i in randint(0,10,13)])
    year=1940+randint(1,65,1)[0]
    month=randint(1,13,1)[0]
    day=randint(1,28,1)[0]
    date_of_birth=str(year)+'-'+str(month)+'-'+str(day)
    
    patient={'pid':pid,'upn':upn,'surname':name,'forenames':name,'date_of_birth':date_of_birth,'year_of_birth':date_of_birth[0:4],'sex':sex[0],'location_id':randint(1,44,1)[0],'user_id':1,'created':date_of_birth+' 00:00:00','modified':date_of_birth+' 00:00:00'}
    year=2005+randint(0,5,1)[0]
    month=randint(1,13,1)[0]
    day=randint(1,28,1)[0]


    hiv_positive_clinic_start_date=str(year)+'-'+str(month)+'-'+str(day)
    med_info={'pid':pid,'patient_source_id':randint(1,10,1)[0],'hiv_positive_clinic_start_date': hiv_positive_clinic_start_date,'user_id':1,'created':date_of_birth+' 00:00:00','modified':date_of_birth+' 00:00:00','hiv_positive_who_stage':randint(1,5,1)[0]}

    db.insert('patients',patient)
    db.insert('medical_informations',med_info)
    for f in range(number_of_results):
        shuffle(test_ids)
        year=2000+randint(0,10,1)[0]
        month=randint(1,13,1)[0]
        day=randint(1,28,1)[0]
        test_performed=str(year)+'-'+str(month)+'-'+str(day)
        result={'id':result_id,'test_id':test_ids[0],'pid':pid,'test_performed':test_performed,'user_id':1,'created':test_performed+' 00:00:00','modified':test_performed+' 00:00:00'}

        if test_ids[0] in decimal:
            result_value={'result_id':result_id,'value_decimal':randint(0,300-f*15,1)[0],'user_id':1,'created':test_performed+' 00:00:00','modified':test_performed+' 00:00:00'}
        
        db.insert('results',result)
        db.insert('result_values',result_value)

        result_id+=1

    prefix=str(int(pid[0:-1])+1)
    rev_prefix=prefix[::-1]
    a=0;
    digits=[]
    for i in rev_prefix:
        if a%2==0:
            digits.append(2*int(i))
        else:
            digits.append(int(i))
        a+=1
    
    checksum = (10 - (sum(digits) % 10)) % 10;
    pid=prefix+str(checksum)
    print N
    






