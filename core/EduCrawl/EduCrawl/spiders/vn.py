from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import sys
from bs4 import BeautifulSoup
from scrapy.loader import ItemLoader
from pathlib import Path

class TDTConfig:

  def __init__(self):
    self.title_css = [".title-detail"]
    self.content_css = [".fck_detail "]
    self.remove_css = [".block-ts-2-button", ".header-main",\
     "iframe", "img", ".sidebar", ".footer-center", ".copyright",\
     ".block-nganh-7", ".block-nganh-8"]

  def get_config(self, index=0):
    try:
      title = self.title_css[index]
      content = self.content_css[index]
    except:
      return None, None
    return title, content


class TDTSpider(CrawlSpider):
    name = "vn"
    allowed_domains = ["vnexpress.net"]
    start_urls = ["https://vnexpress.net/thoi-su/chinh-tri"]
    rules = [
      Rule(LinkExtractor(allow=r"https://.*vnexpress\.net/.*"),\
       callback='parse_item', follow=True),
    ]

    def __init__(self, *a, **kw):
      super(TDTSpider, self).__init__(*a, **kw)
      self.config = TDTConfig()
      print("Init")

    @property
    def header(self):
       return {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
      }

    def parse_item(self, response):
      soup = BeautifulSoup(response.body, 'html.parser')
      soup.attrs.clear()

      title = None
      content = None
      strips = self.config.remove_css
      # config
      index = -1
      while(title == None or content == None):
        index += 1
        title_css, content_css = self.config.get_config(index)
        if title_css == None:
          break
        # get soup
        title = soup.select_one(title_css)
        content = soup.select_one(content_css)
      filename = response.url.replace("https://","").replace("/","_")
      # Path(f"./data/{filename}.html").write_bytes(response.body)
      self.log(f"Saved file {filename}")
      data = {\
        "url": response.url,\
        "title": title.text,\
        "content": content.text,\
        "html_name": filename,\
        "strip": strips
      }
      yield data
