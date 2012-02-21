#!/usr/bin/python

# This file is provided as a courtesy and comes with absolutely no warranty of
# any kind.  It is provided as-is.  Please read it (and understand it) before
# running it.

# If you end up using this, I'd love to know.  My email address is:
# ryan@gibsonandlily.com
# my website is: http://thingist.com
# Distributed under MIT license.  Ryan McDermott, 2011

import urllib
import urllib2
import simplejson
import cgi
import urlparse
import re

#get the cgi parameters
form = cgi.FieldStorage()
code = form.getvalue("code","")

#set up your facebook API credentials here.  Get these at developers.facebook.com
#do not share these.  They're not public.
redirect_uri = 				#the full path to this script.
					#example:
					#http://thingist.com/photo_libre/export-photos.cgi
client_id = ""				#facebook calls this application_id
client_secret = ""			#facebook calls this application_secret

def auth_facebook():
        args = {} 
        args["redirect_uri"] = redirect_uri 
        args["client_id"] = client_id
        args["client_secret"] = client_secret
        args["code"] = code


	#we take the code that facebook gave back to us, and exchange it for
	#an access token -- signed with our API creds
        data = urllib.urlencode(args)
        url = "https://graph.facebook.com/oauth/access_token"
        request = urllib2.Request(url, data)
        response = urllib2.urlopen(request)
        page = response.read()
        page_parms = urlparse.parse_qs(page)
        access_token = page_parms["access_token"]
        token = access_token[0]
	return(token)


def get_facebook_albums(facebook_token):
	req = urllib.urlopen("https://graph.facebook.com/%s/albums?access_token=%s" % (facebook_uid,facebook_token))
	data = req.read()
	json = simplejson.loads(data)
	albums = {} 
	for item in json['data']:
		albums[item['name']] = item['id']
	return(albums)

def get_facebook_uid(facebook_token):
	req = urllib.urlopen("https://graph.facebook.com/me?access_token=%s" % (facebook_token))
	data = req.read()
	user_info = simplejson.loads(data)
	facebook_uid = user_info["id"]
	return(facebook_uid)



if __name__ == "__main__":
	#if the code has a length, meaning we got one in the URL
	if len(code) > 0:
		facebook_token = auth_facebook()
		facebook_uid = get_facebook_uid(facebook_token)
		facebook_albums = get_facebook_albums(facebook_token)
		#finally, set up a header
		print "content-type:application/vnd.ms-excel"
		print "content-disposition: attachment; filename=facebook_photos.csv"
		print

		for album in facebook_albums:
			id = facebook_albums[album]
			album_title = str(album)
			req = urllib.urlopen("https://graph.facebook.com/%s/photos?access_token=%s" % (id,facebook_token))
			data = req.read()
			album = simplejson.loads(data)
			for item in album['data']:
				if item.has_key("name"):
					url = item['source']
					photo_title = item['name']
					photo_title = re.sub("\"","&quot;",photo_title)
					album_title = re.sub("\"","&quot;",album_title)
					print "\"%s\",\"%s\",\"%s\"\n" % (album_title,photo_title,url),

	#otherwise, call down to facebook and ask for one
	else:
		print "content-type:text/html"
		print
		print """
		<html>
		This tool brought to you by <a href='http://thingist.com/'>Thingist</a><br />
		<br />
		<a href="https://graph.facebook.com/oauth/authorize?client_id=%s&redirect_uri=%s&scope=user_photos">Export your facebook photos</a> <br />(This doesn't get stored)
		""" % (client_id,redirect_uri)
