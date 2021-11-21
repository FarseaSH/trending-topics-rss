# %%
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

r = requests.get("https://tophub.today/n/KqndgxeLl9",
                 headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit"}
                 ) 

soup = BeautifulSoup(r.text, 'html.parser')
container_lst = soup.find_all(class_='rank-item-container')

# 微博热榜
weibo_content = ""
i = 1
for node in container_lst[:40]:
    # query
    title = node.find_next(class_='s-title')
    popularity = node.find_next(class_='s-tie-count')
    url = r"https://s.weibo.com/weibo?q=%23" + title.text + r"%23"


    a = f'<a href="{ url }">' + title.text + "----" + popularity.text + r'</a>'  # link
    weibo_content += f"<p>{i}  {a}</p>  + \n"
    i += 1


rss_output =f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>热榜</title>
    <link>https://www.w3schools.com</link>
    <description><![CDATA[热榜RSS解决方案]]></description>

<item>
    <title>微博热榜 - {datetime.now().strftime(r"%H:%M %a %Y-%m-%d")}</title>
    <link>https://www.w3schools.com</link>
    <description><![CDATA[{weibo_content}]]></description>
</item>
</channel>
</rss>
"""

# save the output
Path('./public').mkdir(parents=True, exist_ok=True)
with open(r'./public/weibo.xml', mode='w', encoding="utf-8") as f:
    f.write(rss_output)