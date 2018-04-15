import re
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import etree
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import time
import schedule

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=chrome_options)


def down_pic(full_pic_url,url):
    driver.get(full_pic_url)
    time.sleep(5)
    html = etree.HTML(driver.page_source)
#xpath Find script to list
    all_a_tags = html.xpath('//script[@type="text/javascript"]/text()')
    download_list = []
    rename = re.findll(r'https://www.instagram.com/(.*)',url)
    for a_tag in all_a_tags:
        if a_tag.strip().startswith('window'):#strip remove space startswith find 'window'start Str
            data = a_tag.split('= {')[1][:-1]
            js_data = json.loads('{'+data,encoding='utf-8')
            edges = js_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']#['edge_sidecar_to_children']['edges']
            try:
                if js_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']:
                    all_pic =[]
                    n = 0
                    for get_link in js_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']:
                        all_pic.append(get_link['node']['display_url'])

                    for down in all_pic:
                        urllib.request.urlretrieve(down,'/home/eunji/save/%s_%d.jpg'%(rename,n))
                        n += 1
            except:
                urllib.request.urlretrieve(edges['display_url'],'/home/eunji/save/%s.jpg'%rename)




def send_mail(url):
    ren = re.findll(r'https://www.instagram.com/(.*)',url)
    mail_host='smtp.qq.com'
    mail_user='13989538@qq.com'
    mail_pass='xmtwcdyfpfoocbcf'
    sender = '13989538@qq.com'
    # receivers = ['946897558@qq.com','li.han.lh2@roche.com','47331207@qq.com','93996948@qq.com']
    receivers = ['946897558@qq.com']
    msg = MIMEMultipart()
    msg['From'] = Header('%s'%ren,'utf-8')
    msg['To'] = Header('H','utf-8')
    msg['Subject'] = Header('%s send photo to u'%ren,'utf-8')

    fl_list = os.listdir('/home/%s/save'%ren)
    num_fl_list = len(fl_list)

#only 1 pic
    if num_fl_list > 1:
        for nfl,fl in zip(range(num_fl_list),fl_list):
            mail_pic ='''
            <p><img src="cid:%s"></p>
            '''%nfl
            msg.attach(MIMEText(mail_pic,'html','utf-8'))
            f = open('/home/%s/save/%s'%(ren,fl),'rb')
            msgImage = MIMEImage(f.read())
            f.close()
            msgImage.add_header('Content-ID','<%s>'%nfl)
            msg.attach(msgImage)
    else:
        mail_pic ='''
        <p><img src="cid:99"></p>
        '''
        msg.attach(MIMEText(mail_pic,'html','utf-8'))
        f = open('/home/%s/save/'%(ren,fl_list[0],'rb')
        msgImage = MIMEImage(f.read())
        f.close()
        msgImage.add_header('Content-ID','<99>')
        msg.attach(msgImage)

    try:
        s = smtplib.SMTP_SSL(mail_host, 465)
        s.login(mail_user,mail_pass)
        s.sendmail(sender, receivers, msg.as_string())
        print ("sucessful")
    except smtplib.SMTPException:
        print ("Error")


def down_and_send_task(url):
    # url = 'https://www.instagram.com/artist_eunji/'
    #url = ['url1','url2']
    #for i in url
    #driver.get(i)
    #正则匹配url中的名字，文件名也用这个名字
    driver.get(url)
    user_page = BeautifulSoup(driver.page_source,'lxml')
    time.sleep(10)
#first version:get newest post
    user_img = user_page.find('div',class_='_e3il2')
    get_update_post = user_img.parent
    pic_link = get_update_post.get('href')
    full_pic_url = 'https://www.instagram.com'+'%s'%pic_link

    time.sleep(5)

    if open('link.txt').read() != full_pic_url:
        open('link.txt','r+').write(full_pic_url)
        open('link.txt').close()
        down_pic(full_pic_url)
        send_mail()
        fl_list = os.listdir('/home/eunji/save')
        for del_file in fl_list:
            os.remove('/home/eunji/save/%s'%del_file)
    driver.close()

def main_task():
    all_name_file = open('name.txt')
    name_line = all_name_file.readline()
    name_list = []
    while name_line:
        name_list.append(name_line,strip('\n'))
        name_line = all_name_file.readline()
    all_name_file.close()
    for url in all_name_file:
        down_and_send_task(url)


schedule.every().day.at('09:30').do(down_and_send_task())
while True:
    schedule.run_pending()
    time.sleep(5)
