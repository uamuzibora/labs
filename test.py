import numpy
import pylab
import ho.pisa as pisa                
x=numpy.arange(0,200)
y=x**2
pylab.plot(x,y)
pylab.savefig("test.png", dpi=460)
html="""<head>
<style type="text/css">
img{zoom:10%;}
</style>
</head>
""" 

def helloWorld():
  filename =  "ulf.pdf"               
  html+='Hello <strong>World</strong><br> <img src="test.png">'
  pdf = pisa.CreatePDF(html,file(filename, "wb"))
#  if not pdf.err:                     
 #   pisa.startViewer(filename)        

if __name__=="__main__":
  pisa.showLogging()                  
  helloWorld()
