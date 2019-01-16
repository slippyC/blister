import subprocess
import install
import os

def main():
    CONST_PATH = '/opt/mem-chk-tools/IDK/IDK_Client/'
    subprocess.call(['clear'])
    print "Setting up tools and preparing to check for MCE Errors..."
    install.memTools()
    tD = os.path.dirname(os.path.abspath(__file__)) + '/.'
    subprocess.call(['cp','-r',tD,CONST_PATH])
    subprocess.call(['python','-O',CONST_PATH+'simp_test.py'])


if __name__ == "__main__":
    main()