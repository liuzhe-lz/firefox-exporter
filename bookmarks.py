from common import *
from places import get_places

from copy import copy
import os.path


def load_bookmarks(input_dir):
    list_ = query(input_dir, 'places.sqlite', 'select * from moz_bookmarks', Bookmark)
    bookmarks = { bookmark._id: bookmark for bookmark in list_ }
    places = get_places(input_dir)
    for bookmark in bookmarks.values():
        bookmark.finalize(bookmarks, places)
    return [ bookmark for bookmark in bookmarks.values() if bookmark.is_webpage ]

def save_bookmarks(input_dir = '.', output_dir = '.', bookmarks = None):
    if bookmarks is None: bookmarks = load_bookmarks(input_dir)
    f = open(os.path.join(output_dir, 'bookmarks.csv'), 'w', encoding = 'utf-8')
    f.write(Bookmark.title + '\n')
    for bookmark in sort_bookmarks(bookmarks):
        f.write(str(bookmark) + '\n')
    f.close()

def sort_bookmarks(bookmarks):
    # group by toolbar/menu, then sort by create time
    dict_ = { }
    for bookmark in bookmarks:
        key = (bookmark.title, bookmark.url)
        if key not in dict_:
            dict_[key] = copy(bookmark)
        else:
            dict_[key].create_time = min(dict_[key].create_time, bookmark.create_time)
            dict_[key].modify_time = max(dict_[key].modify_time, bookmark.modify_time)
            dict_[key].access_time = max(dict_[key].access_time, bookmark.access_time)
            dict_[key].in_toolbar = bookmark.in_toolbar
    return sorted(dict_.values(), key = lambda bookmark: (bookmark.in_toolbar, bookmark.create_time))


class Bookmark:
    def __init__(self, record):
        # 0: id
        # 1: type
        # 2: fk (id of place record)
        # 3: parent
        # 4: position
        # 5: title
        # 6: keywork_id
        # 7: folder_type
        # 8: dateAdded
        # 9: lastModified
        # 10: guid
        # 11: syncStatus
        # 12: syncChangeCounter

        # type:
        #   1: bookmark
        #   2: folder
        #   3: separator

        self._id = record[0]
        self._type = record[1]
        self._fk = record[2]
        self._parent = record[3]
        self.title = record[5]
        self.create_time = record[8]
        self.modify_time = record[9]
        self.access_time = None

        assert self._type in (1, 2, 3), record
        assert self.create_time is not None, record
        assert self.modify_time is not None, record

        if record[10] == 'toolbar_____':
            self.in_toolbar = True
        elif record[10] == 'menu________':
            self.in_toolbar = False
        elif record[10] == 'unfiled_____':
            self.in_toolbar = False
        else:
            self.in_toolbar = None  # None means unknown

        self.is_webpage = None
        self.url = None

    def finalize(self, bookmarks, places):
        self.is_webpage = (self._type == 1 and places[self._fk].is_webpage)
        if self.is_webpage:
            self.url = places[self._fk].url
            self.access_time = places[self._fk].access_time
            # recursively check if in toolbar
            ancestor = self
            while ancestor.in_toolbar is None and ancestor._parent != 0:
                ancestor = bookmarks[ancestor._parent]
            self.in_toolbar = ancestor.in_toolbar
            assert self.in_toolbar is not None

    title = ','.join([ 'title', 'url', 'create time', 'modify time', 'access time', 'in toolbar' ])

    def __str__(self):
        return '{},{},{},{},{},{}'.format(
            escape(self.title),
            escape(self.url),
            format_timestamp(self.create_time),
            format_timestamp(self.modify_time),
            format_timestamp(self.access_time),
            int(self.in_toolbar)
        )


if __name__ == '__main__':
    save_bookmarks()
