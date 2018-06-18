# -*- coding: UTF-8 -*-
import xml.dom.minidom
import time
import json
import html2text
import urllib
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Read config from config.ini file.
site_json_path = config.get('main', 'site_json_path')
wordpress_rss_path = config.get('sync_from_rss', 'wordpress_rss_path')
update_flag = False

if not site_json_path or not wordpress_rss_path:
    print('Please read README.md and edit config.ini first!')
    exit(1)

h = html2text.HTML2Text()
site_json = open(site_json_path, encoding='utf-8').read()
open('site_data_json.bak', 'wb').write(site_json.encode())
site_json = json.loads(site_json)
current_post_id = site_json['next_post_id']
posts = site_json['post']
titles = []
for idx,title in enumerate(posts):
    titles.append(posts[idx]['title']) 

resource = urllib.request.urlopen(wordpress_rss_path).read()
DOMTree = xml.dom.minidom.parseString(resource)
items = DOMTree.documentElement.getElementsByTagName("item")
for idx,item in enumerate(items):
    if not item.getElementsByTagName('content:encoded')[0].childNodes:
        continue
    post_title = item.getElementsByTagName('title')[0].childNodes[0].data
    post_time = items[idx].getElementsByTagName('pubDate')[0].childNodes[0].data
    post_time = time.mktime(time.strptime(post_time, '%a, %d %b %Y %H:%M:%S +0000'))  # 对齐三位小数 :P
    post_body = h.handle(item.getElementsByTagName('content:encoded')[0].childNodes[0].data)
    if post_title in titles:
        continue
    post = {"post_id": current_post_id, "title": post_title, "date_published": post_time,
            "body": post_body}
    posts.insert(0, post)
    current_post_id += 1
    update_flag = True

site_json['next_post_id'] = current_post_id
open(site_json_path, 'wb').write(json.dumps(site_json, ensure_ascii=False, indent="\t").encode())
if update_flag:
    print("New post found, TRUE flag.")
else:
    print("No new posts.")