'''
Created on 2012-11-29

@author: ZHUZE
'''


import hashlib
import os

def strmd5(str):
    return (hashlib.md5(str).hexdigest())

if __name__ == "__main__":
    print strmd5("")