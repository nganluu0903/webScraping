import scrapy
import scrapy
from urllib.parse import urlencode
from pathlib import Path
import os
import lxml

API_KEY = '9b576740-89c6-4214-bfd1-6f452190fe8a'
FILE_NAME=1
MAIN_URL = "https://www.classcentral.com"
def get_scrapeops_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url

class TestSpider(scrapy.Spider):
    name = "quotes"
    custom_settings = { 
    #   'CONCURRENT_REQUESTS': 1,
      'USER_AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'
   }
    def start_requests(self):
        start_urls = [
        "https://www.classcentral.com/",
    ]

        for url in start_urls:
            # yield scrapy.Request(url=get_scrapeops_url(url), callback=self.parse)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        filename = Path(Path.cwd() / "main.html").resolve()
        href_dict={}
        body = response.body.decode('utf-8')
        for href in response.css('li a::attr(href)'):
            url = MAIN_URL+href.get()
            origin_href = href.get()
            
            process_href = origin_href
            if MAIN_URL in process_href:
                process_href=''.join(process_href.split(MAIN_URL)) 
            if process_href[0] == "/":
                process_href = process_href[1:]
            if process_href[-1] == "/":
                process_href = process_href[:-1]
            href_dict[origin_href]=process_href
            # body.replace(origin_href,process_href+"/index.html")
            yield scrapy.Request(url=get_scrapeops_url(url), callback=self.sub_parse,meta={'href': process_href})
        body_lxml = lxml.html.document_fromstring(response.body)
        for thumbnail in body_lxml.xpath('//img'):
            thumbnail_src = thumbnail.get('src') # Original link address
            thumbnail_path = './thumbnails/' + basename(thumbnail_src) # New link address
            thumbnail.set('src',image_path)
            with open(filename, 'w') as f:
                f.write(body)
            break
        
       
            

    def sub_parse(self, response):
        href = response.meta['href']

        directory = Path(Path.cwd() / href)
        os.makedirs(directory,exist_ok=True)
        filename = Path(directory / "index.html").resolve()
        with open(filename, 'wb') as f:
            f.write(response.body)

# class TestSpider(scrapy.Spider):
#     name = "test"

#     start_urls = [
#         "https://www.classcentral.com/",
#     ]

#     def parse(self, response):
#         filename = response.url.split("/")[-1] + '.html'
#         with open(filename, 'wb') as f:
#             f.write(response.body)