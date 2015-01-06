import sys
if not "/usr/lib/python2.7/site-packages/ovirt" in sys.path:
    sys.path.append("/usr/lib/python2.7/site-packages/ovirt")
if not "/usr/lib/python2.7/site-packages/ovirt/license_util" in sys.path:
    sys.path.append("/usr/lib/python2.7/site-packages/ovirt/license_util")


from ovirt.node import plugins, valid, ui
from ovirt.node.utils import process
from ovirt.node.plugins import Changeset
import ovirtnode.ovirtfunctions as _functions
import os

class A(object):
    def b(self):
        def c():
            cmd = "engine-setup --config=/home/mujun/ovirt_config/20141230183208-setup.conf"
            out = ""
            current = 0
            try:
                import pdb
                pdb.set_trace()
                for line in process.pipe_async(cmd):
                    print line
                    if line == ""  or line == None :
                        break
                    line = ''.join(filter(lambda x: x, line.split('\033[0;31m')))
                    line = ''.join(filter(lambda x: x, line.split('\033[32m')))
                    line = ''.join(filter(lambda x: x, line.split('\033[0m')))
                    out += line
            #    if "icmp_req" in line:
            #        current += 100.0 / float(count)
                    current += 1
                    if current%7 == 0:
                        current =0
                        out = ""
                        
            #        self.widgets["ping.progress"].current(current)
                    with open('/root/abc','a+') as f:
                        f.writelines('Result :\n\n%s' %out)
                    self.widgets["ping.result"].text("Result:\n\n %s" % out)
                    if isRun():
                        _functions.system_closefds("rm -rf /etc/ovirt-engine/engine-setup.conf &> /dev/null")
                        _functions.system_closefds("engine-setup --gen-answer-file=/etc/ovirt-engine/engine-setup.conf &> /dev/null")
                        _functions.system_closefds("sed -i 1d /etc/ovirt-engine/engine-setup.conf &> /dev/null")
            #self.logger.debug(out)
            except:
                import traceback
                traceback.print_exc()
        c()

if __name__=='__main__':
    A().b()
