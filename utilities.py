import re
def parse_cited(txt):
    int1 = None
    re1='.*?'	# Non-greedy match on filler
    re2='(\\d+)'	# Integer Number 1
    rg = re.compile(re1+re2,re.IGNORECASE|re.DOTALL)
    m = rg.search(txt)
    if m:
        int1=m.group(1)
    return int1
if __name__ == "__main__":
    pass