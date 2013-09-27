#!/usr/bin/python2

import os.path
import praw
import progressbar
import quvi
import re
import requests
import subprocess


user_agent = "rsnatcher/0.1 (subreddit image and video URL grabber)"

def download(url, title=None):
    filename = url.split('/')[-1]
    filename = filename.split('?')[0]
    if title:
        filename = title + filename.split('.')[-1]
    filename = os.path.basename(filename)

    r = requests.get(url, stream=True, headers={'User-Agent': user_agent})
    downloaded = 0.0
    chunk_size = 1024

    if 'content-length' in r.headers:
        total_size = int(r.headers['content-length'])
    else:
        total_size = 0

    if total_size > 0:
        pbar = progressbar.ProgressBar(maxval=total_size)
        pbar.start()

    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                f.flush()

                if total_size > 0:
                    downloaded += len(chunk)
                    pbar.update(downloaded)

    if total_size > 0:
        pbar.finish()

r = praw.Reddit(user_agent)
q = quvi.Quvi()

#image_regex = re.compile(r'.*\.(gif|jpeg|jpg|png)$')
image_regex = re.compile(r'.*\.(jpeg|jpg|png)$')
video_regex = re.compile(r'.*(pornhub\.com|xnxx\.com|xhamster\.com|xtube\.com|xvideos\.com).*')

#subreddits = ['gaymersgonewild', 'gaybrosgonewild', 'penis']
subreddits = ['selfservice']
subs = r.get_subreddit('+'.join(subreddits)).get_hot(limit=25)
for sub in subs:
    #print(sub.subreddit.display_name, sub.title, sub.url)

    """if image_regex.match(sub.url):
        print(sub.subreddit.display_name, sub.author.name, sub.title, sub.url)
        download(sub.url)"""

    if video_regex.match(sub.url):
        print(sub.subreddit.display_name, sub.author.name, sub.title, sub.url)
        q.parse(sub.url)
        video = q.get_properties()
        download(video['mediaurl'])

#for subreddit in subreddits:
