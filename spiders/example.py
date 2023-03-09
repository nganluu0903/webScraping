import scrapy
from urllib.parse import urlencode
from pathlib import Path
import os
import lxml
import random
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import re
MAIN_URL = "https://www.classcentral.com"
translator = GoogleTranslator(source='auto', target='vi')
class ClassCentralSpider(scrapy.Spider):
    name = "classCentral"

    def start_requests(self):
        start_urls = ["https://www.classcentral.com"]
        yield scrapy.Request(url=start_urls[0], callback=self.parse)
    
    def process_href(self,href):
        if MAIN_URL in href:
            href=''.join(href.split(MAIN_URL)).strip()
        if href[0] == "/":
            href = href[1:]
        if href[-1] == "/":
            href = href[:-1]
        href=href.replace("%20","")
        return href
    def translator(self,text):
        if "{" in text:
            return text
        if len(text.strip())>0:
            # self.log(text)
            return translator.translate(text)
        return text
    def parse(self, response):
        filename = Path(Path.cwd() / "main.html").resolve()
        href_dict={}
        with open(filename, 'wb') as f:
            f.write(response.body)

        tree = lxml.html.fromstring(response.body)

        for anchor in tree.xpath("//a"):
            origin_href = anchor.get('href')
            if origin_href !="/":
                new_href=self.process_href(origin_href)+"/index.html"
                anchor.set('href',new_href)

        # for img in tree.xpath("//img"):
        #     src = img.get('src')
        #     modify_src = re.sub("blur=\d*&", "", src)
        #     self.log(f"{src} --> {modify_src}")
        #     img.set('src',modify_src)
        modified_html_string = lxml.html.tostring(tree).decode('utf-8')
        
        filename = Path(Path.cwd() / "new_html.html").resolve()
        with open(filename, 'w') as f:
            f.write(modified_html_string)
        
        # =============================================================
        with open(filename) as fp:
            soup = BeautifulSoup(fp, "html.parser")
        tags=[tag.name for tag in soup.find_all()]
        all_text=[]
        for tag in tags:
            if tag=="script" or tag=="style" or tag=="title" or tag =="div":
                continue
            for s in soup.findAll(tag,string=True):
                if s.text and "{" not in s.text and len(s.text.strip())>0:
                    if s.text in all_text:
                        continue
                    all_text.append(s.text)
                    # a = self.translator(s.text)
                    # self.log(f"{s.text}--->{a}")
                    # s.string.replace_with(a)

        def batch(iterable, n=1):
            l = len(iterable)
            for ndx in range(0, l, n):
                yield iterable[ndx:min(ndx + n, l)]
        
        batch_size = len(all_text)//20
        translated_text=[]
        for small_batch in  batch(all_text, batch_size):
            temp="#".join(small_batch)
            trans_temp =  translator.translate(temp)
            translated_small_batch = trans_temp.split("#")
            translated_text.extend(translated_small_batch)
        #     target = all_text[i:]
        # if len(list(all_text)>3000):
        #     mid = len(all_text)//2
        #     left=all_text[0:mid]
        #     right = all_text[mid:]
        #     temp = "#".join
        # temp="#".join(all_text)
        # self.log(len(temp))
        # trans_temp =  translator.translate(temp)
        # translated_text = trans_temp.split("#")
        # translated_text = translator.translate_batch(all_text)

        word_dictionary = dict(zip(all_text, translated_text))
        # self.log(word_dictionary)
        for tag in tags:
            if tag=="script" or tag=="style" or tag=="title" or tag =="div":
                continue
            for s in soup.findAll(tag,string=True):
                if s.text and "{" not in  s.text and len(s.text.strip())>0:
                    # self.log(s.text)
                    try:
                        s.string.replace_with(word_dictionary[s.text])
                    except:
                        pass
                    # all_text.append(s.text)
        # tags=[tag.name for tag in soup.find_all()]
        # for tag in tags:
        #     if tag=="script" or tag=="style" or tag=="title" or tag =="div":
        #         continue
        #     for s in soup.findAll(tag,string=True):
        #         s.replace_with(self.translator(s.text))
        html = soup.prettify("utf-8")
        filename = Path(Path.cwd() / "translate.html").resolve()
        with open(filename, "wb") as file:
            file.write(html)

        for href in response.css('li a::attr(href)'):
            origin_href = href.get()
            # process_href = origin_href
            process_href = self.process_href(origin_href)
            # if MAIN_URL in process_href:
            #     process_href=''.join(process_href.split(MAIN_URL)) 
            # if process_href[0] == "/":
            #     process_href = process_href[1:]
            # if process_href[-1] == "/":
            #     process_href = process_href[:-1]
            url = MAIN_URL+"/"+process_href
            # compare = a==process_href
            # self.log(f"Compare: {compare} _> {process_href} - {a}")
            directory = Path(Path.cwd() / process_href)
            filename = Path(directory / "index.html").resolve()
            # if not filename.is_file():
            #     os.makedirs(directory,exist_ok=True)
                # yield scrapy.Request(url=url, callback=self.sub_parse,meta={'save_dir': filename})
                # break
 
    def sub_parse(self, response):
        filename = response.meta['save_dir']

        soup = BeautifulSoup(response.body)
        tags=[tag.name for tag in soup.find_all()]
        for tag in tags:
            if tag=="script" or tag=="style" or tag=="title" or tag =="div":
                continue
            for s in soup.findAll(tag,string=True):
                if s.text:
                    a = self.translator(s.text)
                    s.string.replace_with(a)
                
                # s.replace_with(self.translator(s.text))
        html = soup.prettify("utf-8")
        
        with open(filename, "wb") as file:
            file.write( )
    
