import os
from pathlib import Path
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='auto', target='hi')
def batch_translate(html_contents):
    def batch(iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]
    
    batch_size = len(html_contents)//10
    translated_text=[]
    for small_batch in  batch(html_contents, batch_size):
        if len(small_batch)>=1:
            temp="#".join(small_batch)
            
            trans_temp =  translator.translate(temp)
            # print(f"{temp}-->{trans_temp}")
            if trans_temp:
                translated_small_batch = trans_temp.split("#")
            else:
                translated_small_batch = temp
            translated_text.extend(translated_small_batch)
    return translated_text

if __name__=="__main__":
    html_file_path=[]
    path =  Path(Path.cwd() / "output").resolve()
    for dirpath, subdirs, files in os.walk(path):
        for x in files:
            if x.endswith(".html"):
                html_file_path.append(os.path.join(dirpath, x))
    # print(html_file_path)
    for filename in html_file_path:
        
        output_filename = filename.replace("output","output_translate")
        output_filename = Path(output_filename)
        if output_filename.is_file():
           continue 
        try:
            print(filename)
            with open(filename,  encoding="utf-8") as fp:
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
            translated_text = batch_translate(all_text)
            word_dictionary = dict(zip(all_text, translated_text))
            for tag in tags:
                if tag=="script" or tag=="style" or tag=="title" or tag =="div":
                    continue
                for s in soup.findAll(tag,string=True):
                    if s.text and "{" not in  s.text and len(s.text.strip())>0:
                        try:
                            s.string.replace_with(word_dictionary[s.text])
                        except:
                            pass
            html = soup.prettify("utf-8")
            
            os.makedirs(output_filename.parents[0],exist_ok=True)
            with open(output_filename, "wb") as file:
                file.write(html)
                print("Done")
        except Exception as e: 
            print(e)
        