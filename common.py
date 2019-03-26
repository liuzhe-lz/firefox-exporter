from datetime import datetime
import os.path
import shutil
import sqlite3
from tempfile import NamedTemporaryFile


__all__ = [ 'query', 'escape', 'format_timestamp' ]


_conns = { }

def _get_db(input_dir, db_file_name):
    if db_file_name not in _conns:
        # can't connect to original db if firefox is running
        orig = open(os.path.join(input_dir, db_file_name), 'rb')
        copy = NamedTemporaryFile(delete = False)
        shutil.copyfileobj(orig, copy)
        orig.close()
        copy.close()
        _conns[db_file_name] = sqlite3.connect(copy.name)
    return _conns[db_file_name]

def query(input_dir, db_file_name, sql, packer = lambda x: x):
    db = os.path.join(input_dir, db_file_name)
    cursor = _get_db(input_dir, db_file_name).cursor()
    cursor.execute(sql)
    records = cursor.fetchall()
    return [ packer(record) for record in records ]


def escape(s):
    if s is None: return '""'
    s = s.replace('"', '""')
    s = s.replace('\\', '\\\\')
    s = s.replace('\r', '\\r')
    s = s.replace('\n', '\\n')
    return '"{}"'.format(s)


def format_timestamp(ts):
    if ts is None: return ''
    if 1_000_000_000_000_000 <= ts and ts <= 9_999_999_999_999_999:
        return str(datetime.fromtimestamp(ts // 1_000_000))
    elif 1_000_000_000_000 <= ts and ts <= 9_999_999_999_999:
        return str(datetime.fromtimestamp(ts // 1_000))
    assert False
