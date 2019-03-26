#!/usr/bin/env python3

from profile import Profile

import os
import sys
import traceback


def _export_profile(key, input_dir):
    assert os.path.isdir(input_dir)
    os.makedirs('firefox-profiles', exist_ok = True)
    output_dir = os.path.join('firefox-profiles', key)
    i = 0
    while not _try_mkdir(output_dir):
        i += 1
        output_dir = os.path.join('firefox-profiles', '{}.{}'.format(key, i))
    Profile(input_dir).save(output_dir)

def _try_mkdir(path):
    try:
        os.mkdir(path)
        return True
    except FileExistsError:
        return False


def find_profiles():
    if sys.platform == 'linux':
        return _find_profiles_linux()
    assert False

def _find_profiles_linux():
    path = os.path.expanduser('~/.mozilla/firefox')
    profiles = [ profile for profile in os.listdir(path) if profile.endswith('.default') ]
    return { profile[:-8] : path + '/' + profile for profile in profiles }


def export_default_profiles():
    os.makedirs('firefox-profiles', exist_ok = True)
    for key, input_dir in find_profiles().items():
        _export_profile(key, input_dir)


def export_specific_profile(path):
    assert os.path.isdir(path)
    key = os.path.basename(path)
    if not key:
        key = os.path.basename(os.path.dirname(path))
    if key.endswith('.default'):
        key = key[:-8]
    _export_profile(key, path)


def main(args):
    if len(args) == 0:
        export_default_profiles()
    elif len(args) == 1:
        export_specific_profile(args[0])
    else:
        _print_usage()

def _print_usage():
    print('Usage:')
    print('    {} [PROFILE_PATH]'.format(sys.argv[0]))


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except Exception:
        _print_usage()
        print()
        traceback.print_exc()
