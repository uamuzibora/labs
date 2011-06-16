from core import *
import ho.pisa as pisa
from Count import *
from Scatter import  *
from Compare import *
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import pylab
import pickle
picture_format='.png'
import logging
class PisaNullHandler(logging.Handler):
    def emit(self, record):
        pass
logging.getLogger("ho.pisa").addHandler(PisaNullHandler())
from config import *
import StringIO
colors=['b','g','r','c','m','y','k']
font='serif'
html_template_header="""
<html>
<body>
"""
html_template_footer="""
</body>
</html>
"""

def clean(n_count,n_scatter):
    """
    Removes saved images
    """
    for i in range(n_count):
        os.remove('count'+str(i)+picture_format)
    for i in range(n_scatter):
        os.remove('scatter'+str(i)+picture_format)

def get_reports():
    """
    Finds and returns a list of all saved report templates
    """
    files=sorted(os.listdir(path+'reports'))
    
    reports=[]
    for f in files:
        filename=os.path.splitext(f)
        if filename[1]=='.rep':
            reports.append(filename[0])
    return reports
        
    
def save_report(title,items):
    """
    Saves a report template as pickle file
    """
    ret=False
    if not os.path.exists(title+'.rep'):
        os.chdir(path+'reports')
        f=open(title+'.rep','w')

        pickle.dump(items,f)
        ret= True
        f.close()
    return ret

def load_report(title):
    """
    Reads a saved report template and returns a dictionary of items
    """
    os.chdir(path+'reports')
    items=False
    if os.path.exists(title+'.rep'):
        f=open(title+'.rep','r')
        items=pickle.load(f)
        f.close()
    return items

def generate_report(title,items):
    """
    Takes a title and a dictionary of items and generates a report
    Returns a stringIO file 
    """
    os.chdir(output_path)
    items_classes=[]
    n_count=0
    n_scatter=0
    html=html_template_header+'<h1>'+title+'</h1><table>'
    i=0
    # Goes trough and generates each of the items
    for item in items:
        # We want to items on each row
        if i%2==0:
            html+='<tr>'
        html+="<td>"
        if item['type']=='count':
            stat=Count(item['group'],cutoff=item['cutoff'],calculation=item['calculation'],start=item['start'],end=item['end']);
            if item['chart_type']=='table':
                html+=count_table(stat)
            else:
                html+=count_chart(stat,item['chart_type'],n_count)
                #We count the number of images we make so we can delete them later
                n_count+=1
                
        if item['type']=='scatter':
            stat=Scatter(item['variables'],calculation=item['calculation'])
            html+=scatter_plot(stat,n_scatter)
            n_scatter+=1
        if item['type']=='compare':
            stat=Compare(item['variable'],item['group'],calcvariable=item['calcvariable'],calculation=item['calculation'],cutoff=item['cutoff'])
            html+=compare_table(stat)
                
        html+='</td>'
        if i%2==1:
            html+='</tr>'
        
        i+=1

    html+='</tr></table>'+html_template_footer
    filename=title+".pdf"
    f=StringIO.StringIO()
    #Create the PDF
    pdf=pisa.CreatePDF(html,f, show_error_as_pdf=True)
    #clean(n_count,n_scatter)
    return f

def count_table(data):
    """
    Returns the html-code for a count-table
    """
    html="<table><tr><td></td>"
    i=0
    xaxis=data.xaxis()
    data=data.numbers()	
    for k in sorted(data.keys()):
            html+='<td>'+str(k)+'</td>'
    html+='</tr>'
    while i<len(xaxis):
	html+='<tr><td>'+str(xaxis[i])+'</td>'
	for k in sorted(data.keys()):
	    html+='<td>'+str(data[k][i])+'</td>'
        html+='</tr>'
	i+=1

    html+='</table>'
    return html

def scatter_plot(scatter,numb):
    """
    Makes a scatter plot and returns the html code for it
    """
    plt.figure()
    x,y,cor=scatter.numbers()
    xlabel,ylabel=scatter.labels()
    plt.scatter(x,y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    decoratePlot(legsize=0)
    plt.savefig('scatter'+str(numb)+picture_format,dpi=20000)
    
    html='<img src="scatter'+str(numb)+picture_format+'" style="zoom:60%">'
    html+='<br /><p>Correlation is '+str(cor)+'</p>'
    return html

def count_chart(count,chart_type,numb):
    """
    Makes a count chart(bar,pie or timeline) and returns the html code for it
    """
    pylab.figure()
    data=count.numbers()
    number_of_series=len(data)
    xlabels=count.xaxis()

    html=''
    
    if chart_type=='bar_chart':
        x=numpy.arange(len(xlabels))
        bar_width=0.9/float(number_of_series)
        i=0
        #Set up the x-axis
        for d in data:
            plt.bar(x+i*bar_width,data[d],color=colors[i],width=bar_width,label=d)
            i+=1
        plt.xticks(x+0.5, xlabels)
        plt.legend()
      
        decoratePlot()
      
        plt.savefig('count'+str(numb)+picture_format,dpi=1000)
        html='<img src="count'+str(numb)+picture_format+'" style="zoom:60%">'
    if chart_type=='pie_chart':
        plt.figure(figsize=(9,9))
        piechart=numpy.zeros((len(data[data.keys()[0]])))
        for serie in sorted(data.keys()):
            piechart+=numpy.array(data[serie])
        plt.pie(piechart)
        tot=numpy.sum(piechart)
        # Set up labels with the percentage written
        for i in range(len(xlabels)):

            xlabels[i]+=' '+str(100*piechart[i]/float(tot))+'%'
        plt.legend(xlabels)
        decoratePlot()
        plt.savefig('count'+str(numb)+picture_format)
        html='<img src="count'+str(numb)+picture_format+'" style="zoom:60%">'
    elif chart_type=='timeline':
        data=count.timeline_numbers()
        xaxis=count.timeline_xaxis()
        dates=[]
        
        for x in xaxis:
#            print x
            dates.append(datetime.datetime(*x[0:6]))
            #dates.append(x)
        #Set up matplotlib to handle dates
        years    = mdates.YearLocator()   # every year
        months   = mdates.MonthLocator()  # every month
        yearsFmt = mdates.DateFormatter('%Y')

        fig = plt.figure()
        ax = fig.add_subplot(111)
        for d in data:
            ax.plot(dates,data[d],label=d)


        # format the ticks
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(yearsFmt)
        ax.xaxis.set_minor_locator(months)

        datemin = datetime.date(dates[0].year, 1, 1)
        datemax = datetime.date(dates[-1].year+1, 1, 1)
        ax.set_xlim(datemin, datemax)
        plt.legend()
        decoratePlot()
        fig.autofmt_xdate()

        plt.savefig('count'+str(numb)+picture_format,dpi=2000)
        html='<img src="count'+str(numb)+picture_format+'" style="zoom:60%">'
    return html

def compare_table(compare):
    """
    Returns html-code for a compare-table
    """
    mean,p_value,N=compare.numbers()
    subgroups=compare.labels()
    html="<table><tr><td></td><td>Mean</td><td>P-value</td><td>N</td>"
    
    for i in range(len(mean)):
        html+="<tr><td>"+subgroups[i]+"</td><td>"+str(mean[i])+"</td><td>"+str(p_value[i])+"</td><td>"+str(N[i])+"</td></tr>"
        
    html+="</table>"
    return html
def decoratePlot(legsize=16,xsize=16,ysize=16):
    """
    Decorating the plots, text-sizes
    """
    if legsize!=0:
        leg=pylab.gca().get_legend()
    
        txt=leg.get_texts()
        pylab.setp(txt, fontsize=legsize,family=font)
    xticklabels = pylab.getp(pylab.gca(), 'xticklabels')
    yticklabels = pylab.getp(pylab.gca(), 'yticklabels')
    pylab.setp(yticklabels, fontsize=ysize,family=font)
    pylab.setp(xticklabels, fontsize=xsize,family=font)


if __name__=="__main__":

    pisa.showLogging()
    items=[{'type':'count','chart_type':'table','group':['sex','age'],'cutoff':[30],'calculation':['First'],'end': '2010-06-07','start': '2000-01-16'}]
    items.append({'type':'count','chart_type':'bar_chart','group':['sex','age'],'cutoff':[30],'calculation':['First'],'end': '2010-06-07','start': '2000-01-16'})
    items.append({'type':'count','chart_type':'pie_chart','group':['sex'],'cutoff':[],'calculation':['First'],'end': '2010-06-07','start': '2000-01-16'})
    items.append({'type':'scatter','cutoff':[],'variables':['cd4_count','height'],'calculation':['First','Mean']})
    items.append({'cutoff': ['50'], 'calcvariable': 'Mean', 'group': ['sex', 'age'], 'calculation': ['Mean', 'First'], 'variable': 'cd4_count', 'type': 'compare'})
    #items=[{'type':'scatter','cutoff':[],'variables':['cd4_count','height'],'calculation':['First','Mean']}]
    #items=[{'cutoff': [''], 'end': '2010-06-09', 'calculation': ['First'], 'start': '2000-01-16', 'chart_type': '', 'group': ['sex'], 'type': 'count'}]

#    print generate_report('test',items)
    #print items
    #print save_report('test',items)
    #print get_reports()
    print generate_report("VF",load_report('VF-report'))
