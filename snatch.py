#!/usr/bin/python3

import argparse
import json
import os
import os.path
import progressbar
import re
import requests
import subprocess


class RSnatcher(object):
    image_re = r'.*\.(jpeg|jpg|png)$'
    video_domains = ('gayforit.eu', 'gotgayporn.com', 'empflix.com',
                     'jizzhut.lua', 'keezmovies.com','manhub.com',
                     'pornhub.com', 'xnxx.com', 'xhamster.com', 'xtube.com',
                     'xvideos.com', 'youjizz.com')

    def __init__(self, user_agent, subdirs=False):
        self.user_agent = user_agent
        self.subdirs = subdirs
        self.image_regex = re.compile(self.image_re)
        self.video_regex = re.compile(
            '.*(' +
            '|'.join([re.escape(d) for d in self.video_domains]) +
            ').*')

    def download(self, url, title=None, length=None, user=None):
        filename = url.split('/')[-1]
        filename = filename.split('?')[0]
        if title:
            filename = title + '.' + filename.split('.')[-1]
        filename = os.path.basename(filename)

        if self.subdirs and user:
            dirname = os.path.basename(user)
            if not os.path.exists(dirname):
                os.mkdir(dirname)

            filename = os.path.join(dirname, filename)

        if os.path.exists(filename):
            print("{}: file already exists".format(filename))
            return

        r = requests.get(
            url,
            stream=True,
            headers={'User-Agent': self.user_agent})
        downloaded = 0.0
        chunk_size = 1024

        if not length and 'content-length' in r.headers:
            length = int(r.headers['content-length'])

        if length > 0:
            pbar = progressbar.ProgressBar(maxval=length)
            pbar.start()

        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    f.flush()

                    if length > 0:
                        downloaded += len(chunk)
                        pbar.update(downloaded)

        if length > 0:
            pbar.finish()

    def snatch(self, subreddits, limit=25):
        r = requests.get(
            'http://reddit.com/r/{subreddits}/hot.json?limit={limit}'.
            format(
                subreddits='+'.join(subreddits),
                limit=limit),
            headers={'User-Agent': self.user_agent})
        subs = r.json()['data']['children']
        for sub in subs:
            subreddit = sub['data']['subreddit']
            title = sub['data']['title']
            url = sub['data']['url']

            if 'author' in sub['data'] and len(sub['data']['author']) > 0:
                author = sub['data']['author']
            else:
                author = None


            if self.image_regex.match(url):
                print((subreddit, title, author, url))
                self.download(url, user=author)

            if self.video_regex.match(url):
                print((subreddit, title, author, url))

                quvid = subprocess.check_output(['quvi', url])
                media = json.loads(quvid.decode('utf-8'))
                self.download(
                    url=media['link'][0]['url'],
                    title=media['page_title'],
                    length=int(media['link'][0]['length_bytes']),
                    user=author)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="subreddit image and video grabber")
    parser.add_argument(
        '-l',
        '--limit',
        type=int,
        default=25,
        help="Maximum number of posts to parse.")
    parser.add_argument(
        '-s',
        '--subdirs',
        type=bool,
        default=False,
        action='store_true',
        help="Create subdirectories for posts by each user.")
    parser.add_argument('subreddits', nargs='*', metavar='subreddit')
    args = parser.parse_args()

    rs = RSnatcher("rsnatcher/0.1 (subreddit image and video grabber)", subdirs=args.subdirs)
    rs.snatch(args.subreddits)
