from common import *

import lz4.block

import json
import os.path


def load_tabs(input_dir):
    path = os.path.join(input_dir, 'sessionstore-backups', 'recovery.jsonlz4')
    comp_data = open(path, 'rb').read()
    assert comp_data[:8] == b'mozLz40\0'
    data = lz4.block.decompress(comp_data[8:])
    tabs = [ ]
    for win in json.loads(data)['windows']:
        tabs += [ Tab(tab) for tab in win['tabs'] ]
    return tabs

def save_tabs(input_dir = '.', output_dir = '.', tabs = None):
    if tabs is None: tabs = load_tabs(input_dir)
    f = open(os.path.join(output_dir, 'tabs.csv'), 'w')
    f.write(Tab.title + '\n')
    for tab in sort_tabs(tabs):
        f.write(str(tab) + '\n')
    f.close()

def sort_tabs(tabs):
    dict_ = { }
    for tab in tabs:
        if tab.url not in dict_ or tab.access_time > dict_[tab.url].access_time:
            dict_[tab.url] = tab
    return sorted(dict_.values(), key = lambda tab: tab.access_time)


class Tab:
    def __init__(self, data):
        self.title = data['entries'][-1]['title']
        self.url = data['entries'][-1]['url']
        self.access_time = data['lastAccessed']

    title = ','.join([ 'title', 'url', 'access time' ])

    def __str__(self):
        return '{},{},{}'.format(
            escape(self.title),
            escape(self.url),
            format_timestamp(self.access_time)
        )


if __name__ == '__main__':
    save_tabs()
