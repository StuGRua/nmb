import smtplib
from email.mime.text import MIMEText
def sender(msg_to,send_info):
    msg_from='2889205153@qq.com'                                 #发送方邮箱
    passwd='cnwpouojpobvdccg'                                   #填入发送方邮箱的授权码
    msg_to=msg_to                                  #收件人邮

    subject="确认邮件" 
    content='请点击此链接以确认激活账号'+send_info
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    try:
        s = smtplib.SMTP_SSL("smtp.qq.com",465)#邮件服务器及端口号
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
        print ("发送成功")
    except Exception as e:
        print (e)
    finally:
        s.quit()
if __name__ == "__main__":
    exit(0)
