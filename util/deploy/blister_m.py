import time
import tests
import subprocess

def main():
    subprocess.call(['clear'])
    initialTime = "DIMM stress test started " + \
    time.strftime("%A %b, %I:%M:%S%p", time.localtime())
    print initialTime
    test = tests.Tests()
    test.memTest()    
   
    while True:
        time.sleep(10)
        dFail = test.checkMCE()
        if dFail != None:
            subprocess.call(['clear'])
            print initialTime + "\n\nDIMM\t\tCount\n------------------------------------------------------------------------\n"
            for i in range(0,len(dFail[0])):
                print dFail[0][i] + "\t\t" + str(dFail[1][i]) + "\n"

if __name__ == "__main__":
    main()