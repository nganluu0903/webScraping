import scrapy
from urllib.parse import urlencode
from pathlib import Path
import os
import lxml
import random

MAIN_URL = "https://www.classcentral.com"
class ClassCentralSpider(scrapy.Spider):
    name = "classCentral"

    def start_requests(self):
        start_urls = ["https://www.classcentral.com"]
        yield scrapy.Request(url=start_urls[0], callback=self.parse)
    
    def process_href(self,href):
        if MAIN_URL in href:
            href=''.join(href.split(MAIN_URL)) 
        if href[0] == "/":
            href = href[1:]
        if href[-1] == "/":
            href = href[:-1]
        return href
    def parse(self, response):
        filename = Path(Path.cwd() / "main.html").resolve()
        href_dict={}
        with open(filename, 'wb') as f:
            f.write(response.body)

        # self.log(response.body)
        tree = lxml.html.fromstring(response.body)

        for anchor in tree.xpath("//a"):
            origin_href = anchor.get('href') # Original link address
            if origin_href !="/":
                
                new_href=self.process_href(origin_href)+"/index.html"
                self.log(f"{origin_href} ----> {new_href}")
                anchor.set('href',new_href) # Setting new link address
        modified_html_string = lxml.html.tostring(tree).decode('utf-8')
        filename = Path(Path.cwd() / "new_html.html").resolve()
        with open(filename, 'w') as f:
            f.write(modified_html_string)
        for href in response.css('li a::attr(href)'):
           
            origin_href = href.get()
            
            process_href = origin_href
            if MAIN_URL in process_href:
                process_href=''.join(process_href.split(MAIN_URL)) 
            if process_href[0] == "/":
                process_href = process_href[1:]
            if process_href[-1] == "/":
                process_href = process_href[:-1]
            url = MAIN_URL+"/"+process_href
            yield scrapy.Request(url=url, callback=self.sub_parse,meta={'href': process_href})
 
    def sub_parse(self, response):
        href = response.meta['href']

        directory = Path(Path.cwd() / href)
        os.makedirs(directory,exist_ok=True)
        filename = Path(directory / "index.html").resolve()
        with open(filename, 'wb') as f:
            f.write(response.body)
    
