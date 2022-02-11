from email.mime import base
import gdown
import subprocess
import os
import re
from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum, PechaMetaData
from openpecha.core.pecha import OpenPechaFS 
from openpecha.core.annotation import Page, Span
from openpecha.core.ids import get_pecha_id
from openpecha import github_utils,config
from uuid import uuid4
from datetime import datetime

url = 'https://drive.google.com/uc?id={id}'
zipped_dir="temp/temp.zip"
par_dir = "temp"
extracted_dir = "temp/extracted"
vol_no_name_map={}
vol = 1


def download_drive(id):
    subprocess.run(f"mkdir {par_dir} && mkdir {extracted_dir}",shell=True)
    gdown.download(url.format(id=id), f"{zipped_dir}", quiet=False)
    subprocess.run(f"unzip {zipped_dir} -d {extracted_dir}",shell=True)
    delete_unwanted_files()


def delete_unwanted_files():
    subprocess.run(f"rm -rf {extracted_dir}/__MACOSX",shell=True)
    for dirpath,dirs,_ in sorted(os.walk(par_dir)):
        if "RTF" in dirs:
            subprocess.run(f"rm -rf '{dirpath}/RTF'",shell=True)


def parse_file():
    global zipped_dir
    pecha_id = get_pecha_id()
    pecha_name = os.listdir(f"{extracted_dir}")[0]
    subprocess.run(f"mv {zipped_dir} '{par_dir}/{pecha_name}.zip'",shell=True)
    zipped_dir=f"{par_dir}/{pecha_name}.zip"
    base_text = ''
    i=1
    for dirpath,_,filenames in sorted(os.walk(f"{extracted_dir}")):
        if filenames and os.path.basename(dirpath) !=pecha_name:
            file_name = get_file_name(dirpath)
            if len(filenames) != 1:      
                for file in sorted(filenames):
                    path = os.path.join(dirpath,file)
                    base_text += get_base_text(path)
            else:
                path = os.path.join(dirpath,filenames[0])
                base_text = get_base_text(path)
            create_opf(base_text,file_name,pecha_id) 
            base_text = ''
    create_meta(pecha_id)

    return pecha_id


def create_meta(pecha_id):
    opf_path=f"{config.PECHAS_PATH}/{pecha_id}/{pecha_id}.opf"
    opf= OpenPechaFS(opf_path=opf_path)

    meta = get_meta()    
    opf._meta=meta
    opf.save_meta()


def get_meta():
    instance_meta = PechaMetaData(
        initial_creation_type=InitialCreationEnum.input,
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
        source_metadata={"volume_no_to_title":vol_no_name_map})

    return instance_meta


def get_file_name(dirpath):
    
    path = ""
    while os.path.basename(dirpath) != "extracted":
        
        path=os.path.basename(dirpath)+"/"+path if path != "" else os.path.basename(dirpath)[0:20]
        dirpath=dirpath.replace(f"/{os.path.basename(dirpath)}","")
        
    path =  path.replace("  ","_")

    return path

    
def get_base_text(path):
    try:
        with open(path,encoding="UTF-16LE") as f:
            base_text=f.read()
    except:
        base_text=''
    return base_text[2:-1].replace("[DD]","")            


def create_opf(base_text,file_name,pecha_id):
    global vol

    opf_path=f"{config.PECHAS_PATH}/{pecha_id}/{pecha_id}.opf"
    opf = OpenPechaFS(opf_path=opf_path)
    new_filename = str("{:0>3d}".format(int(vol)))
    vol_no_name_map.update({f"v{new_filename}":f"{file_name}"})
    pagination_layer,base_text = get_pagination_layer(base_text)
    layers = {f"v{new_filename}": {LayerEnum.pagination: pagination_layer}}
    base = {f"v{new_filename}":base_text}

    opf.layers = layers
    opf.base = base
    opf.save_base()
    opf.save_layers()
    vol+=1


def get_pagination_layer(base_text):
    
    page_annotations = {}
    char_walker = 0
    formatted_text = format_text(base_text)
    base_text = ""

    for text in formatted_text:
        page_annotation, char_walker,text = get_page_annotation(text, char_walker)
        base_text += text +"\n\n"
        page_annotations.update(page_annotation)

    pagination_layer = Layer(
        annotation_type=LayerEnum.pagination, annotations=page_annotations
    )

    return pagination_layer,base_text


def get_page_annotation(text,char_walker):

    imgnum = get_imgnum(text)
    text = re.sub("\[.*.\]","",text)
    text=text.strip()

    page_annotation = {
        uuid4().hex: Page(span=Span(start=char_walker, end=char_walker+len(text)), imgnum=imgnum)
    } 

    return page_annotation,(char_walker + len(text) + 2),text  


def get_imgnum(text):
    text=text.replace("[?]","")
    img = re.search("(\[.*\])?(.*)",text,re.DOTALL)
    if img.group(1) != None:
        imgnum = re.search("\[(.*)\](.*)?",img.group(1)).group(1)
        img_no = re.search("(\d*)(\D*)",imgnum).group(1)
        img_alp = re.search("(\d*)(\D*)",imgnum).group(2)
        img_no = re.sub("^0+(?!$)", "", img_no)
        imgnum = int(img_no)*2-1 if img_alp == "A" else int(img_no)*2
    else:
        imgnum = img.group(1)
    return imgnum


def format_text(base_text):
    bases = re.split("\n\n",base_text)
    return bases


def publish_opf(pecha_id):
    pecha_path = f"{config.PECHAS_PATH}/{pecha_id}"
    assest_path =[f"{zipped_dir}"]

    github_utils.github_publish(
    pecha_path,
    not_includes=[],
    message="initial commit"
    )

    github_utils.create_release(
    repo_name=pecha_id,
    asset_paths=assest_path,
    )


def delete_temp_files():
    subprocess.run(f"rm -rf {par_dir}",shell=True)


def main(drive_id):
    download_drive(drive_id)
    pecha_id = parse_file()
    publish_opf(pecha_id)
    delete_temp_files()

if __name__ == "__main__":
    main('10qcUAnT-C0X_sSWcRe7f48VBagv4G8eR')




