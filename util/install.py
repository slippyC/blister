import subprocess
import os

def __output():
    return open(os.devnull,'w')

def memTools():
    ret = subprocess.call(['yum','install','mem-chk-tools','-y'],stdout=__output(),stderr=__output())

def centosEPEL():
    ret = subprocess.call(['wget','-O','/epl.rpm','https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm'],stdout=__output()).communicate()
    ret = subprocess.Popen(['yum','install','/epl.rpm','-y'],stdout=__output()).communicate()