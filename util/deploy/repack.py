import tests

def main():
    mce = tests.Tests()
    ret = mce.checkMCE()
    print "Current DIMM failues are:\n" + " ".join(ret)



if __name__ == "__main__":
    main()