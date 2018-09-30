#!/usr/bin/env python3.6

"""
List all links on all pages of a geeks for geeks tag.

By default, a JSON is generated, which can be edited by hand.

Usage: list_links [options] <URL>
"""

import sys
import json

from collections import OrderedDict

import requests
import pyquery

from bs4 import BeautifulSoup

ROOT_JSON = "JSON/"

URL = sys.argv[1].rstrip('/')
TAG = URL.split('/')[-1].title()

FNAME = ROOT_JSON + f"{TAG}.json"


def abort(msg):
    print(msg, file=sys.stderr)
    exit(1)


def print_titles(content):
    for title in content.find_all('strong'):
        print(title.text.strip())


def save_links(content, filename):
    # DS/Algo
    # url = "http://www.geeksforgeeks.org/data-structures/"
    # url = "http://www.geeksforgeeks.org/fundamentals-of-algorithms/"
    # soup = BeautifulSoup(requests.get(url).text)
    # content = soup.find('div', class_="entry-content")

    links = []

    for ul in content.find_all('ul')[1:]:
        topic = OrderedDict()

        for link in ul.find_all('a'):
            if 'geeksquiz' not in link.get('href'):
                topic[link.text.strip()] = link['href'].strip()

        if topic:
            links.append(topic)

    with open(filename, "w") as out:
        json.dump(links, out, indent=4)


def fetch_post_links(urls, filename=None, combined=False):
    if type(urls) is str:
        urls = [urls]

    links = OrderedDict()

    for url in urls:
        soup = BeautifulSoup(requests.get(url).text, "lxml")
        content = soup.find('div', id="content")

        topic = OrderedDict()
        for ques in content.find_all("h2", class_="entry-title"):
            link = ques.find("a")
            topic[link.text.strip()] = link['href'].strip()

        if combined:
            links.update(topic)
        else:
            topic_name = url.split('/')[-2].title()
            links[topic_name] = topic

    if not filename:
        print(json.dumps(links, indent=4))
    else:
        with open(filename, "w") as out:
            json.dump(links, out, indent=4)


def unique_links(filename):
    with open(filename) as inp:
        data = json.load(inp, object_pairs_hook=OrderedDict)

    uniq = OrderedDict()
    for title, link in data.items():
        if link not in uniq.values():
            uniq[title] = link

    with open(filename, "w") as out:
        json.dump(uniq, out, indent=4)


def list_pages(root_url):

    links = []
    num_pages = 0

    try:
        pq = pyquery.PyQuery(url=root_url)
    except:  # noqa
        abort("URL doesn't exist.")

    if pq('.pages'):
        num_pages = int(pq('.pages')[0].text.split()[-1])

    if not num_pages:
        abort("No pages!")

    for page in range(1, num_pages + 1):
        links.append(URL + f"/page/{page}/")

    return links


if __name__ == '__main__':
    unique_links(FNAME)
    fetch_post_links(list_pages(URL), FNAME, combined=True)
