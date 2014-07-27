#-*- coding: utf-8 -*-
# ssh.alfredworkflow, v1.1
# www.oldcai.com 2014

import alfred
import json
import re

from os import path, walk
from time import time

_MAX_RESULTS=36


class Hosts(object):
    def __init__(self, original, user=None):
        self.original = original
        self.hosts = {original: ['input']}
        self.user = user

    def add(self, host, source):
        if host in self.hosts:
            self.hosts[host].append(source)
        else:
            self.hosts[host] = [source]

    def update(self, _list):
        if not _list:
            return
        (hosts, source) = _list
        for host in hosts:
            self.add(host, source)

    def item(self, host, source):
        _arg = self.user and '@'.join([self.user, host]) or host
        _uri = 'Key: %s' % _arg
        _sub = 'Copy %s.pub (source: %s)' % (_uri, ', '.join(source))
        return alfred.Item(
            attributes={'uid': _uri, 'arg': _arg, 'autocomplete': _arg},
            title=_uri, subtitle=_sub, icon='icon.png'
        )

    def xml(self, _filter=(lambda x: True), maxresults=_MAX_RESULTS):
        items = [self.item(host=self.original, source=self.hosts[self.original])]
        for (host, source) in (
            (x, y) for (x, y) in self.hosts.iteritems()
            if ((x != self.original) and _filter(x))
        ):
            items.append(self.item(host, source))
        return alfred.xml(items, maxresults=maxresults)

def fetch_ssh_keys(_path, alias='~/.ssh/'):
    master = path.expanduser(_path)
    if not path.isdir(master):
        return
    cache = path.join(alfred.work(volatile=True), 'ssh_keys.1.json')
    if path.isfile(cache) and path.getmtime(cache) > path.getmtime(master):
        return (json.load(open(cache, 'r')), alias)
    results = set()
    for subdir, dirs, files in walk(path.expanduser(_path)):
        for filename in files:
            if filename.endswith(".pub"):
                results.add(filename[:-4])
    with open("1.log", "a") as f:
        f.write(path.expanduser(_path) + str(results))
    json.dump(list(results), open(cache, 'w'))
    return (results, alias)


def complete(query, maxresults=_MAX_RESULTS):
    if '@' in query:
        (user, host) = query.split('@', 1)
    else:
        (user, host) = (None, query)

    host_chars = (('\\.' if x is '.' else x) for x in list(host))
    pattern = re.compile('.*?\b?'.join(host_chars), flags=re.IGNORECASE)

    hosts = Hosts(original=host, user=user)
    hosts.update(fetch_ssh_keys('~/.ssh/'))

    return hosts.xml(pattern.search, maxresults=maxresults)

