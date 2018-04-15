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
                        urllib.request.urlretrieve(down,'/home/eunji/save/eunji_%d.jpg'%n)
                        n += 1
            except:
                urllib.request.urlretrieve(edges['display_url'],'/home/eunji/save/eunji.jpg')




def send_mail():
    mail_host='smtp.qq.com' 
    mail_user='13989538@qq.com'   
    mail_pass='xmtwcdyfpfoocbcf'
    sender = '13989538@qq.com'
    # receivers = ['946897558@qq.com','li.han.lh2@roche.com','47331207@qq.com','93996948@qq.com'] 
    receivers = ['946897558@qq.com']
    msg = MIMEMultipart()
    msg['From'] = Header('IG post','utf-8')
    msg['To'] = Header('H','utf-8')
    msg['Subject'] = Header('BOT send','utf-8')

    fl_list = os.listdir('/home/eunji/save')
    num_fl_list = len(fl_list)

#only 1 pic
    if num_fl_list > 1:
        for nfl,fl in zip(range(num_fl_list),fl_list):
            mail_pic ='''
            <p><img src="cid:%s"></p>
            '''%nfl
            msg.attach(MIMEText(mail_pic,'html','utf-8'))
            f = open('/home/eunji/save/%s'%fl,'rb')
            msgImage = MIMEImage(f.read())
            f.close()
            msgImage.add_header('Content-ID','<%s>'%nfl)
            msg.attach(msgImage)
    else:
        mail_pic ='''
        <p><img src="cid:99"></p>
        '''
        msg.attach(MIMEText(mail_pic,'html','utf-8'))
        f = open('/home/eunji/save/'%fl_list[0],'rb')
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


if open('link.txt').read() != full_pic_url:
    open('link.txt','r+').write(full_pic_url)
    open('link.txt').close()
    down_pic(full_pic_url)
    send_mail()
