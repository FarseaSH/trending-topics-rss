# %%
from datetime import datetime, timedelta
from pathlib import Path
import configparser

import requests
from bs4 import BeautifulSoup


class ContentParser():
    def __init__(self, rebang_id, title, original_url) -> None:
        self.rebang_id = rebang_id
        self.title = title
        self.original_url = original_url

    def _parseRawPage(self):
        """
        return rank-item in a list
        """

        r = requests.get(
            r"https://tophub.today/n/{rebang_id}".format(rebang_id=self.rebang_id),
            headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit"}
        ) 
        soup = BeautifulSoup(r.text, 'html.parser')

        return soup.find_all(class_='rank-item-container')

    def _getDescriptionPart(self):
        """
        parse the rank-item list and return the description part in RSS
        """

        content = ""
        i = 1
        for node in self._parseRawPage()[:40]:
            # query
            url = node['href']
            title = node.find_next(class_='s-title')
            popularity = node.find_next(class_='s-tie-count')

            a = f'<a href="{r"https://tophub.today" +  url }">' + title.text + "----" + popularity.text + r'</a>'  # link
            content += f"<p>{i}  {a}</p>\n"
            i += 1

        return content

    def getItem(self):
        current_beijing_time = datetime.now() + timedelta(hours=8.0)

        return f"""
        <item>
        <title>{self.title} - {current_beijing_time.strftime(r"%H:%M %a %Y-%m-%d")}</title>
        <link>{self.original_url}</link>
        <description><![CDATA[{self._getDescriptionPart()}]]></description>
        </item>
        """


class WeiboParser(ContentParser):
    def __init__(self):
        WEIBO_ID = "KqndgxeLl9"
        super().__init__(WEIBO_ID, "微博热搜", "https://s.weibo.com/top/summary")


    def _getDescriptionPart(self):
        weibo_content = ""
        i = 1
        for node in self._parseRawPage()[:40]:
            # query
            title = node.find_next(class_='s-title')
            popularity = node.find_next(class_='s-tie-count')
            url = r"https://s.weibo.com/weibo?q=%23" + title.text + r"%23"
            a = f'<a href="{ url }">' + title.text + "----" + popularity.text + r'</a>'  # link
            weibo_content += f"<p>{i}  {a}</p>\n"
            i += 1
        return weibo_content


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    content_parser_list = []
    content_parser_list.append(WeiboParser())

    for section in config.sections():
        content_parser_list.append(ContentParser(rebang_id=config[section]['rebang_id'],
                                                 title=config[section]['title'],
                                                 original_url=config[section]['original_url']
                                                 ))

    item_part = "".join([c_p.getItem() for c_p in content_parser_list])

    rss_output =f"""<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
    <channel>
        <title>热榜</title>
        <link>https://github.com/FarseaSH/trending-topics-rss/blob/gh-pages/index.xml</link>
        <description><![CDATA[热榜RSS解决方案]]></description>
    {item_part}
    </channel>
    </rss>
    """

    # save the output
    Path('./public').mkdir(parents=True, exist_ok=True)
    with open(r'./public/index.xml', mode='w', encoding="utf-8") as f:
        f.write(rss_output)

if __name__ == "__main__":
    main()