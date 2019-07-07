import urllib.request
from tkinter import *
def getfee(room_name):
    link = 'http://bems.dlut.edu.cn/MCWEB/RechargeNotice.aspx?category=38&name=%E8%A5%BF%E5%B1%B1'
    try:
        response = urllib.request.urlopen(link,timeout=3)
        result = response.read().decode('utf-8')
        index = result.find(room_name)
        result = result[index+26:index+40]
        ind2 = result.find('</td>')
        result = result[0:ind2]
        print(result)
        return result
    except Exception as e:
        print(e)
        return 0
'''
#if __name__ == 'main':
root = Tk()
fee = getfee('327')
if float(fee)<3:
    print('<3')
    text = Label(root,text="电费不足")
    root.mainloop()
else:
    exit(0)
'''
getfee('327')