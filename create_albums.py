#!/usr/bin/python3

import flickrapi
import sys, os, datetime, re
import json
import time
import socket

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
# Get the list of albums from Flickr
#---------------------------
def list_albums ():
  try:
    response = flickr.photosets.getList(user_id=flickr_user_id)
  except flickrapi.exceptions.FlickrError as e:
    print (e)
    print ('Press Enter')
    input ()
    return
  if response ['stat'] == 'ok':
    for flickr_album in response ['photosets'] ['photoset']:
      flickr_album_title = flickr_album ['title'] ['_content']
      flickr_album_id = flickr_album ['id']
      print ('Got Flickr album "%s" id "%s"' % (flickr_album_title, flickr_album_id))    
  else:
    print ('Error requesting list of albums')

#---------------------------
# Create albums on Flickr
#---------------------------
def create_album(title, flickr_primary_photo_id):
  print ('Adding album "%s"' % (title))
  flickr_id = ''
  flickr_link = ''
  try:
    response = flickr.photosets.create (title=title, primary_photo_id=flickr_primary_photo_id)
  except flickrapi.exceptions.FlickrError as e:
    print (e)
    print ('Press Enter')
    input ()
    return flickr_id, flickr_link
  if response ['stat'] == 'ok':
    flickr_id = response ['photoset'] ['id']
    flickr_link = response ['photoset'] ['url']
    print ('Added album "%s", id "%s", link "%s"' % (title, flickr_id, flickr_link))
  else:
    print ('Error Adding album "%s"' % (title))
  return flickr_id, flickr_link

def callback(progress):
  print('\r%s' % (str (progress)), end='')

class FileWithCallback(object):
  def __init__(self, filename, callback):
    self.file = open(filename, 'rb')
    self.callback = callback
    # the following attributes and methods are required
    self.len = os.path.getsize(filename)
    self.fileno = self.file.fileno
    self.tell = self.file.tell
  
  def read(self, size):
    if self.callback:
      self.callback(self.tell() * 100 // self.len)
    return self.file.read(size)
  

#---------------------------
# Upload photo
#---------------------------
def upload_photo(filename, title, description, tags):
  tags = '"' + tags.replace(',', '" "') + '"'
  path = filename
  print ('Uploading photo %s, "%s", tags %s' % (path, title, tags))
  sent = False
  while not sent:
    try:
      response = flickr.upload (
        filename=path,
        fileobj=FileWithCallback(path, callback),
        title=title,
        description=description,
        tags=tags,
        format='rest')
      print ('Picture uploaded')
      sent = True
    except Exception as e:
      print (e)
      print ('Try again (Y/n)?')
      s = input ()
      if (s == 'n'):
        return ''
      
    
  response = response.decode()
  print (response)
  if (response.find('stat="ok"') > 0) :
    fields = re.findall(r'<photoid>([0-9]*)</photoid>', response)
    id_flickr = fields [0]
    return id_flickr
  else:
    print ('Wrong response')
    return ''
  

#---------------------------
# Add photo to album
#---------------------------
def add_photo_to_album(photo_id, album_id):
  print ('Adding photo %s to album %s' % (photo_id, album_id))
  try:
    response = flickr.photosets.addPhoto(photo_id=photo_id, photoset_id=album_id)
  except flickrapi.exceptions.FlickrError as e:
    print (e)
    print ('Press Enter')
    input ()
    return
  if response ['stat'] == 'ok':
    print ('Added photo %s to album %s' % (photo_id, album_id))
  else:
    print ('Error adding photo %s to album %s' % (photo_id, album_id))

#---------------------------
# Get link to photo
#---------------------------
def get_link_to_photo(photo_id):
  print ('Getting links to photo %s' % (photo_id))
  try:
    response = flickr.photos.getSizes(photo_id=photo_id)
  except flickrapi.exceptions.FlickrError as e:
    print (e)
    print ('Press Enter')
    input ()
    return ''
  if response ['stat'] == 'ok':
    sizes = response ['sizes'] ['size']
    img_tag = ''
    for size in sizes:
      img_tag = '<a data-flickr-embed="true" href="'
      img_tag = img_tag + re.findall (r'(https.*/[0-9]*/).*', size ['url']) [0]
      img_tag = img_tag + '"><img src="'
      img_tag = img_tag + size ['source']
      img_tag = img_tag + '" width="'
      img_tag = img_tag + str (size ['width'])
      img_tag = img_tag + '" height="'
      img_tag = img_tag + str (size ['height'])
      img_tag = img_tag + '"></a>'
      if (size ['label'] == 'Medium 800'):
        break
    print ('Got img tag %s' % (img_tag))
    return img_tag
  else:
    print ('Error getting links to photo %s' % (photo_id))
    return ''
  

path_orig = 'mnt'
dry_run = False

# Get the list of albums from file

albums = []
with open ('Albums.csv', 'r' ) as f:
  for s in f.read().splitlines():
    fields = s.split(';')
    title = fields [1]
    album = {
      'id': fields [0],
      'title': title,
      'count': fields [2],
      'link': fields [3],
      'filename': fields [4]}
    if (len (fields) > 5) :
      album ['flickr_id'] = fields [5]
      if (len (fields) > 6) :
        album ['flickr_link'] = fields [6]
      else:
        album ['flickr_link'] = ''
    else:
      album ['flickr_id'] = ''
      album ['flickr_link'] = ''
    albums.append (album)
    print (album)
  

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
      'album': fields [9]}
    if (len (fields) > 10):
      picture ['flickr_id'] = fields [10]
      if (len (fields) > 11):
        picture ['flickr_img_tag'] = fields [11]
      else:
        picture ['flickr_img_tag'] = ''
    else:
      picture ['flickr_id'] = ''
      picture ['flickr_img_tag'] = ''
    pictures.append (picture)
  

print ('Read %d pictures' % (len (pictures)))

flickr_albums = []
flickr_pictures = []

album_count = 1

pictures_uploaded = 0
pictures_uploaded_max = 50

skip_remaining_pictures = False

for album in albums:
  #print ('Upload album %d of %d "%s" (y/N)?' % (album_count, len (albums), album ['title']))
  #s = input ()
  s = 'y'
  if (s == 'y'):
    flickr_pictures_in_album = []
    
    # Upload pictures
    for picture in pictures:
      if picture ['album'] == album ['title']:
        if (picture ['flickr_id'] == ''):
          if not skip_remaining_pictures and (pictures_uploaded > pictures_uploaded_max):
            #print ('Added %2d pictures. Keep adding (y/N)?' % (pictures_uploaded))
            #s = input ()
            s = 'n'
            if not (s == 'y'):
              skip_remaining_pictures = True
          if skip_remaining_pictures:
            print ('Skipping picture %2d "%s"' % (len (flickr_pictures_in_album), picture ['title']))
            flickr_pictures_in_album.append (picture)
            continue
          print ('Adding picture %2d (%d of %d) "%s"' % (len (flickr_pictures_in_album), pictures_uploaded, pictures_uploaded_max, picture ['title']))
          if (len (picture ['img_orig']) > 0):
            filename = path_orig + '/' + picture ['img_orig'].split('/')[-1]
            if not dry_run:
              flickr_id = upload_photo(filename, picture ['title'], picture ['description'], picture ['tags'])
              time.sleep (1)
            else:
              flickr_id = ''
              print ('upload_photo(%s, %s, %s)' % (filename, picture ['title'], picture ['tags']))
            picture ['flickr_id'] = flickr_id
            pictures_uploaded = pictures_uploaded + 1
          else:
            print ('File for picture "%s" does not exist' % (picture ['title']))
            print ('Press Enter')
            input ()
        else:
          print ('Picture "%s" already exists' % (picture ['title']))
        flickr_pictures_in_album.append (picture)
      
    # Create album
    if ((album ['flickr_id'] == '') and (not flickr_pictures_in_album [0] ['flickr_id'] == '')):
      if not dry_run:
        flickr_id, flickr_link = create_album(album ['title'], flickr_pictures_in_album [0] ['flickr_id'])
      else:
        flickr_id = ''
        flickr_link = ''
        print ('create_album(%s, %s)' % (album ['title'], flickr_pictures_in_album [0] ['flickr_id']))
      album ['flickr_id'] = flickr_id
      album ['flickr_link'] = flickr_link
    else:
      print ('Album "%s" already exists' % (album ['title']))
    
    # Add pictures to albums and get links
    for i, picture in enumerate(flickr_pictures_in_album):
      print ('Adding picture %2d "%s" to album and getting link' % (i, picture ['title']))
      if not (picture ['flickr_id'] == ''):
        if (picture ['flickr_img_tag'] == ''):
          if not dry_run:
            add_photo_to_album(picture ['flickr_id'], album ['flickr_id'])
            img_tag = get_link_to_photo(picture ['flickr_id'])
          else:
            print ('add_photo_to_album(%s, %s)' % (picture ['flickr_id'], album ['flickr_id']))
            img_tag = ''
            print ('get_link_to_photo(%s)' % (picture ['flickr_id']))
          picture ['flickr_img_tag'] = img_tag
        else:
          print ('Picture "%s" already has img tag' % (picture ['title']))
          #print ('Press Enter')
          #input ()
      else:
        print ('Picture "%s" has no Flickr ID' % (picture ['title']))
      flickr_pictures.append (picture)
    
    print ('Added %d pictures from album "%s"' % (len (flickr_pictures_in_album), album ['title']))
  else:
    print ('Skipping album "%s"' % (album ['title']))
    pictures_count = 0
    for picture in pictures:
      if picture ['album'] == album ['title']:
        flickr_pictures.append (picture)
        pictures_count = pictures_count + 1
    print ('Added %d pictures from album "%s"' % (pictures_count, album ['title']))
  print ('Added album "%s"' % (album ['title']))
  flickr_albums.append (album)
  album_count = album_count + 1

# Write albums to file

with open ('Albums_flickr.csv', 'w') as f:
  for album in flickr_albums:
    print (album)
    f.write ("%s;%s;%s;%s;%s;%s;%s\n" % (
      album ['id'],
      album ['title'],
      album ['count'],
      album ['link'],
      album ['filename'],
      album ['flickr_id'],
      album ['flickr_link']))
    
  
#Write pictures to file

with open ('Pictures_flickr.csv', 'w') as f:
  for picture in flickr_pictures:
    #print (picture)
    f.write ("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n" % (
      picture ['link'],
      picture ['title'],
      picture ['description'],
      picture ['tags'],
      picture ['img_small'],
      picture ['img_orig'],
      picture ['date_uploaded'],
      picture ['lat'],
      picture ['lon'],
      picture ['album'],
      picture ['flickr_id'],
      picture ['flickr_img_tag']))
    
  
os.rename ('Albums_flickr.csv', 'Albums.csv')
os.rename ('Pictures_flickr.csv', 'Pictures.csv')