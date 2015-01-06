#! /usr/bin/python

'''
Created on 2013-1-6

@author: ZHUZE
'''
import sys
import time
import subprocess
import des
import md5
import get_hardwareid

desKey="guofu123"

def _addLicensetoDB(license,name,vmAmount,deadLine):
    stamp = int(time.time())
    sqlQuery = "INSERT INTO license(licensekey, name, vm_amount, deadline, time_stamp) VALUES('%s', '%s', '%s', '%s', %s)" % (license, name, vmAmount, deadLine,stamp)
    #sqlQuery = "UPDATE license(licensekey, name, vm_amount, deadline, time_stamp) VALUES('%s', '%s', %s, %s, %s)" % (license, name, vmAmount, deadLine,stamp)
    #execRemoteSqlCommand("postgres","localhost", "5432","engine", sqlQuery, True, "license import error")
    execRemoteSqlCommand("engine","localhost", "5432","engine", sqlQuery, True, "license import error")

def execRemoteSqlCommand(userName, dbHost, dbPort, dbName, sqlQuery, failOnError=False, errMsg="license import error"):
    cmd = "/usr/bin/psql -h %s -p %s -U %s -d %s -c \"%s\"" % (dbHost, dbPort, userName, dbName, sqlQuery)
    return execExternalCmd(cmd, failOnError, errMsg)

def execExternalCmd(command, failOnError=False, msg="license import error", maskList=[]):
    """
    Run External os command
    Receives maskList to allow passwords masking
    """
    p = subprocess.Popen(command, shell=True,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, close_fds=True)
    out, err = p.communicate()
    output = out + err
    if failOnError and p.returncode != 0:
        raise Exception(msg)
    return ("".join(output.splitlines(True)), p.returncode)

if __name__ == "__main__":
    args=sys.argv
    name=args[1]
    license=args[2]
    vmAmount=""
    deadLine=""
    try:
        licenseDe = des.strdesde(license,desKey)
        licenseName = licenseDe[0:4]
        mac = get_hardwareid.get_hardwareid(license)
        #if (licenseName == md5.strmd5(mac)[0:4]):
	if ( mac == True ):
            vmAmount = licenseDe[4:8]
            deadLine = licenseDe[8:16]
            # print "license key format success"
        else:
            print "invalid license"
    except:
        print "license key format error"
    _addLicensetoDB(license,name,vmAmount,deadLine)
    
