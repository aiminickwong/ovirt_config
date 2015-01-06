#!/usr/bin/python

from Crypto.Cipher import AES
import os
import binascii
#import md5
import re
import des
import hashlib
desKey = 'guofu123'

def encode(str,key):
    mode = AES.MODE_ECB
    decryptor = AES.new(key,mode)
    code = decryptor.encrypt(str)
    return code

def get_mac_address():
    import uuid
    node = uuid.getnode()
    #print node
    mac = uuid.UUID(int = node).hex[-12:]
    return mac

def decode(key):
    mode = AES.MODE_ECB
    
    decryptor = AES.new(key,mode)
    input = open('/tmp/data','rb')
    while True:
         ciphertext = input.read(32)
         #print 'aaaaaaaaaaaaaa'
         if not ciphertext:
	     break
         text = decryptor.decrypt(ciphertext)
         #print text
    input.close()
def strmd5(str):
    return (hashlib.md5(str).hexdigest())
	
def get_hardwareid(licensemac):
    #mac = get_mac_address()
    #print licensemac
    mac = None
    ismac = False
    licenseDe = des.strdesde(licensemac,desKey)
    licenseName = licenseDe[0:4]
    for line in os.popen("/bin/dmesg |grep eth"):
        #print line
        regex=r"[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}"
        mac =re.findall(regex,line)
        if mac:
            mac0 = mac[0].replace(':','')
            #print mac0
            mac0 = '%s::::' % mac0
            ciphertext = encode(mac0,'1234567890abcdef')
            c = binascii.hexlify(ciphertext)
            n=""
            m=""
            while c:
                f=c[0:2]
                n+= f+" "
                m+=binascii.unhexlify(f)
                c=c[2:]
            #print n
            #print licenseName
	    #print md5.strmd5(m)[0:4]
            if ( licenseName == strmd5(m)[0:4] ):
                ismac = True
                #print 'aaaaaaaaaaaaaaaaaaaaaaaaa'
		return ismac
        else:
            continue 
    return ismac


if __name__ == '__main__':
    for lien in os.popen("lspci |grep 'Ethernet controller'"):
        id = lien.split(' ')[0]
        print id
    mac = get_mac_address()
    mac = '%s::::' % mac
    print mac
    output = open('/tmp/data', 'wb') 
    #print decode(mac,'1234567890abcdef')
    ciphertext = encode(mac,'1234567890abcdef')
    #print '%s' % ciphertext
    #c = int(ciphertext,16)
    c = binascii.hexlify(ciphertext)
    #print binascii.unhexlify(ciphertext)
    n=""
    m=""
    while c:
    	f=c[0:2]
    	n+= f
        m+=binascii.unhexlify(f) 
    	c=c[2:]
    print n
    output.write(m)
    output.close()
    #decode('1234567890abcdef')
