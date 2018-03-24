#!/usr/bin/python3

import sys, os, datetime, re
import urllib3
import os.path

pictures = []
with open ('Pictures.csv', 'r' ) as f:
  for s in f.read().splitlines():
    fields = s.split(';')
    picture = {'link': fields [0], 'title': fields [1], 'description': fields [2], 'tags': fields [3], 'img_small': fields [4], 'img_orig': fields [5], 'lat': fields [6], 'lon': fields [7], 'album': fields [8]}
    pictures.append (picture)

def getFile (path, link):
  filename = path + '/' + link.split('/')[-1]
  if os.path.isfile(filename) == False:
    print ('Downloading', link, 'to', filename)
    response = http.request('GET', link)
    with open (filename, 'wb') as f:
      f.write (response.data)
  else:
    print ('Skipping', link, ', file', filename, 'exists')

http = urllib3.PoolManager()

#sudo mount -rw -t cifs \\\\10.10.1.52\\Yandex.Fotki mnt

path_small = 'mnt/XL'
path_orig = 'mnt/orig'

try:
  os.mkdir(path_small)
except Exception as e:
  print (e)

try:
  os.mkdir(path_orig)
except Exception as e:
  print (e)

pictures_count = 0

for picture in pictures:
  pictures_count = pictures_count + 1
  print ('Picture', pictures_count)
  img_small = picture ['img_small']
  img_orig = picture ['img_orig']
  
  getFile (path_small, img_small)
  
  getFile (path_orig, img_orig)
