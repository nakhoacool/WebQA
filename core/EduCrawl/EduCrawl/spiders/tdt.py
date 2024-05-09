from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup
from pathlib import Path
from colorama import Fore, Style
import re

PATH = "../drive/MyDrive/uni/graduate/crawl/TDTdata/"

DENY = [
  "lib.tdtu.edu.vn",
  "vfis.tdtu.edu.vn",
  "oer.tdtu.edu.vn",
  "clc.tdtu.edu.vn",
  "sdtc.tdtu.edu.vn",
  "grad.tdtu.edu.vn",
  "tttn.tdtu.edu.vn",
  "old-stdportal.tdtu.edu.vn",
  "new-stdportal.tdtu.edu.vn",
  "stdportal.tdtu.edu.vn",
  "elearning.tdtu.edu.vn",
  "icfe2022.tdtu.edu.vn",
  "iclrll2024.tdtu.edu.vn",
  "ecc.tdtu.edu.vn",
  "ccvc.tdtu.edu.vn",
  "www.pinterest.com",
  "pinterest.com",
  "www.facebook.com",
  "facebook.com",
  "www.youtube.com",
  "youtube.com",
  "www.linkedin.com",
  "linkedin.com"
  ]

DENY_LINKS=[
  "https://.*tdtu\.edu\.vn/.*tin-tuc.*",
  "https://.*tdtu\.edu\.vn/.*ban-tin.*",
  "https://.*tdtu\.edu\.vn/.*tu-khoa.*",
  "https://.*tdtu\.edu\.vn/.*news.*",
  "https://icfe.*tdtu.edu.vn",
  "https://iclrll.*tdtu.edu.vn",
  "https://.*360.*", 
  "https://.*tdtu\.edu\.vn/.*login.*",
  "https://.*tdtu\.edu\.vn/.*signup.*"
  ]

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
      Rule(
        LxmlLinkExtractor(
          allow="https://.*tdtu\.edu\.vn/.*", deny_domains=DENY, deny=DENY_LINKS), 
          callback='parse_item', follow=True),
    ]

    def __init__(self, *a, **kw):
      super(TDTSpider, self).__init__(*a, **kw)
      self.config = TDTConfig()
      print("Init")

    def warn(self, text):
      print(Fore.YELLOW + text + Style.RESET_ALL)

    def log(self, text):
      print(Fore.GREEN + text + Style.RESET_ALL)

    @property
    def header(self):
       return {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
      }

    def parse_item(self, response):
      weburl = response.url
      allow_run = True
      data = None
      # domain
      for domains in DENY:
        if domains in weburl:
          allow_run = False
          break
      # regex
      for link in DENY_LINKS:
        match = re.search(rf"{link}", weburl)
        if match:
          allow_run = False
          break
      # store
      if allow_run:
        filename = weburl.replace("https://","").replace("/","_")
        Path(f"{PATH}/data/{filename}.html").write_bytes(response.body)
        self.log(f"Saved file {filename}")
        data = {
          "url": weburl,
          "html_name": filename,
          "skipped": 'no'
        }
      else:
        self.warn(text=f"Skip {weburl}")
        data = {
          "url": weburl,
          "html_name": "",
          "skipped": 'yes'
        }
      yield data