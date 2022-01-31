from os import pardir
from re import sub
from unicodedata import name
import gdown
import subprocess
import os

from git import base
from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum, PechaMetaData
from openpecha.core.pecha import OpenPechaFS 
from openpecha.core.annotation import AnnBase, Span
from uuid import uuid4
from openpecha.core.ids import get_pecha_id


url = 'https://drive.google.com/uc?id=10qcUAnT-C0X_sSWcRe7f48VBagv4G8eR'
output="./output/test3.zip"
par_dir = "output"


def download_drive():

    gdown.download(url, output, quiet=False)
    subprocess.run(f"unzip {output} -d {par_dir}",shell=True)
    subprocess.run(f"rm {output}",shell=True)
    subprocess.run(f"rm -rf {par_dir}/__MACOSX",shell=True)

def parse_file(dir):
    pecha_id = get_pecha_id()
    pecha_name = os.listdir(dir)[0]
    base_text = ''
    name=1
    for dirpath,dirnames,filenames in os.walk(dir):
        

        if filenames and os.path.basename(dirpath) !=pecha_name:
            """ print("current path:",dirpath)
            print("directries",dirnames)
            print("files",filenames)
            print(len(filenames)) """
            filename = get_file_name(dirpath)
            if len(filenames) != 1:
                for file in filenames:
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
        path=os.path.basename(dirpath)+"_"+path if path != "" else os.path.basename(dirpath)
        dirpath=dirpath.replace(f"/{os.path.basename(dirpath)}","")
    print(path)
    return path

def get_base_text(path):
    with open(path,encoding="UTF-16LE") as f:
        base_text=f.read()

    return base_text                   

def create_opf(base_text,filename,pecha_id):
    opf_path=f"./opfs/{pecha_id}/{pecha_id}.opf"
    opf = OpenPechaFS(opf_path=opf_path)
    base = {f"{filename}":base_text}

    opf.base = base
    opf.save_base()


if __name__ == "__main__":
    #download_drive()
    parse_file(par_dir)




