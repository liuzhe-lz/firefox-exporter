from common import *

import pyasn1.codec.der.decoder as der_decoder
from pyDes import triple_des, CBC

import base64
from copy import copy
import hashlib
import hmac
import json
import os.path


def load_passwords(input_dir):
    key = _get_global_key(input_dir)
    logins = json.load(open(os.path.join(input_dir, 'logins.json')))
    return [ Password(data, key) for data in logins['logins'] ]

def save_passwords(input_dir = '.', output_dir = '.', passwords = None):
    if passwords is None: passwords = load_passwords(input_dir)
    f = open(os.path.join(output_dir, 'passwords.csv'), 'w')
    f.write(Password.title + '\n')
    for password in sort_passwords(passwords):
        f.write(str(password) + '\n')
    f.close()

def sort_passwords(passwords):
    dict_ = { }
    for data in passwords:
        key = (data.hostname, data.username)
        if key not in dict_:
            dict_[key] = copy(data)
        else:
            if data.modify_time > dict_[key].modify_time:
                dict_[key].password = data.password
                dict_[key].modify_time = data.modify_time
            dict_[key].access_time = max(dict_[key].access_time, data.access_time)
            dict_[key].create_time = min(dict_[key].create_time, data.create_time)
            dict_[key].used_times += data.used_times
    return sorted(dict_.values(), key = lambda data: (data.hostname, data.username))


class Password:
    def __init__(self, data, key):
        self.hostname = data['hostname']
        self.username = _decode_login_data(data['encryptedUsername'], key)
        self.password = _decode_login_data(data['encryptedPassword'], key)
        self.create_time = data['timeCreated']
        self.modify_time = data['timePasswordChanged']
        self.access_time = data['timeLastUsed']
        self.used_times = data['timesUsed']

    title = ','.join([ 'hostname', 'user name', 'password', 'create time', 'modify time', 'access time', 'used times' ])

    def __str__(self):
        return '{},{},{},{},{},{},{}'.format(
            escape(self.hostname),
            escape(self.username),
            escape(self.password),
            format_timestamp(self.create_time),
            format_timestamp(self.modify_time),
            format_timestamp(self.access_time),
            self.used_times
        )


# Decryption algorithm copied from https://github.com/kspearrin/ff-password-exporter

def _get_global_key(input_dir):
    r = query(input_dir, 'key4.db', 'select item1, item2 from metaData where id="password"')
    global_salt, item2 = r[0]
    item2_asn1 = der_decoder.decode(item2)[0]
    item2_salt = item2_asn1[0][1][0].asOctets()
    item2_data = item2_asn1[1].asOctets()
    item2_val = _decrypt_key(global_salt, item2_salt, item2_data)
    assert item2_val == 'password-check'.encode()

    r = query(input_dir, 'key4.db', 'select a11 from nssPrivate where a11 is not null')
    a11 = r[0][0]
    a11_asn1 = der_decoder.decode(a11)[0]
    a11_salt = a11_asn1[0][1][0].asOctets()
    a11_data = a11_asn1[1].asOctets()
    a11_val = _decrypt_key(global_salt, a11_salt, a11_data)
    return a11_val[:24]

def _decrypt_key(global_salt, entry_salt, data, password = b''):
    assert len(entry_salt) == 20
    hp = _sha1(global_salt + password)
    chp = _sha1(hp + entry_salt)
    k1 = _hmac(entry_salt + entry_salt, chp)
    tk = _hmac(entry_salt,  chp)
    k2 = _hmac(tk + entry_salt, chp)
    k = k1 + k2
    assert len(k) == 40
    return _decrypt_3des(data, iv = k[-8:], key = k[:24])

def _decode_login_data(b64, key):
    der = base64.b64decode(b64)
    obj = der_decoder.decode(der)[0]
    iv = obj[1][1].asOctets()
    data = obj[2].asOctets()
    return _decrypt_3des(data, iv, key).decode()


def _decrypt_3des(data, iv, key):
    ret = triple_des(key, CBC, iv).decrypt(data)
    return ret[ : -ret[-1] ]  # remove padding

def _sha1(data):
    s = hashlib.sha1()
    s.update(data)
    return s.digest()

def _hmac(data, key):
    h = hmac.new(key, digestmod = 'sha1')
    h.update(data)
    return h.digest()


if __name__ == '__main__':
    save_passwords()
