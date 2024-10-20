import json
import os
from collections import defaultdict

from yt_dlp import YoutubeDL

config_directory = os.path.abspath("../config")
already_watched = {}
ignored = {}
broken_videos: dict[str, list] = {}
keywords_to_skip: dict[str, list] = {}
channels = {}
checked_titles = {}


def read_config():
    read_channel_dict()
    read_and_add_new_channels_to_channel_dict()
    read_already_watched()
    read_ignored()
    read_not_working_videos()
    read_keywords_to_skip()
    read_checked_titles()
    save_channel_dict()


# TODO read in new channels after the old ones
def read_and_add_new_channels_to_channel_dict():
    global channels
    if not os.path.exists("../categories"):
        return
    for category in os.listdir("../categories"):
        with open( "../categories/" + category, encoding='utf-8') as f:
            for line in f:
                with YoutubeDL({"quiet": "true"}) as ydl:
                    test = ydl.extract_info(line, download=False)
                    if str(test['uploader']) not in channels:
                        category_in_dict = channels.get(str(category.split(".")[0]), {})
                        category_in_dict[str(test['uploader'])] = str(test['channel_id'])
                        channels.update({str(category.split(".")[0]): category_in_dict})
    # delete all category files
    for category in os.listdir("../categories"):
        os.remove("../categories/" + category)

def read_ignored():
    try:
        f = open(config_directory + "/ignored.json", encoding='utf-8')
        global ignored
        ignored = json.load(f)
    except:
        ignored = {}


def save_ignored():
    with open(config_directory + '/ignored.json', 'w', encoding='utf-8') as outfile:
        json.dump(ignored, outfile, indent=4)


def save_downloaded_list():
    with open(config_directory + '/watched.json', 'w+', encoding='utf-8') as outfile:
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


def save_channel_dict():
    with open(config_directory + '/channels.json', 'w', encoding='utf-8') as outfile:
        global channels
        json.dump(channels, outfile, indent=4)


def read_channel_dict():
    print(config_directory + "/channels.json")
    global channels
    try:
        f = open(config_directory + "/channels.json", encoding='utf-8')

        channels = json.load(f)
    except:
        channels = {}

def get_channels():
    return channels


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
