from common import *


_cached_places = { }

def get_places(input_dir = '.'):
    if input_dir not in _cached_places:
        _cached_places[input_dir] = _get_places_no_cache(input_dir)
    return _cached_places[input_dir]

def _get_places_no_cache(input_dir):
    sql = 'select id, url, title, hidden, frecency, last_visit_date, description from moz_places'
    place_records = query(input_dir, 'places.sqlite', sql, Place)
    places = { place.id: place for place in place_records }
    attr_records = query(input_dir, 'places.sqlite', 'select id, name from moz_anno_attributes')
    annos = { id_: name for id_, name in attr_records }
    anno_records = query(input_dir, 'places.sqlite', 'select place_id, anno_attribute_id from moz_annos')
    for place_id, anno_id in anno_records:
        if annos[anno_id].startswith('downloads'):
            places[place_id].is_download = True
    return places


class Place:
    def __init__(self, record):
        self.id, self.url, self.title, self.hidden, self.visit_times, self.access_time, self.desc = record
        self.is_webpage = not self.url.startswith('place:') and not record[1].startswith('about:')
        self.is_download = False
        if self.is_webpage: assert '://' in self.url, record
        assert self.hidden in (0, 1), record
