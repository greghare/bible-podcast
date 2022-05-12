#!/usr/bin/env python

import json
import sys
import requests
import shutil
import os
import glob
from feedgen.feed import FeedGenerator
from mutagen.mp3 import MP3
import configparser
import ftplib
from datetime import datetime
import pytz

DOMAIN = 'https://greghare.me/bible-podcast'
LOCAL_MEDIA_FOLDER = 'media'
REMOTE_MEDIA_FOLDER = 'media'
FEED_FILENAME = 'feed.rss'

# Get FTP credentials
configParser = configparser.RawConfigParser()   
configFilePath = 'main.config'
configParser.read(configFilePath)
FTP_SERVER = configParser.get('ftp-creds', 'server') 
FTP_USERID = configParser.get('ftp-creds', 'user_id')
FTP_PASSWD = configParser.get('ftp-creds', 'password')

API_KEY = configParser.get('esv-api', 'api_key')
API_URL = configParser.get('esv-api', 'api_url')

# Login to FTP (FTP user is configured to use only directory
# for storing podcast data)
ftp = ftplib.FTP(FTP_SERVER)
ftp.login(FTP_USERID, FTP_PASSWD)
ftp.cwd(".")

pc = FeedGenerator()
pc.load_extension('podcast')

pc.podcast.itunes_category('Education')
pc.podcast.itunes_owner('Greg Hare', 'greg@greghare.me')
pc.podcast.itunes_image('https://pngimg.com/uploads/bible/bible_PNG22.png')

pc.title('Bible in a Year')
pc.author( {'name':'Greg Hare'} )
pc.link( href='https://greghare.me', rel='alternate' )
pc.subtitle('A podcast feed updated daily with a new reading from the ESV Bible')
pc.link( href='https://greghare.me/bible-podcast/feed.rss', rel='self' )
pc.language('en')

# Get current year
curYear = datetime.now().strftime("%Y")
local_tz = 'America/New_York'

def download_passage(passage, filepath):

    # query configuration
    params = { 'q': passage }
    headers = { 'Authorization': 'Token %s' % API_KEY }

    # request passage
    response = requests.get(API_URL, params=params, headers=headers, stream=True)
    
    # save passage as mp3
    with open(filepath, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

    print('Added "'+filepath+'" successfully')

    return filepath

def add_passage(passage, day):

    # Download audio passage
    filepath = LOCAL_MEDIA_FOLDER+'/'+passage+'.mp3'
    download_passage(passage, filepath)
    
    # Get audio length in bytes
    bytes = os.path.getsize(filepath)
    bytes_unicode = str(bytes).encode("utf-8").decode("utf-8")

    # Get date for entry
    entryDate = pytz.timezone(local_tz).localize(datetime.strptime(day + " " + curYear, '%B %d %Y')) # convert day to date object
    #entryDate = entryDate.strftime('%a, %d %b %Y 00:00:00 EST') # format date

    # Add entry to podcast feed
    pe = pc.add_entry()
    pe.id(filepath)
    pe.title(passage)
    pe.description('Listen to ' + passage)
    pe.enclosure(DOMAIN + "/" + filepath, bytes_unicode, 'audio/mpeg')
    pe.pubDate(entryDate)

    # Change directory to script install path
    install_path = os.getcwd()
    os.chdir(install_path)

    # Upload audio file to remote media directory
    audio_file = open(filepath, 'r')
    filename = os.path.basename(filepath)
    ftp.storbinary("STOR " + filename, open(filepath, 'rb'))
    audio_file.close()

# Delete MP3 files in remote media folder
def delete_server_files():
    ftp.cwd(REMOTE_MEDIA_FOLDER)
    files = ftp.nlst()
    for f in files:
        if f != '.' and f != '..' and ".mp3" in f:
            ftp.delete(f)
    ftp.cwd("..")

def build_feed():

    # Change FTP directory to REMOTE_MEDIA_FOLDER
    ftp.cwd(REMOTE_MEDIA_FOLDER)

    # Clean local media folder
    files = glob.glob(LOCAL_MEDIA_FOLDER + '/*')
    for f in files:
        os.remove(f)    

    # Open the reading plan
    with open('reading_plan.json') as data_file:    
        reading_plan = json.load(data_file)

    # Get the reading plan key for today
    curMonth = datetime.now().strftime("%B")
    curDay = str(datetime.now().day)
    today = curMonth + " " + curDay

    # Setup index and reading plan lookup
    rp_indexer = list(reading_plan)
    rp_lookup = list(reading_plan.values())

    # Get today's verse count and index
    verse_count = reading_plan[today]["verse_count"]
    day = rp_indexer.index(today)

    # Add readings until just under 500 verses
    while verse_count <= 500:

        day_string = rp_indexer[day]

        # Add reading
        reading = str(rp_lookup[day]["reading"])
        add_passage(reading, day_string)        
        
        # TODO: Fix index out of bounds for early January
        day -= 1 # look back one day 
        verse_count += rp_lookup[day]["verse_count"]

    # Change FTP directory back to root
    ftp.cwd("..")

def upload_feed():
    
    pc.rss_file(FEED_FILENAME)

    feed_file = open(FEED_FILENAME, 'r')
    filename = os.path.basename(FEED_FILENAME)
    ftp.storbinary("STOR " + FEED_FILENAME, open(FEED_FILENAME, 'rb'))
    feed_file.close()


if __name__ == '__main__':
    delete_server_files()
    build_feed()
    upload_feed()