import subprocess
import os
import sys

DEP_PAC = 'package.tar.gz'
DOWNLOAD_LINK = "https://github.com/slippyC/blister/raw/master/package.tar.gz"
CONST_PATH = '/opt/mem-chk-tools/IDK/IDK_Client/'

def main():
    subprocess.call(['clear'])
    print "Setting up tools and preparing to check for MCE Errors..."
    tS = cpuModel()
    if not (tS == 61 or tS == 71):
        print "\n\nYou must use a Juggernaut or some other Broadwell based server,\npreferably highest Mhz CPU and more cores for more DIMMS.\nThis just makes tracking down possible bad DIMMS quicker."
        sys.exit(0)
    memTools()
    deploy()
    print CONST_PATH + "blister_m.py"
    ret = subprocess.call(["python","-O",CONST_PATH+"blister_m.py"])
    
def downloader(link, fileName):
    ret = subprocess.call(['wget', '-O', fileName, link], stdout=__output(),stderr=__output())

def cpuModel():
    ret = subprocess.Popen(['lscpu'], stdout=subprocess.PIPE).communicate()[0]
    return int(ret[ret.find("Model:"):].split()[1])

def deploy():
    tD = os.path.dirname(os.path.abspath(__file__)) + '/'
    downloader(DOWNLOAD_LINK, DEP_PAC)
    ret = subprocess.call(["tar", "-zxvf", DEP_PAC], stdout=__output())
    ret = subprocess.call(['cp',"package/.",CONST_PATH, "-R"])

def __output():
    return open(os.devnull, 'w')

# Yes, there is new way to do this.  I have implemented checking errors with Tach/Skylake based procs as well.
# I'm just not going to do it here, nor unless I got paid to do it.  So please don't ask, unless ya are ready to
# pony up the coin.  :)
def memTools():
    ret = subprocess.call(
        ['yum', 'install', 'mem-chk-tools', '-y'], stdout=__output(), stderr=__output())


if __name__ == "__main__":
    main()
