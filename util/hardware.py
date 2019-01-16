import subprocess
import os
import install
import menu
import time
import threading

# Memory Related
def freeMem():  # Free Memory on system
    ret = subprocess.Popen(
        ['free', '-m'], stdout=subprocess.PIPE).communicate()[0]
    i = 0
    while (ret[i:i+1] != "\n"):
        i += 1
    i += 1
    return int(ret[i:].split()[3])

def memInfo():
    while True:
        subprocess.call(['clear'])        
        print "\n\nChoose action to perform:\n\n" \
            "1. Serial\n2. Mem Test\n3. Previous Menu\n\n"
        uI = raw_input("Enter Choice:")
        subprocess.call(['clear'])    
        if uI == "1":
            ret = subprocess.Popen(['dmidecode','-t','17'],stdout=subprocess.PIPE).communicate()[0].split("\n")
            loc = []
            s = []
            p = []
            for l in ret:
                if l.find('Locator') > -1 and l.split()[0] != "Bank":
                    loc.append(l.split(":")[1])
                elif l.find('Serial') > -1:
                    s.append(l.split(':')[1])
                elif l.find('Part') > -1:
                    p.append(l.split(':')[1])
            print "Location\t\tPart Number\t\tSerial"
            print "******************************************************************"
            for i in range(0,len(loc)):
                print loc[i] + "\t\t" + p[i] + "\t" + s[i]
            uI = raw_input("\n\nPress enter to continue...")
        elif uI == "2":
            subprocess.call(['clear'])
            print "System being setup for test..."
            if not __debug__:
                install.memTools()
            tD = os.path.dirname(os.path.abspath(__file__))
            ret = subprocess.call(['cp',tD+'/tests.py',tD+'/deploy/'])
            # Copy hardware.py from this folder to the /deploy folder, easier to keep files in sync and less duplication of files
            tD +=  "/deploy/"
            tD2 = "/opt/mem-chk-tools/IDK/IDK_Client/"
            ret = subprocess.call(['cp','-r',tD+'.',tD2])
            subprocess.call(['clear'])
            if not __debug__:
                ret = subprocess.call(['python','-O',tD2 + "blister_m.py"])
            else:
                ret = subprocess.call(['python',tD2 + "blister_m.py"])           
        elif uI == "3":
            break


# CPU Related
def cores():  # Number of cores including hyper-threading
    ret = subprocess.Popen(['lscpu'], stdout=subprocess.PIPE).communicate()[0]
    return int(ret[ret.find('CPU('):].split()[1])

def cpuInfo():
    return subprocess.Popen(['lscpu'],stdout=subprocess.PIPE).communicate()[0]


# HD Related
class ioThread (threading.Thread):    

    def __init__(self,drive,testType):
        threading.Thread.__init__(self)
        self.drive = drive
        self.testType = testType

    def run(self):
        if self.testType == "4":
            ret = subprocess.Popen(['smartctl','-a','/dev/'+self.drive['loc']],stdout=subprocess.PIPE).communicate()[0]
            ret = ret.split('\n')
            secCnt = 0
            secInfo = []
            for r in ret:
                if r.find('Sector') > -1:
                    if secCnt > 0:
                        secInfo.append(r[-1:])
                    else:
                        secCnt = 1
            self.drive['ret'] = "/dev/" + self.drive['loc'] + "\n------------------------------------------\n"
            self.drive['ret'] += "Reallocated Sectors:\t\t\t" + secInfo[0] + "\nCurrent Pending Sectors:\t\t" + secInfo[1]
        elif self.testType == "2": #todo:probably change to dd based test.  I need to do some checking for drive empty before performing
            ret = subprocess.Popen(['dd','if=/dev/'+self.drive['loc'],'of=/dev/null','bs=4k','count=500k'],stderr=subprocess.PIPE).communicate()[1].split()[-2:]
            #ret = subprocess.Popen(['hdparm','-t','/dev/' + self.drive['loc']],stdout=subprocess.PIPE).communicate()[0].split("=")[1]
            self.drive['ret'] = "/dev/" + self.drive['loc'] + "\t\t" + " ".join(ret)

def hdInfo():  # todo:Need to do a lot of work here.  Serial, select certain drive, maybe list the drives and they choose or all option with Serial choice
    while True:
        subprocess.call(['clear'])
        print "Choose what action to perform on drives:\n\n" \
            "1. General Info\n" \
            "2. Drive Read Speed\n" \
            "3. SATA Connection Info\n" \
            "4. SMART Errors\n" \
            "5. Previous Menu\n\n"
        uI = raw_input("Enter Choice: ")
        subprocess.call(['clear'])
        if uI == "5":
            break
        
        drives = __lsblk()
        drive = []
        numThreads = len(threading.enumerate())
        if uI == "1":
            print "Drive\t\tType\t\tSerial"
            print "------------------------------------------------"
        elif uI == "2":
            print "Please wait a few moments for drives to complete testing.....\n"
        cnt = 0
        dLen = len(drives)
        for d in drives:
            if uI == "1":           
                # Trying faster way, see if problem with correct serial for drives
                # ret = subprocess.Popen(['smartctl','-i','/dev/' + d[0]],stdout=subprocess.PIPE).communicate()[0]
                # print "/dev/" + d[0] + ":\t" + ret[ret.find('Serial'):].split('\n')[0].split(':')[1]
                dType = "HDD"
                if d[2] == "0":
                    dType = "SSD"
                print "/dev/" + d[0] + "\t" + dType + "\t\t" + d[1]
            elif uI == "2":
                drive.append({'loc':d[0],'ret':""})
                tThread = ioThread(drive[len(drive)-1],"2")
                tThread.start()
                if cnt == dLen - 1:
                    tThread.join()
            elif uI == "3":            
                ret = subprocess.Popen(['smartctl','-i','/dev/'+d[0]],stdout=subprocess.PIPE).communicate()[0]
                ret = ret[ret.find('SATA'):]
                print "/dev/" + d[0] + ":\t" + ret.split(':')[1] + ret.split(':')[2].split('\n')[0]
            elif uI == "4":
                drive.append({'loc':d[0],'ret':""})
                tThread = ioThread(drive[len(drive)-1],"4")
                tThread.start()
            cnt += 1
            
        while len(threading.enumerate()) > numThreads:                       
            pass
        
        for d in drive:
            print d['ret']

        iput = raw_input("\n\nPress enter to continue...")

def __lsblk():
    retVal = []
    ret = subprocess.Popen(['lsblk', '-d', '-n', '-o', 'name,type,tran,serial,rota'],stdout=subprocess.PIPE).communicate()[0]
    ret = ret.split("\n")
    for i in range(0,len(ret)-1):
		if ret[i].find("disk") > -1 and ret[i].find("usb") < 0 and ret[i].split()[0].find("sd") > -1:
			retVal.append([ret[i].split()[0],ret[i].split()[3],ret[i].split()[4]]) # return drive letter,serial,rota(if SSD or HDD)
    return retVal


# System related
def sysInfo():
    subprocess.call(['clear'])
    ret = subprocess.Popen(['dmidecode','-t','1'],stdout=subprocess.PIPE).communicate()[0]
    print ret

def clearBMC():
    subprocess.call(['clear'])
    print "Listing contents..."
    print subprocess.Popen(['ipmitool','sel','list'],stdout=subprocess.PIPE).communicate()[0]
    while True:
        uI = raw_input("Are you sure you would like to clear contents(y/n)?")
        if uI == "y":
            subprocess.Popen(['ipmitool','sel','clear'],stdout=subprocess.PIPE).communicate()[0]
        elif uI == "n":
            break


# Sensor Related
def sensorInfo():
    while True:
        subprocess.call(['clear'])
        print "Choose sensor type:\n\n1. Temperature\n2. Fans\n3. All\n4. Previous Menu\n\n"
        uI = raw_input("Enter Choice: ")
        if uI == "1":
            __ipmitool("temperature")
        elif uI == "2":
            __ipmitool("fan")
        elif uI == "3":
            __ipmitool("")
        elif uI == "4":
            break

def __ipmitool(s):
    subprocess.call(['clear'])
    if s == "":
        print subprocess.Popen(['ipmitool','sdr'],stdout=subprocess.PIPE).communicate()[0]
    else:
        print subprocess.Popen(['ipmitool','sdr','type',s],stdout=subprocess.PIPE).communicate()[0]
    uI = raw_input("\n\nPress enter to continue...")


# Network Related
def netInfo():
    subprocess.call(['clear'])
    ret = subprocess.Popen(['ipmitool','lan','print'],stdout=subprocess.PIPE).communicate()[0].split("\n")
    bmc = ['','']
    for r in ret:
        if r.find("MAC") > -1:
            bmc[0] = r[-1:]
        elif r.find("IP") > -1:
            bmc[1] = r[-1:]
            break
    print "BMC Info\n----------------------------------\n"
    print "MAC:\t" + bmc[0]
    print "IP:\t" + bmc[1] + "\n"

    ret = subprocess.Popen(['ip','addr'],stdout=subprocess.PIPE).communicate()[0].split("\n")
    for i in range(0,len(ret)):
        nI = ['','','NA']
        if ret[i].find('link/ether') > -1:
            nI[0] = ret[i-1].split()[1].split(':')[0]
            nI[1] = ret[i].split()[1]
            if (i+1) < len(ret) and ret[i+1].find('inet') > -1 and ret[i+1].find('inet6') == -1:
                nI[2] = ret[i+1].split()[1].split('/')[0]
            print nI[0]+"\n----------------------------------\nMAC:\t"+nI[1]+"\nIPv4:\t"+nI[2]+"\n"    
    
    uI = raw_input("\nPress enter to continue...")
