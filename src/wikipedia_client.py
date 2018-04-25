import wikipedia
import os.path
import xml.etree.cElementTree as ET
import logging

def download_articles(page_titles_list, dump_folder_path, lang="en"):
    logging.info("Articles download start")
    wikipedia.set_lang(lang)
    extracted_pages_titles=[]
    for title in page_titles_list:
        filename = title.encode('ascii',errors='ignore').replace(" ","_")+".xml"
        dump_file_path=dump_folder_path+filename
        if os.path.isfile(dump_file_path):
            logging.error(title+": Dump file already exists")
            continue
        try:
            page=wikipedia.page(title)
            file = open(dump_file_path, 'a+')
            root=ET.Element("documents")
            doc = ET.SubElement(root, "doc")
            doc.set('title', page.title)
            doc.text=page.content
            tree = ET.ElementTree(root)
            tree.write(file)
            extracted_pages_titles.append(page.title)
        except:
            print(title+" page not saved")
            logging.info(title+" page not saved")

    logging.info("Articles download end")
    return extracted_pages_titles
