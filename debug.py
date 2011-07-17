
import config
import datetime
import os

def debug(message):
    """
    This function saves the message into a temporary file that can be read 
    by the header file in templates. It also saves the messages in a permanent      logfile
    """

    f=open(config.log_file,'a')
   
    f.write(str(datetime.datetime.now())+" "+message+"\n")
    f.close()

