import gspread
import simplejson
from random import randint
from tumblpy import *
from secrets import *
import urllib2

published_file = SCRIPT_PATH + 'published.txt'

# fetch the google spreadsheet - https://docs.google.com/spreadsheet/ccc?key=0AtHxCskz4p33dEhBZ3Jpc1VoTmIzQ0V3ODJ5eVdzcUE
key="0AtHxCskz4p33dEhBZ3Jpc1VoTmIzQ0V3ODJ5eVdzcUE" # this is public
gc = gspread.login(GOOG_USER,GOOG_PASSWORD)
sht1 = gc.open_by_key(key)
all_rows = sht1.sheet1.get_all_values()
total_image_count = sum(1 for img in all_rows if img[all_rows[0].index('Online Source')].upper().find('.JPG') > -1) # some rows contain non-images
column_titles = all_rows[0]

# fetch the previously published images
published = [p.rstrip() for p in open(published_file).readlines()]
if len(published) == total_image_count: 
	published = [] # every post has been published, starting over from scratch

def pick_one(): 
	row = all_rows[randint(1,len(all_rows)-1)] 
	our_pick = dict(zip(column_titles, row)) # http://stackoverflow.com/questions/209840/map-two-lists-into-a-dictionary-in-python
	url = our_pick['Online Source']
	if (url in published) | (url.upper().find('.JPG') < 0): # this is already published or not an image
		return pick_one()
	return our_pick

# post to tumblr
our_pick = pick_one()
blog_url = 'sunglint.tumblr.com'
t = Tumblpy(app_key = app_key,
        app_secret = app_secret,
        oauth_token = oauth_token,
        oauth_token_secret=oauth_token_secret)
title = our_pick['Title'].title()
description = our_pick['Abstract'].title()
credit = our_pick['NASA Center']
link = our_pick['NTRS Link']
date = our_pick['Publication Year']
img_url = our_pick['Online Source']
caption = '<h2>' + title + '</h2><p><b>' + date + '</b></p><p>' + description + '</p>' + credit + '<p>Visit the <a href = "' + link + '">ntrs.nasa.gov page</a> for more info and image sizes.'
img = urllib2.urlopen(img_url)
post = t.post('post', blog_url=blog_url, params={'type':'photo', 'caption': caption, 'data': img, 'link':img_url})

# update the published log
if post['id']:
	published.append(img_url)
	f = open(published_file, 'w')
	simplejson.dump(published, f)
	f.close()

