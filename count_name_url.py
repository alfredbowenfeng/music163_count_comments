import requests
from bs4 import BeautifulSoup
import re,time
import os,json
import base64
from Crypto.Cipher import AES
from pprint import pprint

Default_Header = {
	'Referer':'http://music.163.com/',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.3029.110 Safari/537.36',
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate, sdch',
	'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,und;q=0.4,ja;q=0.2,ko;q=0.2,nb;q=0.2',
	'Upgrade-Insecure-Requests': '1',
	'Proxy-Connection': 'keep-alive',
}

BASE_URL = 'http://music.163.com'

_session = requests.session()
_session.headers.update(Default_Header)

def getPage(pageIndex):
	pageUrl = 'http://music.163.com/discover/playlist/?order=hot&cat=%E5%85%A8%E9%83%A8&limit=35&offset='+pageIndex
	content=_session.get(pageUrl).content
	# print(content)
	soup = BeautifulSoup(content, "html.parser")
	songList = soup.findAll('a',attrs = {'class':'tit f-thide s-fc0'})
	for i in songList:
		getPlayList(i['href'])

def getPlayList(playListId):
	playListUrl = BASE_URL + playListId
	soup = BeautifulSoup(_session.get(playListUrl).content, "html.parser")
	songList = soup.find('ul',attrs = {'class':'f-hide'})
	for i in songList.findAll('li'):
		startIndex = (i.find('a'))['href']
		songId = startIndex.split('=')[1]
		if (readEver(songId)==1):
			print(i.find('a').string + ',' + 'http://music.163.com/#/song?id=' + songId)
			time.sleep(1)

def get_params():
	first_param = "{rid:\"\", offset:\"0\", total:\"true\", limit:\"20\", csrf_token:\"\"}"
	second_param = "010001"
	third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
	forth_param = "0CoJUm6Qyw8W8jud"
	iv = "0102030405060708"
	first_key = forth_param
	second_key = 16 * 'F'
	h_encText = AES_encrypt(first_param, first_key, iv)
	h_encText = AES_encrypt(h_encText.decode(), second_key, iv)
	return h_encText

def get_encSecKey():
	encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
	return encSecKey

def AES_encrypt(text, key, iv):
	pad = 16 - len(text) % 16
	text = text + (pad * chr(pad))
	encryptor = AES.new(key, AES.MODE_CBC, iv)
	encrypt_text = encryptor.encrypt(text)
	encrypt_text = base64.b64encode(encrypt_text)
	return encrypt_text

def get_json(url, params, encSecKey):
	data = {
		 "params": params,
		 "encSecKey": encSecKey
	}
	headers = {
		'Cookie': 'appver=1.5.0.75771;',
		'Referer': 'http://music.163.com/'
	}
	response = requests.post(url, headers=headers, data=data)
	return response.content.decode()

def readEver(songId):
	url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_'+str(songId)+'/?csrf_token='
	songUrl = 'http://music.163.com/song?id=' + str(songId)
	params = get_params();
	encSecKey = get_encSecKey();
	json_text = get_json(url, params, encSecKey)
	json_dict = json.loads(json_text)
	if json_dict['total'] > 50000:
		print(str(json_dict['total']) + ',', end='')
		return 1
	else:
		return 0

if __name__=='__main__':
	for i in range(0,43):
		getPage(str(i*35))