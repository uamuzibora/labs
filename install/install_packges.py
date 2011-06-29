

from setuptools.command import easy_install

def install_with_easyinstall(package):
    easy_install.main(["-U", package])


#Quick program to install all the python packages to the default location
packages=[
"mako",
"pisa",
"reportlab",
"html2pdf",
"pygresql",
"flup",
"psycopg2"]
for p in packages:
    install_with_easyinstall(p)
