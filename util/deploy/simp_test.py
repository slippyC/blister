import tests
import subprocess

def main():
    mce = tests.Tests()
    dFail = mce.checkMCE()
    subprocess.call(['clear'])
    print "Current DIMM Failures...\n\nDIMM\t\tCount\n------------------------------------------------------------------------\n"
    if dFail != None:
        for i in range(0,len(dFail[0])):
            print dFail[0][i] + "\t\t" + str(dFail[1][i]) + "\n"
    else:
        print "No current DIMM Failures"

if __name__ == "__main__":
    main()