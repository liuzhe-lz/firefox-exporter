from common import *
from places import get_places

from copy import copy
import os.path


def load_history(input_dir):
    history = [ History(place) for place in get_places(input_dir).values() ]
    return [ hist for hist in history if hist.valid ]

def save_history(input_dir = '.', output_dir = '.', history = None):
    if history is None: history = load_history(input_dir)
    f = open(os.path.join(output_dir, 'history.csv'), 'w')
    f.write(History.title + '\n')
    for hist in sort_history(history):
        f.write(str(hist) + '\n')
    f.close()

def sort_history(history):
    dict_ = { }
    for hist in history:
        if hist.url not in dict_:
            dict_[hist.url] = copy(hist)
        else:
            if hist.access_time > dict_[hist.url].access_time:
                dict_[hist.url].access_time = hist.access_time
                dict_[hist.url].title = hist.title
                dict_[hist.url].desc = hist.desc
            dict_[hist.url].visit_times += hist.visit_times
    return sorted(dict_.values(), key = lambda hist: hist.access_time)


class History:
    def __init__(self, place):
        self.valid = (not place.hidden and place.is_webpage and place.access_time is not None)
        self.url = place.url
        self.title = place.title
        self.visit_times = place.visit_times
        self.access_time = place.access_time
        self.desc = place.desc

    title = ','.join([ 'access time', 'title', 'url', 'visit times', 'description' ])

    def __str__(self):
        return '{},{},{},{},{}'.format(
            format_timestamp(self.access_time),
            escape(self.title),
            escape(self.url),
            self.visit_times,
            escape(self.desc)
        )


if __name__ == '__main__':
    save_history()
