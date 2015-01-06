import os
fn = os.path.dirname(__file__)
first_level=os.path.dirname(fn)
sec_level=os.path.dirname(first_level)
#third_level=os.path.dirname()
fn=os.path.abspath(os.path.join(sec_level,"20141230183208-setup.conf"))
print fn

