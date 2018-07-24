# -*- coding: UTF-8 -*-
import xml.dom.minidom
import time
import json
import html2text
import configparser


def getPostsData(site_json_path, wordpress_xml_path):
    site_json = open(site_json_path, encoding='utf-8').read()
    open('site_data_json.bak', 'wb').write(site_json.encode())
    site_json = json.loads(site_json)
    DOMTree = xml.dom.minidom.parse(wordpress_xml_path)
    xml_items = DOMTree.documentElement.getElementsByTagName("item")
    return site_json, xml_items


def updatePosts(site_json, xml_items):
    h = html2text.HTML2Text()
    current_post_id = site_json['next_post_id']
    posts = site_json['post']
    for idx, item in enumerate(xml_items):
        if not item.getElementsByTagName('content:encoded')[0].childNodes:
            continue
        post_title = item.getElementsByTagName('title')[0].childNodes[0].data
        post_time = xml_items[idx].getElementsByTagName(
            'pubDate')[0].childNodes[0].data
        post_time = time.mktime(time.strptime(
            post_time, '%a, %d %b %Y %H:%M:%S +0000'))  # 对齐三位小数 :P
        post_body = h.handle(item.getElementsByTagName(
            'content:encoded')[0].childNodes[0].data)
        post = {"post_id": current_post_id, "title": post_title, "date_published": post_time,
                "body": post_body}
        posts.insert(0, post)
        current_post_id += 1
    open(site_json_path, 'wb').write(json.dumps(
        site_json, ensure_ascii=False, indent="\t").encode())
    return True


# main
# Read config
config = configparser.ConfigParser()
config.read('config.ini')
site_json_path = config.get('main', 'site_json_path')
wordpress_xml_path = config.get('main', 'wordpress_xml_path')

# check config
if not site_json_path or not wordpress_xml_path:
    print('Please read README.md and edit config.ini first!')
    exit(1)
site_json, xml_items = getPostsData(site_json_path,wordpress_xml_path)

try:
    updatePosts(site_json,xml_items)
except UnicodeError:
    print("XML Unicode Error, please check the encoding and syntax of yout xml file.")
else: 
    print('Good! Convert Finished, Please sign site and published, then refresh the page, you will see your WordPress post')
