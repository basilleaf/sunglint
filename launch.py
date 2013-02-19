import boto, simplejson, urllib2, requests
from random import randint
from tumblpy import *

published_url = "https://s3.amazonaws.com/sunglints_oy_ya__/published.txt"
blog_url = 'sunglint.tumblr.com'
post_tags = 'sunglint,NASA,Earth'

# AWS creds
aws_access_key_id = os.environ['aws_access_key_id'])
aws_secret_access_key = os.environ['aws_secret_access_key'])
bucket_name = os.environ['bucket_name'])

# Tumblr creds
app_key = os.environ['app_key'])
app_secret = os.environ['app_secret'])
oauth_token = os.environ['oauth_token'])
oauth_token_secret = os.environ['oauth_token_secret'])


class ScienceData:

	def get_dataset(self):
		# fetch the dataset, it's in a public google spreadsheet:
		response = requests.get('https://docs.google.com/spreadsheet/ccc?key=0AtHxCskz4p33dEhBZ3Jpc1VoTmIzQ0V3ODJ5eVdzcUE&output=csv')
		assert response.status_code == 200, 'Wrong status code'
		all_rows = [r.split(',') for r in response.content.split("\n")]
		return all_rows

	def total_image_count(self):
		all_rows = self.get_dataset()
		total_image_count = sum(1 for img in all_rows if img[all_rows[0].index('Online Source')].upper().find('.JPG') > -1) # some rows contain non-images so checking for that
		return total_image_count

class BlogPosts:

	def get_previous(self):
		# returns the list previously published images from public url on s3
		response = urllib2.urlopen(published_url)
		published = [p.rstrip() for p in response.readlines()]

		# are we at the end? have they all been published? 
		if len(published) == ScienceData().total_image_count: 
			published = [] # every post has been published, starting over from scratch
		
		return published

	def get_most_recent(self):
		return "most recent time"


class Image: 

	# pick an image at random that hasn't been picked before
	def random(self): 
		published = BlogPosts().get_previous()
		all_rows = ScienceData().get_dataset()
		column_titles = all_rows[0]
		total_image_count = ScienceData().total_image_count()
		random_row = all_rows[randint(1,len(all_rows)-1)] 
		random_image = dict(zip(column_titles, random_row)) # make a nice json version - http://stackoverflow.com/questions/209840/map-two-lists-into-a-dictionary-in-python
		url = random_image['Online Source']
		if (url in published) | ((url.upper().find('.JPG') < 0) & (url.upper().find('.JPEG') < 0)): # this is already published or it's not an image
			return self.random() # game over try again
		return random_image


	# post to tumblr
	def post_to_tumblr(self, random_image):
		
		print random_image
		t = Tumblpy(app_key = app_key,
		        app_secret = app_secret,
		        oauth_token = oauth_token,
		        oauth_token_secret=oauth_token_secret)
		title = random_image['Title'].title()
		description = random_image['Abstract'].title()
		credit = random_image['NASA Center']
		link = random_image['NTRS Link']
		date = random_image['Publication Year']
		img_url = random_image['Online Source']
		acc_no = random_image['Accession Number']
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
		return post['id'] if post['id'] else False


	def log_as_published(self,image_url):
		# update the published log
		published = BlogPosts().get_previous()
		published.append(image_url)
		s3 = boto.connect_s3(aws_access_key_id,aws_secret_access_key)
		bucket = s3.create_bucket(bucket_name)
		key_name = published_url.split('/').pop()
		bucket.delete_key(key_name)
		key = bucket.new_key(key_name)
		key.set_contents_from_string("\n".join(published))
		key.set_acl('public-read')

try:
	img = Image()
	random_image = img.random()
	img.post_to_tumblr(random_image)
	img.log_as_published(random_image['Online Source'])
except:
	pass


