#!/usr/bin/python3

import sys, os, datetime, re
import urllib3
from urllib.parse import unquote

albums = {}
pictures = []

def requestPictureDescription (http, link):
  print ('Getting', link)
  try:
    response = http.request('GET', link)
    s = response.data.decode()
    fields = re.findall(r'meta name="title" content="([^"]*)"', s)
    title = fields [0]
    fields = re.findall(r'photo-description__value[^>]*>([^<]*)</div>', s)
    if (len (fields) > 0):
      description = fields [0]
    else:
      description = ''
    fields = re.findall(r'data-tag-name="([^"]*)"', s)
    tags = ''
    for i in fields:
      if (len (tags) > 0):
        tags = tags + ','
      tags = tags + i
    fields = re.findall(r'"url":"(https://img-fotki.yandex.ru/get/[^"]*orig)"', s)
    img_orig = fields [0]
    fields = re.findall(r'"latitude":([-0-9.]*),"longitude":([-0-9.]*)', s)
    if (len (fields) > 0):
      lat = fields [0] [0]
      lon = fields [0] [1]
    else:
      lat = ''
      lon = ''
    return description, tags, img_orig, lat, lon
  except Exception as e:
    print (e)
    print ('Press any key...')
    input ()
    return '', '', '', '', ''

def isPictureInList (link):
  for picture in pictures:
    if (picture ['link'] == link):
      return True
  return False

for root, dirs, files in os.walk('.'):
  for file in files:
    album_id = re.findall(r'Album ([0-9]*).txt', file)
    if (len (album_id) > 0):
      album_id = album_id [0]
      #print (album_id, file)
      album = {'id' : album_id, 'filename' : file}
      albums [album_id] = album

http = urllib3.PoolManager()
pictures_count = 0;

for i in albums:
  album = albums [i]
  #print (i, album)
  with open (album ['filename'], 'r' ) as f:
    s = f.read()
    fields = re.findall(r'װמעמדנאפטט ג אכüבמלו «<a href="([^"]*)">([^<]*)</a>»', s)
    album ['link'] = fields [0] [0]
    album ['title'] = fields [0] [1]
    fields = re.findall(r'<a href="([^"]*)"><img src="([^"]*)" title="([^"]*)" alt="([^"]*)" border="0"/></a>', s)
    album ['count'] = len(fields)
    print ('Got', album ['count'], 'pictures')
    albums [i] = album
    
    for j in fields:
      pictures_count = pictures_count + 1
      link = j [0]
      if isPictureInList (link):
        continue
      description, tags, img_orig, lat, lon = requestPictureDescription (http, link)
      picture = {'link': link, 'title': j [2], 'description': description, 'tags': tags, 'img_small': j [1], 'img_orig': img_orig, 'lat': lat, 'lon': lon, 'album': album ['title']}
      pictures.append (picture)
      print (pictures_count, picture, '\n')

# 2868

with open ('Albums.csv', 'w' ) as f:
  for i in sorted (albums.keys()):
    album = albums [i]
    print (i, album)
    f.write ("%s;%s;%s;%s;%s\n" % (album ['id'], album ['title'], album ['count'], album ['link'], album ['filename']))

with open ('Pictures.csv', 'w' ) as f:
  for i in pictures:
    picture = i
    print (picture)
    f.write ("%s;%s;%s;%s;%s;%s;%s;%s;%s\n" % (picture ['link'], picture ['title'], picture ['description'], picture ['tags'], picture ['img_small'], picture ['img_orig'], picture ['lat'], picture ['lon'], picture ['album']))

pictures_map = {}
for picture in pictures:
  link = picture ['link']
  if (link in pictures_map.keys()):
    print (link, picture ['title'], picture ['album'])
    print ('Press any key...')
    input ()
  pictures_map [link] = picture
