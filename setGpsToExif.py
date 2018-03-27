#!/usr/bin/python3

import sys, os, datetime, re
import os.path

pictures = []
with open ('Pictures.csv', 'r' ) as f:
  for s in f.read().splitlines():
    fields = s.split(';')
    picture = {
      'link': fields [0],
      'title': fields [1],
      'description': fields [2],
      'tags': fields [3],
      'img_small': fields [4],
      'img_orig': fields [5],
      'date_uploaded': fields [6],
      'lat': fields [7],
      'lon': fields [8],
      'album': fields [9]}
    pictures.append (picture)

# https://stackoverflow.com/questions/89228/calling-an-external-command-in-python
# https://stackoverflow.com/questions/41849691/how-to-add-gps-latitude-and-longitude-using-exiftool-in-mac-how-to-edit-meta-da
# https://scribblesandsnaps.com/2011/11/23/easy-geotagging-with-exiftool/

def setGps (path, link, lat, lon):
  filename = path + '/' + link.split('/')[-1]
  if os.path.isfile(filename) == True:
    s = os.popen('exiftool -l ' + filename + ' | grep -c Latitude').read().splitlines()
    if (s [0] != '0'):
      print ('Coordinates exist for', filename)
    else:
      print ('Setting coordinates for', filename)
      
      #exiftool -GPSLongitudeRef=E -GPSLongitude=139.7513889 -GPSLatitudeRef=N -GPSLatitude=35.685
      line = 'exiftool -GPSLongitudeRef='
      if (float (lon) >= 0):
        line = line + 'E'
      else:
        lon = lon [1:]
        line = line + 'W'
      line = line + ' -GPSLongitude='
      line = line + lon
      line = line + ' -GPSLatitudeRef='
      if (float (lat) >= 0):
        line = line + 'N'
      else:
        lat = lat [1:]
        line = line + 'S'
      line = line + ' -GPSLatitude='
      line = line + lat
      line = line + ' -overwrite_original '
      line = line + filename
      
      print (line)
      #s = ['    1 image files updated']
      s = os.popen(line).read().splitlines()
      print (s)
      if (s [0] != '    1 image files updated'):
        print ('Press any key...')
        input ()
      
    
  else:
    print ('Skipping', link, ', file', filename, 'does not exist')
    print ('Press any key...')
    input ()

path_orig = 'mnt/orig'

pictures_count = 0

for picture in pictures:
  pictures_count = pictures_count + 1
  print ('Picture', pictures_count)
  img_orig = picture ['img_orig']
  lat = picture ['lat']
  lon = picture ['lon']
  if ((lat != '') and (lon != '')):
    setGps (path_orig, img_orig, lat, lon)
  else:
    if ((lat != '') or (lon != '')):
      print ('Coordinates are incomplete!')
      print ('Press any key...')
      input ()
    else:
      print ('No coordinates')
  
