#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import datetime
import urllib2, urllib
import wsgiref.handlers
import re, os
import simplejson
import difflib
import sys 


from urllib2 import *
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail  
from time import gmtime, strftime

g_lunar_month_days = [
    0xF0EA4, 0xF1D4A, 0x52C94, 0xF0C96, 0xF1536, 0x42AAC, 0xF0AD4, 0xF16B2, 0x22EA4, 0xF0EA4,  # 1901-1910
    0x6364A, 0xF164A, 0xF1496, 0x52956, 0xF055A, 0xF0AD6, 0x216D2, 0xF1B52, 0x73B24, 0xF1D24,  # 1911-1920
    0xF1A4A, 0x5349A, 0xF14AC, 0xF056C, 0x42B6A, 0xF0DA8, 0xF1D52, 0x23D24, 0xF1D24, 0x61A4C,  # 1921-1930
    0xF0A56, 0xF14AE, 0x5256C, 0xF16B4, 0xF0DA8, 0x31D92, 0xF0E92, 0x72D26, 0xF1526, 0xF0A56,  # 1931-1940
    0x614B6, 0xF155A, 0xF0AD4, 0x436AA, 0xF1748, 0xF1692, 0x23526, 0xF152A, 0x72A5A, 0xF0A6C,  # 1941-1950
    0xF155A, 0x52B54, 0xF0B64, 0xF1B4A, 0x33A94, 0xF1A94, 0x8152A, 0xF152E, 0xF0AAC, 0x6156A,  # 1951-1960
    0xF15AA, 0xF0DA4, 0x41D4A, 0xF1D4A, 0xF0C94, 0x3192E, 0xF1536, 0x72AB4, 0xF0AD4, 0xF16D2,  # 1961-1970
    0x52EA4, 0xF16A4, 0xF164A, 0x42C96, 0xF1496, 0x82956, 0xF055A, 0xF0ADA, 0x616D2, 0xF1B52,  # 1971-1980
    0xF1B24, 0x43A4A, 0xF1A4A, 0xA349A, 0xF14AC, 0xF056C, 0x60B6A, 0xF0DAA, 0xF1D92, 0x53D24,  # 1981-1990
    0xF1D24, 0xF1A4C, 0x314AC, 0xF14AE, 0x829AC, 0xF06B4, 0xF0DAA, 0x52D92, 0xF0E92, 0xF0D26,  # 1991-2000
    0x42A56, 0xF0A56, 0xF14B6, 0x22AB4, 0xF0AD4, 0x736AA, 0xF1748, 0xF1692, 0x53526, 0xF152A,  # 2001-2010
    0xF0A5A, 0x4155A, 0xF156A, 0x92B54, 0xF0BA4, 0xF1B4A, 0x63A94, 0xF1A94, 0xF192A, 0x42A5C,  # 2011-2020
    0xF0AAC, 0xF156A, 0x22B64, 0xF0DA4, 0x61D52, 0xF0E4A, 0xF0C96, 0x5192E, 0xF1956, 0xF0AB4,  # 2021-2030
    0x315AC, 0xF16D2, 0xB2EA4, 0xF16A4, 0xF164A, 0x63496, 0xF1496, 0xF0956, 0x50AB6, 0xF0B5A,  # 2031-2040
    0xF16D4, 0x236A4, 0xF1B24, 0x73A4A, 0xF1A4A, 0xF14AA, 0x5295A, 0xF096C, 0xF0B6A, 0x31B54,  # 2041-2050
    0xF1D92, 0x83D24, 0xF1D24, 0xF1A4C, 0x614AC, 0xF14AE, 0xF09AC, 0x40DAA, 0xF0EAA, 0xF0E92,  # 2051-2060
    0x31D26, 0xF0D26, 0x72A56, 0xF0A56, 0xF14B6, 0x52AB4, 0xF0AD4, 0xF16CA, 0x42E94, 0xF1694,  # 2061-2070
    0x8352A, 0xF152A, 0xF0A5A, 0x6155A, 0xF156A, 0xF0B54, 0x4174A, 0xF1B4A, 0xF1A94, 0x3392A,  # 2071-2080
    0xF192C, 0x7329C, 0xF0AAC, 0xF156A, 0x52B64, 0xF0DA4, 0xF1D4A, 0x41C94, 0xF0C96, 0x8192E,  # 2081-2090
    0xF0956, 0xF0AB6, 0x615AC, 0xF16D4, 0xF0EA4, 0x42E4A, 0xF164A, 0xF1516, 0x22936,           # 2090-2099
]


Fo_holidays = [
               (1,1, "弥勒佛圣诞日"),
               (1,6, "定光佛圣诞日"),
               (2,8, "释迦牟尼佛出家日"),
               (2,15, "释迦牟尼佛涅盘日"),
               (2,19, "观世音菩萨圣诞日"),
               (2,21, "普贤菩萨圣诞日"),
               (3,16, "准提菩萨圣诞日"),
               (4,4, "文殊菩萨圣诞日"),
               (4,8, "释迦牟尼佛圣诞日"),
               (4,15, "佛吉祥日——释迦牟尼佛诞生、成道、涅盘三期同一庆"),
               (5,13, "伽蓝菩萨圣诞日"),
               (6,3, "护法韦驮尊天菩萨圣诞日"),
               (6,19, "观世音菩萨成道日"),
               (7,13, "大势至菩萨圣诞日"),
               (7,24, "龙树菩萨圣诞日"),
               (7,30, "地藏菩萨圣诞日"),
               (8,22, "燃灯佛圣诞日"),
               (9,19, "观世音菩萨出家纪念日"),
               (9,30, "药师琉璃光如来圣诞日"),
               (10,5, "达摩祖师圣诞日"),
               (11,17, "阿弥陀佛圣诞日"),
               (12,8, "释迦如来成道日"),
               (12,29, "华严菩萨圣诞日"),                                           
               ]

NumGB = ["","一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
         "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "廿",
         "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "卅",
         "卅一"]


import sys
from datetime import datetime, timedelta

START_YEAR, END_YEAR = 1901, 1900 + len(g_lunar_month_days)
LUNAR_START_DATE, SOLAR_START_DATE = (1901, 1, 1), datetime(1901,2,19) # 1901閿熸枻鎷烽敓鏂ゆ嫹閿熼摪绛规嫹涓�敓渚ョ櫢鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹涓�901/2/19
LUNAR_END_DATE, SOLAR_END_DATE = (2099, 12, 30), datetime(2100,2,18) # 2099閿熸枻鎷�2閿熸枻鎷�0閿熶茎鐧告嫹閿熸枻鎷烽敓鏂ゆ嫹閿熸枻鎷烽敓鏂ゆ嫹2100/2/8

def date_diff(tm):
    return (tm - SOLAR_START_DATE).days

def get_leap_month(lunar_year):
    return (g_lunar_month_days[lunar_year-START_YEAR] >> 16) & 0x0F

def lunar_month_days(lunar_year, lunar_month):
    return 29 + ((g_lunar_month_days[lunar_year-START_YEAR] >> lunar_month) & 0x01)

def lunar_year_days(year):
    days = 0
    months_day = g_lunar_month_days[year - START_YEAR] 
    for i in range(1, 13 if get_leap_month(year) == 0x0F else 14):
       day = 29 + ((months_day>>i)&0x01)
       days += day
    return days

def get_lunar_date(tm):
    if (tm < SOLAR_START_DATE or tm > SOLAR_END_DATE):
        raise Exception('out of range')

    span_days = date_diff(tm)

    year, month, day = START_YEAR, 1, 1
    tmp = lunar_year_days(year)
    while span_days >= tmp:
        span_days -= tmp
        year += 1
        tmp = lunar_year_days(year)

    leap = False
    tmp = lunar_month_days(year, month)
    while span_days >= tmp:
        span_days -= tmp
        month += 1
        tmp = lunar_month_days(year, month)
    leap_month = get_leap_month(year)
    if  month > leap_month:
        month -= 1
        if month == leap_month:
            leap = True
    day += span_days
    return (year, month, day)



def guestbook_key(guestbook_name=None):
    """Constructs a datastore key"""
    return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')


def verify_reCAPTCHA (recaptcha_challenge_field,
            recaptcha_response_field,
            private_key,
            remoteip):
    """
    Submits a reCAPTCHA request for verification. Returns RecaptchaResponse
    for the request

    recaptcha_challenge_field -- The value of recaptcha_challenge_field from the form
    recaptcha_response_field -- The value of recaptcha_response_field from the form
    private_key -- your reCAPTCHA private key
    remoteip -- the user's ip address
    """

    if not (recaptcha_response_field and recaptcha_challenge_field and
            len (recaptcha_response_field) and len (recaptcha_challenge_field)):
        return RecaptchaResponse (is_valid = False, error_code = 'incorrect-captcha-sol')
    

    def encode_if_necessary(s):
        if isinstance(s, unicode):
            return s.encode('utf-8')
        return s

    params = urllib.urlencode ({
            'privatekey': encode_if_necessary(private_key),
            'remoteip' :  encode_if_necessary(remoteip),
            'challenge':  encode_if_necessary(recaptcha_challenge_field),
            'response' :  encode_if_necessary(recaptcha_response_field),
            })

    request = urllib2.Request (
        url = "http://www.google.com/recaptcha/api/verify",
        data = params,
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "User-agent": "reCAPTCHA Python"
            }
        )
    
    httpresp = urllib2.urlopen (request)

    return_values = httpresp.read ().splitlines ();
    httpresp.close();
    return_code = return_values [0]

    if (return_code == "true"):
        return True
    else:
        return False
    

class Greeting(db.Model):
    """Data Model"""
    email = db.EmailProperty()
    add_date = db.DateTimeProperty(auto_now=True)

############################################################################################################
class MainPage(webapp.RequestHandler):
    def get(self):
        curtime = gmtime()
        (myyear, mymonth, myday) = get_lunar_date(datetime(curtime.tm_year, curtime.tm_mon, curtime.tm_mday)+timedelta(hours=curtime.tm_hour+8))        
        
        self.response.headers['content-type'] = 'text/html;charset=utf-8'
        self.response.out.write("""
        
        <html>
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="keywords" content="佛教节日,提醒,通知,订阅" />
        <meta name="description" content="佛教节日,提醒,通知,订阅" />
        <title>佛节日</title>
        </head>
        <body>
        <font size=10><strong>佛节日</strong></font>
        """)
        
        for x in Fo_holidays:
            if x[0] == mymonth and x[1] ==  myday:
                self.response.out.write("<p>今日 (" + NumGB[mymonth] +"月" + NumGB[myday] + "日)" + "是 " + x[2] + "，祈愿佛日增辉，正法久驻，国泰民安，众生解脱!</p>")

        self.response.out.write('<p>输入电子邮件地址, 我们会在每个佛节日通知您!</p>')
                
        self.response.out.write("""
            <form action="/submit" method="POST">
                <div><textarea name="email" rows="1" cols="60">fojieri@gmail.com</textarea></div>
                <script type="text/javascript" src="http://www.google.com/recaptcha/api/challenge?k=6LfRJs0SAAAAAO9xDCduTjW5I9B19I5sBd6GkJqD"></script>
                <noscript>
                  <iframe src="http://www.google.com/recaptcha/api/noscript?k=6LfRJs0SAAAAAO9xDCduTjW5I9B19I5sBd6GkJqD" height="300" width="500" frameborder="0"></iframe><br />
                  <textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
                  <input type='hidden' name='recaptcha_response_field' value='manual_challenge' />
                </noscript>
                <hr>
                <div><input type="submit" value="通知我"></div>
            </form>
            """)
        self.response.out.write('</body></html>')       

                
class AddUser(webapp.RequestHandler):
    def post(self):
        guestbook_name = 'zzxc'
        
        if(len(self.request.get("recaptcha_response_field"))==0):
            self.response.out.write("""
                            <script type="text/javascript">
                            alert("请输入验证码")
                            </script>""")
            self.response.out.write("""
                                <a href='/'>重来</a>""")
            return
        
        #self.response.out.write('<blockquote>%s</blockquote>' % verify_reCAPTCHA (self.request.get("recaptcha_challenge_field"), self.request.get("recaptcha_response_field"), '6LfRJs0SAAAAAFpQxZ_NfEB6rI9AriZb6eUNQHui', os.environ["REMOTE_ADDR"]))
        if( verify_reCAPTCHA (self.request.get("recaptcha_challenge_field"), self.request.get("recaptcha_response_field"), '6LfRJs0SAAAAAFpQxZ_NfEB6rI9AriZb6eUNQHui', os.environ["REMOTE_ADDR"])  ):
            
            greeting = Greeting(parent=guestbook_key(guestbook_name))
            greeting.email = (cgi.escape(self.request.get('email')).replace("\r\n", " ")).strip()
            
            #If the email is valid
            if re.match("\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*", greeting.email):

                greeting.put()
                self.response.out.write("""
                            <script type="text/javascript">
                            alert("订阅成功")
                            </script>""")
            else:
                self.response.out.write("""
                            <script type="text/javascript">
                            alert("请使用合法邮件地址")
                            </script>""")
        else:
                self.response.out.write("""
                    <script type="text/javascript">
                    alert("验证码输入错误")
                    </script>""")
                        
        self.response.out.write("""
                            <a href='/'>重来</a>""")



class SendEmail(webapp.RequestHandler):
    def get(self):
        curtime = gmtime()
        (myyear, mymonth, myday) = get_lunar_date(datetime(curtime.tm_year, curtime.tm_mon, curtime.tm_mday)+timedelta(hours=curtime.tm_hour+8))
        
        for x in Fo_holidays:
            if x[0] == mymonth and x[1] ==  myday:
                greetings = Greeting.all()
                for greeting in greetings:
                    user_address = cgi.escape(greeting.email)
                    (user_year, user_month, user_day) = get_lunar_date(greeting.add_date + timedelta(hours=8) )

                    if mail.is_email_valid(user_address) and (user_year < myyear or user_month < mymonth or user_day < myday):
                        self.response.out.write('<blockquote>sending...</blockquote>')
                        sender_address = 'noreply@literhub.com'
                        subject = "今天是佛节日!"
                        body = "今日 (" + NumGB[mymonth] +"月" + NumGB[myday] + "日)" + "是 " + x[2] + "，祈愿佛日增辉，正法久驻，国泰民安，众生解脱!"            
                        mail.send_mail(sender_address, user_address, subject, body)
                        greeting.put()
                        self.response.out.write('<blockquote>done!</blockquote>')


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/submit', AddUser),
                                      ('/sendingabc', SendEmail)
                                    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
            
