from bookmarks import load_bookmarks, save_bookmarks
from downloads import load_downloads, save_downloads
from history import load_history, save_history
from passwords import load_passwords, save_passwords
from tabs import load_tabs, save_tabs

import os


class Profile:
    def __init__(self, input_dir):
        print('Loading bookmarks...')
        self.bookmarks = load_bookmarks(input_dir)
        print('Loading downloads...')
        self.downloads = load_downloads(input_dir)
        print('Loading history...')
        self.history = load_history(input_dir)
        print('Loading passwords...')
        self.passwords = load_passwords(input_dir)
        print('Loading tabs...')
        self.tabs = load_tabs(input_dir)

    def save(self, output_dir):
        os.makedirs(output_dir, exist_ok = True)
        print('Saving')
        save_bookmarks(bookmarks = self.bookmarks, output_dir = output_dir)
        save_downloads(downloads = self.downloads, output_dir = output_dir)
        save_history(history = self.history, output_dir = output_dir)
        save_passwords(passwords = self.passwords, output_dir = output_dir)
        save_tabs(tabs = self.tabs, output_dir = output_dir)
        print('Data saved to {}'.format(output_dir))
