
import os
import sys

path= "/".join(os.path.dirname(os.path.realpath(__file__)).split("/")[:-1])

os.environ['HOME'] =path
sys.path.append(path)
if sys.version_info>(2,6):
    from urlparse import parse_qs
else:
    from cgi import parse_qs
import wsgiref.util


from mako.template import Template
from mako.lookup import TemplateLookup
from config import * 
#from webob import *
from core import *
from Count import *
from Scatter import *
from Compare import *
import report

templates=TemplateLookup(path+'templates');
def debug(s):
    f=open("output/output.txt","a")
    f.write(str(s)+"\n")
    f.close()
def application(environ, start_response):
    """
    Main application that get's called
    """
    #environ['wsgilog.logger'].info('This information is logged.')
    # Exception will be logged and sent to the browser formatted as HTML.
    try:
        template,content=handle_url(environ)
    except:
        error_msg="There was an error with the input, check that you have inputed the right number of variables and that all needed extra information has been entered. Error msg: "+ str(sys.exc_info()[1])
        content={'variables':list_variables(),'date':first_patient(),'error':error_msg}
        template="index.html"
        

    status = '200 OK'
    if template !='file':
        """
        We want to show a normal webpage
        """
        template=templates.get_template(template) 
        response_headers = [('Content-Type', 'text/html')]
        start_response(status, response_headers)
        ret=[template.render(content=content).encode('utf-8')]
    else:
        """
        We want to offer a file for download, content=filename
        """
        body,title=content
        os.chdir(output_path)
        status = '200 OK'
        response_headers = [('Content-Type', 'application/pdf'),('Content-disposition','attachment; filename="'+title+'.pdf"')]

        start_response(status, response_headers)
        ret=body.getvalue()
    return ret

    #except:
     #   status = "500 Oops"
     #   response_headers = [("content-type","text/html")]
     #   start_response(status, response_headers, sys.exc_info())
     #   return ["<h1> An error happend</h1>"]
        
def handle_url(environ):
    """ 
    A function to handle the url, call the appropriate function and return the template and content
    """
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    
    request_body = environ['wsgi.input'].read(request_body_size)
    param = parse_qs(request_body);
    function=environ.get('PATH_INFO','/');
    if function=='':
        function=environ.get("SCRIPT_NAME","/")

    if function=='/count':
        template,content=count(param)
    elif function=='/scatter':
        template,content=scatter(param)
    elif function=='/compare':
        template,content=compare(param)
    elif function=='/pdf':
        template,content=pdf(param)
    elif function=='/generate_report':
        template,content=generate_report(param);
    elif function=='/vf':
        template,content=vf(param);
    elif function=='/generate_saved_report':
        template,content=generate_saved_report(param);
    else:
        template,content=index(param)
    return template,content
   
def index(param):
    """
    Displays the index site
    """
    content={'variables':list_variables(),'date':first_patient()}
    return ('index.html',content)
def count(param):
    """
    Display the counting site
    """
    start=param.get('start_year',[''])[0]+'-'+param.get('start_month',[''])[0]+'-'+param.get('start_day',[''])[0]
    end=param.get('end_year',[''])[0]+'-'+param.get('end_month',[''])[0]+'-'+param.get('end_day',[''])[0]

    group=param.get('group',[''])
    cutoff=param.get('cutoff',[''])
    calc=param.get('calc',[''])
    c=Count(group, cutoff=cutoff,calculation=calc,start=start,end=end);

    return ('count.html', c);
def vf(param):
    """
    Shows a page with Vestgard-Fransen statistics
    """
    source=Count(['patient_source_id','who_stage'])
    source2=Count(['patient_source_id'])
    cd4=Compare('cd4_count',['patient_source_id'],calcvariable='First')
    return ('vf.html',(source,source2,cd4))
def scatter(param):
    """
    Displaying the scatter plot
    """
    variables=param.get('variables',[''])
    calc=param.get('calc',[''])
    sc=Scatter(variables,calculation=calc)
    
    return ('scatter.html',sc);

def compare(param):
    """
    Displaying a comparisson of different variables 
    """
    group=param.get('group',[''])
    variable=param.get('variables',[''])[0]
    calc=param.get('calc',[''])
    calcvariable=param.get('calcvariable',[''])[0]
    cutoff=param.get('cutoff',[''])
    c=Compare(variable,group,calcvariable=calcvariable,calculation=calc,cutoff=cutoff)
    return ('compare.html',c);

def pdf(param):
    """
    Interface for generating pdf-reports
    """
    template="pdf.html"
    c={'variables':list_variables(),'date':first_patient()}

    c['reports']=report.get_reports();
    return(template,c);
def generate_report(param):
    """
    Either generates a report or saves the report.
    Get's hold of all the variables and passes them along to the generate_report function
    """
    number=int(param.get('number',[''])[0])
    items=[]
    title=param.get('title',[''])[0]
    for i in range(1,number+1):
        stat_type=param.get('type'+str(i),[''])[0]
        if stat_type=='count':
            chart_type=param.get('counttype'+str(i),[''])[0]
            start=param.get('countstart'+str(i)+'_year',[''])[0]+'-'+param.get('countstart'+str(i)+'_month',[''])[0]+'-'+param.get('countstart'+str(i)+'_day',[''])[0]
            end=param.get('countend'+str(i)+'_year',[''])[0]+'-'+param.get('countend'+str(i)+'_month',[''])[0]+'-'+param.get('countend'+str(i)+'_day',[''])[0]

            group=param.get('countgroup'+str(i),[''])
            cutoff=param.get('countcutoff'+str(i),[''])
            calc=param.get('countcalc'+str(i),[''])
            items.append({'type':'count','start':start,'end':end,'cutoff':cutoff,'calculation':calc,'group':group,'chart_type':chart_type})
        elif stat_type=='scatter':
            variables=param.get('scattervariables'+str(i),[''])
            calc=param.get('scattercalc'+str(i),[''])
            items.append({'type':'scatter','variables':variables,'calculation':calc})
        elif stat_type=='compare':
            group=param.get('comparegroup'+str(i),[''])
            variable=param.get('comparevariables'+str(i),[''])[0]
            calc=param.get('comparecalc'+str(i),[''])
            calcvariable=param.get('comparecalcvariable'+str(i),[''])[0]
            cutoff=param.get('comparecutoff'+str(i),[''])
            items.append({'type':'compare','variable':variable,'group':group,'calcvariable':calcvariable,'calculation':calc,'cutoff':cutoff})
    


    action=param.get('action',[''])[0]
    if action=='save':
        report.save_report(title,items)
        return pdf(param)
    elif action=='generate':
        content=report.generate_report(title,items)
        return ('file',(content,title))
 
def generate_saved_report(param):
    """
    Returns a file object whcih can be stored by the user
    """
    title=param.get('report',[''])[0]
    items=report.load_report(title)
    return ('file',(report.generate_report(title,items),title))




    


if __name__=='__main__':
    from flup.server.fcgi import WSGIServer
    WSGIServer(application,bindAddress = '/tmp/fcgi.sock').run()
    #cutoff=['30','100']
    #calc=['Mean']
    #c=Count(['age','cd4_count'],cutoff=cutoff,calculation=calc,start='2001-01-01',end='2007-01-01');
    #template=templates.get_template('count.html') 
    #print template.render(content=c)
    #print list_variables()
    #cutoff=['30','100']
    #calc=['Regression','Mean']
    #sc=Scatter(['cd4_count','cd4_count'],calculation=calc);
    #template=templates.get_template('scatter.html') 
    #print template.render(content=sc)
    #c=Compare('cd4_count',['sex','age'],cutoff=['40'],calcvariable='Mean')
    #template=templates.get_template('compare.html')
    #print template.render(content=c)
    
