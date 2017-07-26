import urllib.request
import smtplib
from datetime import datetime
import time
import os
import re
import sys

from email.mime.text import MIMEText
from email.header import Header


host_server = 'smtp.qq.com'
sender = 'xyz1219@qq.com'
receivers = ['624727007@qq.com']
receiver = ['398174029@qq.com']
subject = '中国银行英镑汇率'

password = os.environ['MAIL_PASSWORD']

smtp = smtplib.SMTP_SSL(host_server,465)


now_rate = ''
send_rate = []
reference_rate = ''



# 查找英镑汇率
def find_gbp():
    url = 'http://www.boc.cn/sourcedb/whpj'
    request = urllib.request.urlopen(url)
    datas = request.read()
    datas = datas.decode('utf-8')
    lines = datas.split()
    global now_rate
    i = 0
    for target in lines:
        i = i + 1
        if target == '<td>英镑</td>':
            gbp = lines[i+2]
            now_rate = re.sub('<td>','',gbp)
            now_rate = re.sub('</td>','',now_rate)
            break
    return now_rate

# 发送汇率邮件
def send_email():
    global send_rate
    send_rate.append(now_rate)
    message = MIMEText("中国银行英镑当前汇率为"+send_rate[-1], 'plain', 'utf-8')
    message['From'] = Header('xuyingzhe', 'utf-8')
    message['TO'] = Header('To whom it may concern', 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    # smtp.set_debuglevel(1)
    smtp.ehlo(host_server)
    smtp.login(sender, password)
    smtp.sendmail(sender, receivers, message.as_string())
    smtp.sendmail(sender, receiver, message.as_string())
    smtp.quit()


# 这次汇率与上次汇率的比较，返回'差距很大'或'无'
def compare_rate():
    if abs(float(now_rate)-float(reference_rate)) >= 3:
        return 'vary greatly'
    else:
        return 'none'

# 判断是否发邮件
def send_or_not():
    global reference_rate
    if compare_rate() == 'vary greatly':
        send_email()
        reference_rate = send_rate[-1]
        print('Already sent! reference_rate is now %s\n' %reference_rate)


def run():
    find_gbp()
    print(now_rate)
    print(reference_rate)
    # send_email()
    print(compare_rate())
    send_or_not()

def get_reference_rate_first():
    global reference_rate
    if len(sys.argv) == 2:
        reference_rate = sys.argv[1]
    else:
        reference_rate = find_gbp()

if __name__ == '__main__':
    # reference_rate = '885' find_gbp()
    get_reference_rate_first()
    print('The reference rate is ' + reference_rate)
    while True:
        run()
        print(time.strftime('%Y-%m-%d %H:%M:%S\n', time.localtime(time.time())))
        time.sleep(300)


