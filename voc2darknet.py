import os
import sys
import argparse
import json
import xml.etree.ElementTree as ET
from typing import Dict, List
from tqdm import tqdm
import re

if len(sys.argv) < 3:
    print("Usage python voc2darknet.py $DIR_PATH $LABEL_FILE")
    exit()

with open(sys.argv[2]) as f:
    lines = f.readlines()
    lines = [el.strip() for el in lines] 

LABELS = lines

def convert_d_to_darknet(d, size_w, size_h):
    xmin = d['xmin']
    ymin = d['ymin']
    xmax = d['xmax']
    ymax = d['ymax']
    w = xmax - xmin
    h = ymax - ymin
    x, y = (xmin + w/2), (ymin + h/2)
    dw = 1./size_w
    dh = 1./size_h
    x *= dw
    y *= dh
    w *= dw
    h *= dh
    return (x,y,w,h)


def get_darknet_lines(annotation_root):
    size = annotation_root.find('size')
    width = int(size.findtext('width'))
    height = int(size.findtext('height'))
    write_lines = []
    for obj in annotation_root.findall('object'):
        bounding_box = obj.find('bndbox')
        d = {}
        for el in ['xmin','ymin','xmax','ymax']:
            d[el] = float(bounding_box.findtext(el))
        d['class'] = obj.findtext('name')
        #class_index = LABELS.index(d['class'])
        class_index = 0
        x, y, w, h = convert_d_to_darknet(d, width, height)
        line = f'{class_index} {x} {y} {w} {h} \n'
        write_lines.append(line)

    return write_lines

def convert_xmls_to_darknet(annotation_paths):
    for a_path in tqdm(annotation_paths):
        # Read annotation xml
        ann_tree = ET.parse(a_path)
        ann_root = ann_tree.getroot()
        try:
            write_lines = get_darknet_lines(ann_root)    
        except:
            write_lines = []
        txt_a_path = a_path.replace('xml','txt')
        #print(f'Writing to {txt_a_path}')
        with open(txt_a_path, 'w') as f:
            f.writelines(write_lines)


if __name__ == '__main__':
    ann_paths = []
    for root, dirs, files in os.walk(sys.argv[1], topdown=False):
        for f in files:
            full_filepath = os.path.join(root,f)
            if full_filepath.endswith('xml'):
                ann_paths.append(full_filepath)

    convert_xmls_to_darknet(ann_paths)
