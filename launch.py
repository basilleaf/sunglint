import simplejson
from random import randint
from tumblpy import *
from secrets import *
import urllib2
import boto
import requests

published_url = "https://s3.amazonaws.com/sunglints_oy_ya__/published.txt"
blog_url = 'sunglint.tumblr.com'
post_tags = 'sunglint,NASA,Earth'

# fetch the data from the google spreadsheet
response = requests.get('https://docs.google.com/spreadsheet/ccc?key=0AtHxCskz4p33dEhBZ3Jpc1VoTmIzQ0V3ODJ5eVdzcUE&output=csv')
assert response.status_code == 200, 'Wrong status code'
all_rows = [r.split(',') for r in response.content.split("\n")]
column_titles = all_rows[0]
total_image_count = sum(1 for img in all_rows if img[all_rows[0].index('Online Source')].upper().find('.JPG') > -1) # some rows contain non-images

# fetch the previously published images from public url on s3
response = urllib2.urlopen(published_url)
published = [p.rstrip() for p in response.readlines()]

# are we at the end? have they all been published? 
if len(published) == total_image_count: 
	published = [] # every post has been published, starting over from scratch

# pick a random image we haven't published already
def pick_one(): 
	row = all_rows[randint(1,len(all_rows)-1)] # pick a random row
	our_pick = dict(zip(column_titles, row)) # make a nice json version - http://stackoverflow.com/questions/209840/map-two-lists-into-a-dictionary-in-python
	url = our_pick['Online Source']
	if (url in published) | (url.upper().find('.JPG') < 0): # this is already published or it is not an image
		return pick_one()
	return our_pick

# post to tumblr
def post_to_tumblr():
	our_pick = pick_one()
	print our_pick
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
	acc_no = our_pick['Accession Number']
	caption = """
			<h2>{0}</h2>
			<p><b>{1}</b></p>
			<p>
				{2}<br>
				{3} <br>
				{4}<br>via <a href = "{5}">ntrs.nasa.gov</a>
			"""
	caption = caption.format(title,date,description,credit,acc_no,link).strip()
	img = urllib2.urlopen(img_url)
	post = t.post('post', blog_url=blog_url, params={'type':'photo', 'caption': str(caption), 'data': img, 'link':str(img_url), 'tags':str(post_tags)})

	# update the published log
	if post['id']:
		published.append(img_url)
		s3 = boto.connect_s3(aws_access_key_id,aws_secret_access_key)
		bucket = s3.create_bucket(bucket_name)
		key_name = published_url.split('/').pop()
		bucket.delete_key(key_name)
		key = bucket.new_key(key_name)
		key.set_contents_from_string("\n".join(published))
		key.set_acl('public-read')

post_to_tumblr()

