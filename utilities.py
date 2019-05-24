invalids = [' ','\'','<','>','\"']
def stripit(string):
    s = str(string)
    for inv in invalids:
        s.replace(inv,'')
    return string
