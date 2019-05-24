import hashlib


def md5(arg):
    md5_pwd = hashlib.md5(bytes('abd',encoding='utf-8'))
    md5_pwd.update(bytes(arg,encoding='utf-8'))
    return md5_pwd.hexdigest()
if __name__ == '__main__':
    print(md5('asdf234234234'))