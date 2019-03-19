# coding=utf-8
import itchat
from itchat.content import *
import datetime
import time
import json, requests  # , urllib.request
import urllib.request as urllib2
import urllib.parse
import gzip
from city import city

sendCont_list = []
sendTime_list = []
sendUser_list = []
Help_msg = """尊敬的%s先生/女士您好，
输入help或帮助或？可查询相关指令
输入 weather+城市名 可查询当前天气状况
输入 timing+时间+内容 可在指定时间向您发送指定内容
输入 datetime 可查询当前日期时间"""


@itchat.msg_register(TEXT)
def auto_reply(msg):
    user = itchat.search_friends(userName=msg['FromUserName'])
    if msg['ToUserName'] == 'filehelper':
        user['UserName'] = 'filehelper'
    if u'帮助' == msg['Text'] or u'help' == msg['Text'] or u'？' == msg['Text'] or '?' == msg['Text']:
        itchat.send(Help_msg % user['NickName'], toUserName=user['UserName'])
        print('done')

    if 'weather' in msg['Text']:
        content = detailedWeather(msg['Text'])
        itchat.send(content, toUserName=user['UserName'])
    elif 'datetime' in msg['Text']:
        itchat.send(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), toUserName=user['UserName'])
    elif 'timing' in msg['Text']:
        timingSend(msg['Text'], user['UserName'])
        itchat.send(u'设定完毕', toUserName=user['UserName'])

# this is based on "http://www.weather.com.cn/"
def getWeather(content):
    string_list = []
    if ' ' in content:
        string_list = content.split(' ')
    elif '+' in content:
        string_list = content.split('+')
    else:
        return u'请输入城市名'

    try:
        citycode = city[string_list[1]]
    except:
        return 'city not found!'
    if citycode:
        try:
            url = "http://www.weather.com.cn/data/cityinfo/" + citycode + ".html"  # 构造网址
            info = urllib2.urlopen(url).read()
            data = json.loads(info)
            weather_info = data['weatherinfo']
            str_temp = ('城市：%s\n天气：%s\n温度：%s至%s') % (weather_info['city'], weather_info['weather'], weather_info['temp1'], weather_info['temp2'])
            return str_temp
        except:
            return u'获得天气情况失败！'


def detailedWeather(content):
    string_list = []
    if ' ' in content:
        string_list = content.split(' ')
    elif '+' in content:
        string_list = content.split('+')
    else:
        return u'请输入规范的格式\n输入 weather+城市名 可查询当前天气状况'
    url = 'http://wthrcdn.etouch.cn/weather_mini?city=' + urllib.parse.quote(string_list[1])
    try:
        info_data = urllib.request.urlopen(url).read()
        info_data = gzip.decompress(info_data).decode('utf-8')
        info_dict = json.loads(info_data)
        if info_dict.get('desc') == 'OK':
            forecast = info_dict.get('data').get('forecast')
            # str_temp = '日期：'+forecast[0].get('date')+'\n'
            # str_temp = '城市：'+info_dict['data']['city']+'\n'
            # str_temp = '天气：'++
            # str_temp = '温度：'++
            # str_temp = '高温：'++'低温：'++
            # str_temp = ''
            weather_forecast_txt = '您好，您所在的城市<%s>\n' \
                                   '天气%s，' \
                                   '当前温度%s℃，' \
                                   '今天最高温度%s，' \
                                   '最低温度%s，' \
                                   '风级%s\n' \
                                   '温馨提示：%s' % \
                                   (
                                       info_dict.get('data').get('city'),
                                       forecast[0].get('type'),
                                       info_dict.get('data').get('wendu'),
                                       forecast[0].get('high'),
                                       forecast[0].get('low'),
                                       forecast[0].get('fengli').split('[')[2].split(']')[0],
                                       info_dict.get('data').get('ganmao')
                                   )
            return weather_forecast_txt
        else:
            return u'输入城市有误，请重新输入'
    except:
        return u'无法连接网络'



def timingSend(content, username):
    string_list = []
    if ' ' in content:
        string_list = content.split(' ')
    elif '+' in content:
        string_list = content.split('+')
    else:
        return
    if len(string_list) != 0:
        sendCont_list.append(string_list[2])
        sendTime_list.append(string_list[1])
        sendUser_list.append(username)


itchat.auto_login(hotReload=True)
itchat.run(blockThread=False)

while(1):
    nowTime = datetime.datetime.now().strftime('%H:%M')
    for i in range(len(sendCont_list)):
        if nowTime == sendTime_list[i]:
            itchat.send(sendCont_list[i], toUserName=sendUser_list[i])
            itchat.send(u'消息发送完毕', toUserName=sendUser_list[i])
            sendUser_list.pop(i)
            sendCont_list.pop(i)
            sendTime_list.pop(i)
