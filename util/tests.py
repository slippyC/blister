import subprocess
import os
import sys
import time
if not __debug__:
    import broadwell


class Tests:
    __CONST_PATH_MCE = '/var/log/mcelog'
    __testRunning = False
    __DIMM_LOC = ['A0', 'A1', 'B0', 'B1', 'C0', 'C1', 'D0',
                  'D1', 'E0', 'E1', 'F0', 'F1', 'G0', 'G1',
                  'H0', 'H1','I0','I1','J0','J1','K0','K1',
                  'L0','L1','M0','M1']
    __CONST_PATH = '/opt/mem-chk-tools/IDK/'
    __LOG_PATH = '/tmp/m_test/'

    def __init__(self):
        self.__mceLen = 0
        self.__dimm_errors = []
        self.__dimm_error_count = []
        self.__bw = None


    def memTest(self):  # todo:Automatic resizing of memtester memory allocation instead of by core.  Will take a little longer, but more accurate
        if Tests.__testRunning:
            print "Only one test allowed to run at a time..."
            return        
        
        numCores = self.__getCores()
        mem = self.__freeMem()
        memPerCore = (mem - self.__minMem())/numCores  # May need to do max cores minus 1 then see what's left to be taken up in memory
        Tests.__testRunning = True
        for i in range(0,numCores):
            self.__invokeMemtester(memPerCore)

    def __minMem(self):
        block_size = [500,125,25]
        initialFree = self.__freeMem()
        memLeft = initialFree
        num_cores = self.__getCores() / 2 # Half the amount of cores so have some left to find Max usable memory
        min_start = 1500 # May need to change this as more server types become available(ex:Tachyon/Barkley16)
        iniMem = (memLeft - min_start) / num_cores
        
        for b in block_size:
            logDir = subprocess.call(['mkdir','-p',Tests.__LOG_PATH])
            c = 0
            for i in range(0,num_cores):
                self.__invokeMemtester(iniMem,i,False)
                c += 1

            for i in range(0,c-1):
                path = Tests.__LOG_PATH+"t"+str(i)+".log"
                while True:
                    with open(path,"r") as f:
                        if f.read().find("locked") > -1:
                            break
            memLeft = self.__freeMem()
            while True:
                ret = self.__invokeMemtester(b,c)
                f_mem = self.__freeMem()
                if memLeft > f_mem:
                    memLeft = f_mem
                else:
                    self.stopMemTest()
                    time.sleep(5)
                    iniMem = (initialFree - memLeft) / num_cores
                    break
                c += 1
            nukeLogDir = subprocess.call(['rm','-f',Tests.__LOG_PATH,'-R'])
        
        return memLeft

    def __invokeMemtester(self,amtMem,procNum=None,waitLock=True):
        if procNum == None:
            ret  = subprocess.Popen(['memtester', str(amtMem)],stdout=open(os.devnull,'w')).pid
        else:
            path = Tests.__LOG_PATH+"t"+str(procNum)+".log"
            ret  = subprocess.Popen(['memtester', str(amtMem)],stdout=open(path,"w")).pid
            if waitLock:
                while True:
                    if (os.path.isfile(path)):
                        with open(path,'r') as f:
                            if f.read().find("locked") > -1:
                                break

    def __getCores(self):
        ret = subprocess.Popen(['lscpu'], stdout=subprocess.PIPE).communicate()[0]
        return int(ret[ret.find('CPU('):].split()[1])

    def __freeMem(self):
        ret = subprocess.Popen(['free', '-m'], stdout=subprocess.PIPE).communicate()[0]
        i = 0
        while (ret[i:i+1] != "\n"):
            i += 1
        i += 1
        return int(ret[i:].split()[3])

    def getDimmErrors(self):
        return self.__dimm_errors

    def __iniMemChk(self):  # Sets up IDK interface for finding location of DIMMS
        if self.__idkRunning() == False:
            tStr = Tests.__CONST_PATH + 'idk_core/'            
            os.chdir(tStr)
            ret = subprocess.Popen(['./idk_core', '/listen', '/no_pat'],stdout=open(os.devnull,'w')).pid
            if self.__bw == None:
                self.__bw = broadwell.connect('127.0.0.1')            

    def __idkRunning(self):
        ret = subprocess.Popen(['ps','ax'],stdout=subprocess.PIPE).communicate()[0].split("\n")
        for i in range(0,len(ret)):
            if ret[i].find("idk_core") > -1 and ret[i].find("defunct") < 0:
                return True
        return False

    def getDimm(self, addr):  # Get DIMM location by address
        self.__iniMemChk()        
        ret = self.__bw.AT_forward_translate(int('0x'+addr,16))
        return Tests.__DIMM_LOC[int(str(ret['socket'])+str(ret['imc'])+str(ret['channel'])+str(ret['dimm']), 2)]

    def checkMCE(self):# Need to implement for thermal,overflow,etc.  Right now could give false positive, memory only
        self.__iniMemChk()
        if os.path.getsize(Tests.__CONST_PATH_MCE) > self.__mceLen:  # todo:Find way to read partial file, maybe by byte instead of parsing whole file again for new errors            
            self.__mceLen = os.path.getsize(Tests.__CONST_PATH_MCE)
            with open(Tests.__CONST_PATH_MCE, 'r') as f:            
                for l in f:   #f is file, l reads lines from file(weird way to do it, would think l in f.readlines())
                    if l.find('MISC') > -1:                        
                        if l.find('ADDR') > -1:                            
                            tL = l.split()
                            dimm = self.getDimm(tL[len(tL) - 1])
                            if dimm not in self.__dimm_errors:
                                self.__dimm_errors.append(dimm)
                                self.__dimm_error_count.append(1)
                            else:
                                i = self.__dimm_errors.index(dimm)
                                self.__dimm_error_count[i] += 1
                    if l.find("Transaction:") > -1:
                        if l.find("Memory") < 0:
                            raise ValueError('REPORT THIS ERROR IMMEDIATELY TO CHRIS!!!\nThis is an overflow, thermal, or other type error...')
            return [self.__dimm_errors,self.__dimm_error_count]
        return None

    def stopMemTest(self):
        self.__bw = None
        ret = subprocess.call(['pkill','-9','memtester'])
        ret = subprocess.call(['pkill','-9','idk_core'])
        self.__testRunning = False

    def __del__(self):
        self.__bw = None
        ret = subprocess.call(['pkill','-9','memtester'])
        ret = subprocess.call(['pkill','-9','idk_core'])
        self.__testRunning = False

