from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import re
from markdownify import markdownify as md
from src.service.applog import AppLogService

class WebPageMDLoader:

    def __init__(self) -> None:
        self.env_path = os.path.dirname(__file__)
        base_path = os.path.join(self.env_path, "../../data/crawler_config")
        self.log = AppLogService(name="crawler.log")
        self.content_selectors = pd.read_csv(os.path.join(base_path, "body_identifiers.csv"))
        self.remove_selectors = pd.read_csv(os.path.join(base_path, "remove_identifiers.csv"))
        return

    def load_page(self, link:str) -> str:
        """
            load the text data from a link.

            @param link the URL link

            @return a clean text in md format
        """
        html = requests.get(link)
        soup = BeautifulSoup(html.content, 'html.parser')
        content = None
        # find content
        for idx, data in self.content_selectors.iterrows():
            content = soup.select_one(data['id'])
            if not content == None:
                break
        # remove
        if not content:
            self.log.logger.info(f"[NEW] {link}")
            return soup
        for selector in self.remove_selectors:
            [hit.decompose() for hit in content.select(selector=selector)]
            content.smooth()
        doc = md(html=content.prettify(), 
                 heading_style="ATX", newline_style="\n", 
                 wrap=True, wrap_width=80)
        strips = ["\n{3,}", "\s{3,}", "\t{3, }"]
        replaces = ["\n", " ", " "]
        for strip, replace in zip(strips, replaces):
            doc = re.sub(strip, replace, doc)
        return doc