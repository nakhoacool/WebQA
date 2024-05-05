from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import sys
from bs4 import BeautifulSoup
from scrapy.loader import ItemLoader
from pathlib import Path
from colorama import Fore, Style

PATH = "../drive/MyDrive/uni/graduate/crawl/TDTdata/"
class TDTConfig:

  def __init__(self):
    self.title_css = [".padding-bottom-0 > h2:nth-child(1)",\
     "h1.post-title"]
    self.content_css = ["div.col-lg-12:nth-child(6) > div:nth-child(1) > div:nth-child(1)",\
     ".node__content"]
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
    name = "tdt"
    #dads allowed_domains = ["tdtu.edu.vn"]
    start_urls = ["https://www.tdtu.edu.vn/", "https://tdtu.edu.vn/"]
    rules = [
      Rule(LinkExtractor(
        deny=[r"https://.*tdtu\.edu\.vn/.*tin-tuc.*",
          r"https://.*tdtu\.edu\.vn/.*news.*"
          r"https://lib.tdtu\.edu\.vn/.*",
          r"https://vfis.*.tdtu\.edu\.vn/.*"
          r"https://oer.tdtu\.edu\.vn/.*",
          r"http.?://.*pinterest\.com/.*",
          r"http.?://.*facebook\.com/.*",
          r"http.?://.*linkedin\.com.*",
          r"http.?://.*youtube\.com/.*",
          r"https://.*360.*", 
          r"https://.*tdtu\.edu\.vn/.*login.*",
          r"https://.*tdtu\.edu\.vn/.*signup.*"],\
        allow=r"https://.*tdtu\.edu\.vn/.*"),\
        callback='parse_item', follow=True),
    ]

    def __init__(self, *a, **kw):
      super(TDTSpider, self).__init__(*a, **kw)
      self.config = TDTConfig()
      print("Init")

    def log(self, text):
      print(Fore.GREEN + text + Style.RESET_ALL)

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
      Path(f"{PATH}/data/{filename}.html").write_bytes(response.body)
      self.log(f"Saved file {filename}")
      try:
        # data = {\
        #   "url": response.url,\
        #   "title": title.text,\
        #   "content": content.text,\
        #   "html_name": filename,\
        #   "strip": strips
        # }
        data = {
          "url": response.url,
          "html_name": filename,
        }
        yield data
      except:
        print("[ERROR]")
      
