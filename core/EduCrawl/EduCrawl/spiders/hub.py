from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup
from pathlib import Path
from colorama import Fore, Style
import re

PATH = "../drive/MyDrive/uni/graduate/crawl/HUB/"

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

CONTENT_XPATH = "/html/body/div[1]/div[4]/div[2]/div/div[2]/div/div"

class TDTConfig:

  def __init__(self):
    self.title_css = [".thongbao_tieude",".panel-title"]
    self.content_css = [".thongbao_text"]
    self.remove_css = ["style", "script", "iframe", "img", "button"]
  
  def get_config(self, index=0):
    try:
      title = self.title_css[index]
      content = self.content_css[index]
    except:
      return None, None
    return title, content


class TDTSpider(CrawlSpider):
    name = "hub"
    start_urls = ["http://tuyensinh.hub.edu.vn/"]
    rules = [
      Rule(
        LxmlLinkExtractor(
          allow="http://tuyensinh.hub\.edu\.vn/.*", deny_domains=DENY, deny=DENY_LINKS), 
          callback='parse_item', follow=True)
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
      allow_run = False
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
        contents = response.xpath(CONTENT_XPATH).css("::text").getall()
        titles = response.css(".thongbao_tieude::text").getall()
        data = {
          "url": weburl,
          "skipped": 'yes',
          "title": "\n".join(titles),
          "content": "\n".join(contents) 
        }
        self.log(text=f"Collected: {len(data['title'])} - {len(data['content'])}")
      yield data