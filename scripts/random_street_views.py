import argparse
import os
import random
import numpy as np
import sys
import matplotlib.path as mpltPath
from urllib.request import urlretrieve
import getcolor
import requests as req
import json

import shapefile as shp

API_KEY = "INSERT API KEY HERE"
REQUEST_METADATA_URL = ("https://maps.googleapis.com/maps/api/streetview/metadata?key=" + API_KEY )
REQUEST_IMAGE_URL = (
    "http://maps.googleapis.com/maps/api/streetview?"
    "size=640x640&key=" + API_KEY
)

FILE_PREFIX = "img_"
FILE_SUFFIX = ".jpg"
REQ_LIMIT = 10000

IMAGES_PER_COUNTRY = 160
COUNTRIES_WANTED = ["NOR"]

cur_country_index = -1
cur_countrynum = 0
cur_bbox = [0,0,0,0]
cur_polygon = []
cur_images = 0
requests = 0

SHAPEFILE = "TM_WORLD_BORDERS_0.3-refined.shp"

sf = shp.Reader(SHAPEFILE, encoding="utf8")
shapes = sf.shapes()

def is_point_inside_polygon(x, y, polygon):
    path = mpltPath.Path(polygon)
    inside = path.contains_point(np.array([x, y]))
    return inside

def get_shapenum_of_country(countrycode):
    for i, entry in enumerate(sf.records()):
        # entry[2] is ISO3 of each country
        if entry[2] == countrycode:
            # bbox is the minimal bounding box
            return i

def get_polygon_by_countrynum(countrynum):
    return shapes[countrynum].points

def get_bbox_by_countrynum(countrynum):
    return shapes[countrynum].bbox

def prepare_next_country():
    global cur_countrynum
    global cur_country_index
    global cur_bbox
    global cur_polygon
    global cur_images
    print("prepare next c 1: " + str(cur_country_index))
    cur_country_index += 1
    print("prepare next c 2: " + str(cur_country_index))
    print(len(COUNTRIES_WANTED))
    cur_countrynum = get_shapenum_of_country(COUNTRIES_WANTED[cur_country_index])
    cur_bbox = get_bbox_by_countrynum(cur_countrynum)
    cur_polygon = get_polygon_by_countrynum(cur_countrynum)
    cur_images = 0
    

while cur_country_index < (len(COUNTRIES_WANTED) - 1):

    prepare_next_country()

    if requests >= REQ_LIMIT:
        sys.exit()


    if not os.path.exists(COUNTRIES_WANTED[cur_country_index]):
        os.makedirs(COUNTRIES_WANTED[cur_country_index])

    while cur_images < IMAGES_PER_COUNTRY:
        rand_lon = random.uniform(cur_bbox[0], cur_bbox[2])
        rand_lat = random.uniform(cur_bbox[1], cur_bbox[3])
        if is_point_inside_polygon(rand_lon, rand_lat, cur_polygon):
            lat_lon = str(rand_lat) + "," + str(rand_lon)
            url = REQUEST_METADATA_URL + "&location=" + lat_lon
            print(url)
            res = req.get(url)
            resp = json.loads(res.text)
            if resp["status"] == "OK":
                for i in range(0, 359, 90):
                    outfile = os.path.join(COUNTRIES_WANTED[cur_country_index], FILE_PREFIX + COUNTRIES_WANTED[cur_country_index] + "_"+ lat_lon + "_" + str(i) + FILE_SUFFIX)
                    url = REQUEST_IMAGE_URL + "&location=" + lat_lon + "&heading=" + str(i)
                    try:
                        print(url)
                        requests+=1
                        urlretrieve(url, outfile)
                        cur_images +=1
                        print("Processing " + COUNTRIES_WANTED[cur_country_index] + ":" + str(cur_images) + "/" + str(IMAGES_PER_COUNTRY) + " images")
                    except KeyboardInterrupt:
                        sys.exit("exit")
            if resp["status"] == "OVER_QUERY_LIMIT" or resp["status"] == "REQUEST_DENIED":
                sys.exit()
            if requests >= REQ_LIMIT:
                sys.exit()
            
     

    












