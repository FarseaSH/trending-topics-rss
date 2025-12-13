#!/usr/bin/env python3
"""
微博热搜 RSS 转换脚本
将原始 RSS 中的每个热搜条目聚合为一个时刻的快照
"""

import feedparser
import requests
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import pytz

def fetch_rss(url):
    """获取原始 RSS feed"""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return feedparser.parse(response.content)

def create_rss_feed(items):
    """创建新的 RSS feed"""
    rss = Element('rss', version='2.0')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
    
    channel = SubElement(rss, 'channel')
    
    # 频道信息
    title = SubElement(channel, 'title')
    title.text = '微博热搜榜 - 聚合版'
    
    link = SubElement(channel, 'link')
    link.text = 'https://tophub.today/n/KqndgxeLl9'
    
    description = SubElement(channel, 'description')
    description.text = '每个条目包含一个时刻的所有热搜'
    
    language = SubElement(channel, 'language')
    language.text = 'zh-cn'
    
    lastBuildDate = SubElement(channel, 'lastBuildDate')
    lastBuildDate.text = datetime.now(pytz.UTC).strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # 添加聚合的 items
    for item_data in items:
        channel.append(item_data)
    
    return rss

def aggregate_hotlist(feed):
    """聚合热搜列表为单个 item"""
    # 获取当前时间（北京时间）
    beijing_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(beijing_tz)
    
    # 创建新的 item
    item = Element('item')
    
    # 标题
    title = SubElement(item, 'title')
    title.text = f"微博热搜 - {current_time.strftime('%Y年%m月%d日 %H:%M')}"
    
    # 链接
    link = SubElement(item, 'link')
    link.text = 'https://tophub.today/n/KqndgxeLl9'
    
    # 描述（正文内容）
    description = SubElement(item, 'description')
    
    # 构建热搜列表的 HTML 内容
    content_lines = ['<h2>微博热搜榜</h2>', '<ol>']
    
    for idx, entry in enumerate(feed.entries, 1):
        entry_title = entry.get('title', '无标题')
        entry_link = entry.get('link', '#')
        content_lines.append(f'<li><a href="https://m.weibo.cn/search?containerid=100103type%3D1%26q%3D%E5%85%AD%E7%BA%A7{entry_title}" target="_blank">{entry_title}</a></li>')
    
    content_lines.append('</ol>')
    content_lines.append(f'<p><small>采集时间: {current_time.strftime("%Y-%m-%d %H:%M:%S")}</small></p>')
    
    description.text = '\n'.join(content_lines)
    
    # 发布时间
    pubDate = SubElement(item, 'pubDate')
    pubDate.text = current_time.strftime('%a, %d %b %Y %H:%M:%S %z')
    
    # GUID
    guid = SubElement(item, 'guid', isPermaLink='false')
    guid.text = f"weibo-hot-{current_time.strftime('%Y%m%d%H%M%S')}"
    
    return item

def prettify_xml(elem):
    """美化 XML 输出"""
    rough_string = tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')

def main():
    """主函数"""
    rss_url = 'https://rsshub.liumingye.cn/tophub/KqndgxeLl9'
    output_file = './public/weibo_hot_aggregated.xml'
    
    print(f"正在获取 RSS feed: {rss_url}")
    feed = fetch_rss(rss_url)
    
    print(f"获取到 {len(feed.entries)} 条热搜")
    
    # 聚合热搜为单个 item
    aggregated_item = aggregate_hotlist(feed)
    
    # 创建新的 RSS feed（只包含这一个聚合的 item）
    new_rss = create_rss_feed([aggregated_item])
    
    # 输出到文件
    xml_content = prettify_xml(new_rss)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"已生成新的 RSS feed: {output_file}")
    print(f"当前时间: {datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()