from common import *


_cached_places = { }

def get_places(input_dir = '.'):
    if input_dir not in _cached_places:
        _cached_places[input_dir] = _get_places_no_cache(input_dir)
    return _cached_places[input_dir]

def _get_places_no_cache(input_dir):
    place_records = query(input_dir, 'places.sqlite', 'select * from moz_places', Place)
    places = { place.id: place for place in place_records }
    attr_records = query(input_dir, 'places.sqlite', 'select id, name from moz_anno_attributes')
    annos = { id_: name for id_, name in attr_records }
    assert annos[3] == 'downloads/destinationFileURI' and annos[8] == 'downloads/metaData'
    anno_records = query(input_dir, 'places.sqlite', 'select place_id, anno_attribute_id from moz_annos')
    for place_id, anno_id in anno_records:
        if anno_id == 3 or anno_id == 8:
            places[place_id].is_download = True
    return places


class Place:
    def __init__(self, record):
        # 0: id
        # 1: url
        # 2: title
        # 3: rev_host
        # 4: visit_count
        # 5: hidden
        # 6: typed
        # 7: favicon_id
        # 8: frecency
        # 9: last_visit_date
        # 10: guid
        # 11: foreigh_count
        # 12: url_hash
        # 13: description
        # 14: preview_image_url

        self.id = record[0]
        self.url = record[1]
        self.title = record[2]
        self.hidden = bool(record[5])
        self.visit_times = record[8]
        self.access_time = record[9]
        self.desc = record[13]

        self.is_webpage = not self.url.startswith('place:') and not record[1].startswith('about:')

        self.is_download = False

        if self.is_webpage: assert '://' in self.url, record
        assert record[5] in (0, 1), record
        assert record[7] is None, record
