# -*- coding: UTF-8 -*-
import xml.dom.minidom
import time
import json
import html2text
import urllib
import configparser

def getPostsData(site_json_path, wordpress_rss_path):
    site_json = open(site_json_path, encoding='utf-8').read()
    open('site_data_json.bak', 'wb').write(site_json.encode())
    site_json = json.loads(site_json)
    resource = urllib.request.urlopen(wordpress_rss_path).read()
    DOMTree = xml.dom.minidom.parseString(resource)
    xml_items = DOMTree.documentElement.getElementsByTagName("item")
    return site_json, xml_items

def generateExistIndex(site_json):
    titles = []
    index_body = "欢迎访问落絮飞雁的零网博客！\n\n因为ZeroBlog不支持目录结构:sweat:，所以目录列在下面。\n\n"
    posts = site_json['post']
    for idx,title in enumerate(posts):
        titles.append(posts[idx]['title'])
        # *   [文章目录](?Post:510)\n\n*
        index_body = index_body + "*   [" + posts[idx]["title"] + "](?Post:" + str(posts[idx]["post_id"]) + ")\n\n"
    return titles, index_body

def updateNewPosts(titles, index_body, site_json, xml_items):
    update_flag = False
    h = html2text.HTML2Text()
    current_post_id = site_json['next_post_id']
    posts = site_json['post']
    for idx,item in enumerate(xml_items):
        if not item.getElementsByTagName('content:encoded')[0].childNodes:
            continue
        post_title = item.getElementsByTagName('title')[0].childNodes[0].data
        post_time = xml_items[idx].getElementsByTagName('pubDate')[0].childNodes[0].data
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
        #posts[posts.index'']["body"] = index_body
        #posts[510]["date_published"] = time.mktime(time.strptime(time.localtime, '%a, %d %b %Y %H:%M:%S +0000'))
    open(site_json_path, 'wb').write(json.dumps(site_json, ensure_ascii=False, indent="\t").encode())
    return update_flag


# main
# Read config from config.ini file.
config = configparser.ConfigParser()
config.read('config.ini')
site_json_path = config.get('main', 'site_json_path')
wordpress_rss_path = config.get('sync_from_rss', 'wordpress_rss_path')

if not site_json_path or not wordpress_rss_path:
    print('Please read README.md and edit config.ini first!')
    exit(1)

site_json, xml_items = getPostsData(site_json_path,wordpress_rss_path)
titles, index_body = generateExistIndex(site_json)
update_flag = updateNewPosts(titles, index_body, site_json, xml_items)
if update_flag:
    print("New post found, TRUE flag.")
else:
    print("No new posts.")