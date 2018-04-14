import re
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from lxml import etree
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context
import time
import schedule

driver = webdriver.Chrome()
url = 'https://www.instagram.com/artist_eunji/'
driver.get(url)
user_page = BeautifulSoup(driver.page_source,'lxml')
time.sleep(10)
#first version:get newest post
user_img = user_page.find('div',class_='_e3il2')
get_update_post = user_img.parent
pic_link = get_update_post.get('href')
full_pic_url = 'https://www.instagram.com'+'%s'%pic_link

time.sleep(5)
#下载最新post的图片
def down_pic(full_pic_url):
    driver.get(full_pic_url)
    time.sleep(5)
    html = etree.HTML(driver.page_source)
#xpath Find script to list
    all_a_tags = html.xpath('//script[@type="text/javascript"]/text()')
    download_list = []
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
                        urllib.request.urlretrieve(down,'c:/py/instagram/save/eunji_%d.jpg'%n)
                        n += 1
            except:
                urllib.request.urlretrieve(edges['display_url'],'c:/py/instagram/save/eunji.jpg')


#如果得到的更新post链接和储存的不一致，就写入

def send_mail():
    mail_host='smtp.qq.com'  #设置服务器
    mail_user='13989538@qq.com'    #用户名
    mail_pass='xmtwcdyfpfoocbcf'
    sender = '13989538@qq.com'
    # receivers = ['946897558@qq.com','li.han.lh2@roche.com','47331207@qq.com','93996948@qq.com'] 
    receivers = ['946897558@qq.com']
    msg = MIMEMultipart()
    msg['From'] = Header('IG推送','utf-8')
    msg['To'] = Header('H','utf-8')
    msg['Subject'] = Header('BOT给你发照片啦','utf-8')
#查看目录下有几个文件，就发送几个附件
    fl_list = os.listdir('c:/py/instagram/save')
    num_fl_list = len(fl_list)

#only 1 pic
    if num_fl_list > 1:
        for nfl,fl in zip(range(num_fl_list),fl_list):
            mail_pic ='''
            <p><img src="cid:%s"></p>
            '''%nfl
            msg.attach(MIMEText(mail_pic,'html','utf-8'))
            f = open('c:/py/instagram/save/%s'%fl,'rb')
            msgImage = MIMEImage(f.read())
            f.close()
            msgImage.add_header('Content-ID','<%s>'%nfl)
            msg.attach(msgImage)
    else:
        mail_pic ='''
        <p><img src="cid:99"></p>
        '''
        msg.attach(MIMEText(mail_pic,'html','utf-8'))
        f = open('c:/py/instagram/save/%s'%fl_list[0],'rb')
        msgImage = MIMEImage(f.read())
        f.close()
        msgImage.add_header('Content-ID','<99>')
        msg.attach(msgImage)

    try:
        s = smtplib.SMTP_SSL(mail_host, 465)
        s.login(mail_user,mail_pass)
        s.sendmail(sender, receivers, msg.as_string())
        print ("邮件发送成功")
    except smtplib.SMTPException:
        print ("Error: 无法发送邮件")


if open('link.txt').read() != full_pic_url:
    open('link.txt','r+').write(full_pic_url)
    open('link.txt').close()
    down_pic(full_pic_url)
    send_mail()
