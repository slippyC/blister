from subprocess import call, Popen, PIPE
import hardware
import os

__HD_INFO = {'serial': "Serial", 'SATA': "SATA", 'read': "Read",'error':'Error'}


def screen():
    while True:
        call(['clear'])
        print "Choose hardware:\n\n" \
                "1. Memory\n" \
                "2. HDD/SSD\n" \
                "3. CPU\n" \
                "4. Network\n" \
                "5. Sensors\n" \
                "6. System\n" \
                "7. Quit\n\n"
        uI = raw_input("Enter Choice: ")    
        if uI == "1":
            __mem()
        elif uI == "2":
            __hd()
        elif uI == "3":
            __cpu()
        elif uI == "4":
            hardware.netInfo()
        elif uI == "5":
            __sensor()
        elif uI == "6":
            __sysInfo()
        elif uI == "7":
            break


def __mem():
    hardware.memInfo()


def __hd(): #todo:Need to move choices to hardware.py to keep in implementation instead of menu
    hardware.hdInfo()

def __cpu():
    while True:
        call(['clear'])
        print "Choose what action to perform:\n\n1. CPU Information\n2. CPU Test(Not Implemented Yet)\n3. Previous Menu\n\n"
        uI = raw_input("Enter Choice: ")
        if uI == "1":
            print hardware.cpuInfo()
            __enter()
        elif uI == "3":
            break

    return

def __sysInfo():
    while True:
        call(['clear'])
        print "Choose what action to perform:\n\n1. Server Info\n2. BMC SEL\n3. Previous Menu\n\n"
        uI = raw_input("Enter Choice: ")
        if uI == "1":
            hardware.sysInfo()
            __enter()
        elif uI == "2":
            hardware.clearBMC()
            __enter()
        elif uI == "3":
            break

def __sensor():
    hardware.sensorInfo()


# Utiliy functions for this module
def __enter():
    raw_input("\n\nHit enter to continue...")