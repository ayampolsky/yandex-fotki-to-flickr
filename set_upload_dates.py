#!/usr/bin/python3

import flickrapi
import sys, os, datetime, re
import json
import time
import socket
from operator import itemgetter
import datetime

with open ('api_key.txt', 'r' ) as f:
  s = f.read().splitlines()

api_key = s [0]
api_secret = s [1]
flickr_user_id = s [2]

socket.setdefaulttimeout(10)

flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')

print('Step 1: authenticate')

# Only do this if we don't have a valid token already
if not flickr.token_valid(perms='write'):
  
  # Get a request token
  flickr.get_request_token(oauth_callback='oob')
  
  # Open a browser at the authentication URL. Do this however
  # you want, as long as the user visits that URL.
  authorize_url = flickr.auth_url(perms='write')
  print ('Open %s in browser' % authorize_url)
  
  # Get the verifier code from the user. Do this however you
  # want, as long as the user gives the application the code.
  verifier = str(input('Verifier code: '))
  
  # Trade the request token for an access token
  flickr.get_access_token(verifier)

#---------------------------
# Set date posted to photo
#---------------------------
def set_date_posted(photo_id, date_posted):
  print ('Setting date posted %s to photo %s' % (date_posted, photo_id))
  done = False
  while not done:
    try:
      response = flickr.photos.setDates(photo_id=photo_id, date_posted=date_posted)
    except flickrapi.exceptions.FlickrError as e:
      print (e)
      print ('Try again (Y/n)?')
      s = input ()
      if (s == 'n'):
        return
      
    if response ['stat'] == 'ok':
      print ('Set date posted %s to photo %s' % (date_posted, photo_id))
      done = True
    else:
      print ('Error setting date posted %s to photo %s' % (date_posted, photo_id))
    
  

dry_run = False

# Get the list of pictures from file

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
      'album': fields [9],
      'flickr_id': fields [10],
      'flickr_img_tag': fields [11]}
    pictures.append (picture)
  

print ('Read %d pictures' % (len (pictures)))

# https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary-in-python

pictures_sorted = sorted(pictures, key=itemgetter('date_uploaded'))

upload_date_start = int (datetime.datetime.now().strftime('%s')) - len (pictures)

# Set upload date to pictures

for i, picture in enumerate(pictures_sorted):
  flickr_id = picture['flickr_id']
  date_uploaded = upload_date_start + i
  print ('Setting upload date %d for picture %4d "%s"' % (date_uploaded, i + 1, picture ['title']))
  if not dry_run:
    set_date_posted (flickr_id, date_uploaded)
  else:
    print ('set_date_posted (%s, %d)' % (flickr_id, date_uploaded))
  if ((i > 0) and ((i % 3600) == 0)):
    print ('Waiting for 3600 s. Please wait.')
    time.sleep (3600)
  
