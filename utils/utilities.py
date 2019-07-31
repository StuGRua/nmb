import re
import urllib.request as r
def parse_cited(txt):
    int1 = None
    re1='.*?'	# Non-greedy match on filler
    re2='(\\d+)'	# Integer Number 1
    rg = re.compile(re1+re2,re.IGNORECASE|re.DOTALL)
    m = rg.search(txt)
    if m:
        int1=m.group(1)
    return int1

    
def getfee(room_name):
    link = 'http://bems.dlut.edu.cn/MCWEB/RechargeNotice.aspx?category=38&name=%E8%A5%BF%E5%B1%B1'
    response = r.urlopen(link)
    print('response get')
    result = response.read().decode('utf-8')
    index = result.find(room_name)
    result = result[index+26:index+40]
    ind2 = result.find('</td>')
    result = result[0:ind2]
    print(result)
    return result

if __name__ == "__main__":
    getfee('327')
    pass
#getfee('327')