from common import *
from places import get_places

import os.path


def load_downloads(input_dir):
    return [ Download(place) for place in get_places(input_dir).values() if place.is_download ]

def save_downloads(input_dir = '.', output_dir = '.', downloads = None):
    if downloads is None: downloads = load_downloads(input_dir)
    f = open(os.path.join(output_dir, 'downloads.csv'), 'w', encoding = 'utf-8')
    f.write(Download.title + '\n')
    for dl in sort_downloads(downloads):
        f.write(str(dl) + '\n')
    f.close()

def sort_downloads(downloads):
    dict_ = { }
    for dl in downloads:
        if dl.url not in dict_ or dl.access_time > dict_[dl.url].access_time:
            dict_[dl.url] = dl
    return sorted(dict_.values(), key = lambda dl: dl.access_time)


class Download:
    def __init__(self, place):
        self.url = place.url
        self.title = place.title
        self.access_time = place.access_time

    title = ','.join([ 'access time', 'title', 'url' ])

    def __str__(self):
        return '{},{},{}'.format(
            format_timestamp(self.access_time),
            escape(self.title),
            escape(self.url)
        )


if __name__ == '__main__':
    save_downloads()
