import json
import os
from collections import defaultdict

from yt_dlp import YoutubeDL

config_directory = os.getcwd() + "/configs"
already_watched = {}
ignored = {}
broken_videos: dict[str, list] = {}
keywords_to_skip: dict[str, list] = {}
channels = {}
word_probabilities = {}
checked_titles = {}


# TODO read in new channels after the old ones

def read_and_add_new_channels_to_channel_dict():
    pass


def read_config():
    read_channel_dict()
    read_and_add_new_channels_to_channel_dict()
    read_already_watched()
    read_ignored()
    read_not_working_videos()
    read_keywords_to_skip()
    read_checked_titles()
    pass


def read_ignored():
    try:
        f = open(config_directory + "/ignored.json", encoding='utf-8')
        global ignored
        ignored = json.load(f)
    except:
        ignored = {}
    pass

def save_ignored():
    with open(config_directory + '/ignored.json', 'w', encoding='utf-8') as outfile:
        json.dump(ignored, outfile, indent=4)


def save_downloaded_list():
    with open(config_directory + '/watched.json', 'w', encoding='utf-8') as outfile:
        json.dump(already_watched, outfile, indent=4)


def read_already_watched():
    try:
        f = open(config_directory + "/watched.json", encoding='utf-8')
        global already_watched
        already_watched = json.load(f)
    except:
        already_watched = {}


def get_already_watched():
    return already_watched


def get_ignored():
    return ignored


def read_not_working_videos():
    try:
        f = open(config_directory + "/broken.json", encoding='utf-8')
        global broken_videos
        broken_videos = json.load(f)
    except:
        broken_videos = {}


def get_broken_videos():
    return broken_videos


def save_broken_videos():
    with open(config_directory + '/broken.json', 'w', encoding='utf-8') as outfile:
        json.dump(broken_videos, outfile, indent=4)


def read_keywords_to_skip():
    try:
        f = open(config_directory + "/skip.json", encoding='utf-8')
        global keywords_to_skip
        keywords_to_skip = json.load(f)
    except:
        keywords_to_skip = {}


def get_keywords_to_skip():
    return keywords_to_skip


def save_channel_dict(channel_dict):
    with open(config_directory + '/channels.json', 'w', encoding='utf-8') as outfile:
        json.dump(channel_dict, outfile, indent=4)


def read_channel_dict():
    try:
        f = open(config_directory + "/channels.json", encoding='utf-8')
        global channels
        channels = json.load(f)
    except:
        channels = {}
    return channels


def read_legacy_channel_converter_dict_lists():
    try:
        f = open(config_directory + "/legacy_converter_dict.json", encoding='utf-8')
        global channels
        legacy_channels = json.load(f)
    except:
        legacy_channels = {}
    return legacy_channels


def save_legacy_converter_dict(legacy):
    with open(config_directory + '/legacy_converter_dict.json', 'w', encoding='utf-8') as outfile:
        json.dump(legacy, outfile, indent=4)

def get_channel_dict(channel_link: str):
    with YoutubeDL({"quiet": "true"}) as ydl:
        test = ydl.extract_info(channel_link, download=False)

    return {str(test['uploader']): str(test['channel_id'])}



def save_checked_titles():
    with open(config_directory + '/checked_titles.json', 'w', encoding='utf-8') as outfile:
        json.dump(checked_titles, outfile, indent=4)


def read_checked_titles():
    try:
        f = open(config_directory + "/checked_titles.json", encoding='utf-8')
        global checked_titles
        checked_titles = json.load(f)
    except:
        checked_titles = {}
    return checked_titles
