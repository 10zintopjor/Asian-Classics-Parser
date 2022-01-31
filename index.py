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



url = 'https://drive.google.com/uc?id={id}'
output="./temp/temp.zip"
par_dir = "temp"


def download_drive(id):
    gdown.download(url.format(id=id), output, quiet=False)
    subprocess.run(f"unzip {output} -d {par_dir}",shell=True)
    subprocess.run(f"rm {output}",shell=True)
    subprocess.run(f"rm -rf {par_dir}/__MACOSX",shell=True)

def parse_file(dir):
    pecha_id = get_pecha_id()
    pecha_name = os.listdir(dir)[0]
    base_text = ''
    name=1
    for dirpath,dirnames,filenames in sorted(os.walk(dir)):
        if filenames and os.path.basename(dirpath) !=pecha_name:
            """ print("current path:",dirpath)
            print("directries",dirnames)
            print("files",filenames)
            print(len(filenames)) """
            filename = get_file_name(dirpath)
            if len(filenames) != 1:
                
                for file in sorted(filenames):
                    path = os.path.join(dirpath,file)
                    base_text += get_base_text(path)
            else:
                path = os.path.join(dirpath,filenames[0])
                base_text = get_base_text(path)
            create_opf(base_text,filename,pecha_id)  
            name+=1
            base_text = ''

def get_file_name(dirpath):
    path = ""
    while os.path.basename(dirpath) != par_dir:
        path=os.path.basename(dirpath)+"_"+path if path != "" else os.path.basename(dirpath)[0:20]
        dirpath=dirpath.replace(f"/{os.path.basename(dirpath)}","")
    return path


def get_base_text(path):
    try:
        with open(path,encoding="UTF-8") as f:
            base_text=f.read()
    except:
        base_text=''
    return base_text                   


def create_opf(base_text,filename,pecha_id):
    print(filename)
    opf_path=f"./opfs/{pecha_id}/{pecha_id}.opf"
    opf = OpenPechaFS(opf_path=opf_path)
    base = {f"{filename}":base_text}
    layers = {f"{filename}": {LayerEnum.pagination: get_pagination_layer(base_text)}}

    opf.layers = layers
    opf.base = base
    opf.save_base()
    opf.save_layers()


def get_pagination_layer(base_text):

    page_annotations = {}
    char_walker = 0

    formatted_text = format_text(base_text)

    for text in formatted_text:
        page_annotation, char_walker = get_page_annotation(text, char_walker)
        page_annotations.update(page_annotation)

    pagination_layer = Layer(
        annotation_type=LayerEnum.pagination, annotations=page_annotations
    )

    return pagination_layer

def get_page_annotation(text,char_walker):

    imgnum,text = split_text(text)

    page_annotation = {
        uuid4().hex: Page(span=Span(start=char_walker, end=char_walker+len(text)), metadata={"imgnum":imgnum})
    } 

    return page_annotation, (char_walker + len(text) + 3)   

def split_text(text):
    text=text.replace("[?]","")
    imgnum = re.search("(\[.*\])?(.*)",text,re.DOTALL)

    return imgnum.group(1),imgnum.group(2)

def format_text(base_text):
    base_text = base_text.strip("\n")
    bases = re.split("\n\n\n",base_text)

    return bases

def main(drive_id):
    download_drive(drive_id)
    parse_file(par_dir)


if __name__ == "__main__":
    main('1N2PoU5j1FQ15-63D8CcpegIVLvVXZPOp')




