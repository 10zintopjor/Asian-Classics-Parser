from email.mime import base
from fileinput import filename
import gdown
import subprocess
import os
import re
import chardet
from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum, PechaMetaData
from openpecha.core.pecha import OpenPechaFS 
from openpecha.core.annotation import Page, Span
from openpecha.core.ids import get_pecha_id
from uuid import uuid4
from datetime import datetime

url = 'https://drive.google.com/uc?id={id}'
output="./temp/temp.zip"
par_dir = "temp"
vol_no_name_map={}
vol = 1


def download_drive(id):
    gdown.download(url.format(id=id), output, quiet=False)
    subprocess.run(f"unzip {output} -d {par_dir}",shell=True)
    subprocess.run(f"rm -rf {output}",shell=True)
    subprocess.run(f"rm -rf {par_dir}/__MACOSX",shell=True)


def parse_file(dir):
    pecha_id = get_pecha_id()
    pecha_name = os.listdir(dir)[0]
    base_text = ''
    for dirpath,_,filenames in sorted(os.walk(dir)):
        if filenames and os.path.basename(dirpath) !=pecha_name:
            filename = get_file_name(dirpath)
            if len(filenames) != 1:      
                for file in sorted(filenames):
                    path = os.path.join(dirpath,file)
                    base_text += get_base_text(path)
            else:
                path = os.path.join(dirpath,filenames[0])
                base_text = get_base_text(path)
            create_opf(base_text,filename,pecha_id) 
            base_text = ''
    create_meta(pecha_id)

def create_meta(pecha_id):
    opf_path=f"./opfs/{pecha_id}/{pecha_id}.opf"
    opf= OpenPechaFS(opf_path=opf_path)

    meta = get_meta()    
    opf._meta=meta
    opf.save_meta()

def get_meta():
    instance_meta = PechaMetaData(
        initial_creation_type=InitialCreationEnum.input,
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
        source_metadata=vol_no_name_map)

    return instance_meta

def get_file_name(dirpath):
    path = ""
    while os.path.basename(dirpath) != par_dir:
        path=os.path.basename(dirpath)+"/"+path if path != "" else os.path.basename(dirpath)[0:20]
        dirpath=dirpath.replace(f"/{os.path.basename(dirpath)}","")
    return path.replace(" ","_")


def get_base_text(path):
    try:
        with open(path,encoding="UTF-16LE") as f:
            base_text=f.read()
    except:
        base_text=''
    return base_text[2:-1].replace("[DD]","")            


def create_opf(base_text,filename,pecha_id):
    global vol
    print(filename)
    opf_path=f"./opfs/{pecha_id}/{pecha_id}.opf"
    opf = OpenPechaFS(opf_path=opf_path)
    new_filename = str("{:0>3d}".format(int(vol)))
    vol_no_name_map.update({f"v{new_filename}":f"{filename}"})
    base = {f"v{new_filename}":base_text}
    layers = {f"v{new_filename}": {LayerEnum.pagination: get_pagination_layer(base_text)}}

    opf.layers = layers
    opf.base = base
    opf.save_base()
    opf.save_layers()
    vol+=1

def get_pagination_layer(base_text):

    page_annotations = {}
    char_walker = 0

    formatted_text = format_text(base_text)

    for text in formatted_text:
        lot = len(text)
        page_annotation, char_walker = get_page_annotation(text, char_walker)
        page_annotations.update(page_annotation)

    pagination_layer = Layer(
        annotation_type=LayerEnum.pagination, annotations=page_annotations
    )

    return pagination_layer

def get_page_annotation(text,char_walker):

    imgnum = get_imgnum(text)

    page_annotation = {
        uuid4().hex: Page(span=Span(start=char_walker, end=char_walker+len(text)), metadata={"imgnum":imgnum})
    } 

    return page_annotation,(char_walker + len(text) + 2)   

def get_imgnum(text):
    text=text.replace("[?]","")
    img = re.search("(\[.*\])?(.*)",text,re.DOTALL)
    imgnum = re.search("\[(.*)\](.*)?",img.group(1)).group(1) if img.group(1) != None else img.group(1)
    return imgnum

def format_text(base_text):
    bases = re.split("\n\n",base_text)

    return bases

def main(drive_id):
    #download_drive(drive_id)
    parse_file(par_dir)


if __name__ == "__main__":
    main('10qcUAnT-C0X_sSWcRe7f48VBagv4G8eR')




