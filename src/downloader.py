from datetime import datetime, timedelta, time
import os
import pathlib

import feedparser
from yt_dlp import YoutubeDL

import sponsorblocker
from config_reader import get_channels, get_ignored, get_already_watched, save_ignored, \
    get_keywords_to_skip, get_broken_videos, save_broken_videos, save_downloaded_list


def get_channel_feed(channel):
    channel_rss_feed = feedparser.parse("https://www.youtube.com/feeds/videos.xml?channel_id=" + channel)
    return channel_rss_feed


def add_to_fail_category(error, entry):
    broken_videos = get_broken_videos()
    if "ERROR: Postprocessing" in error.args[0]:
        key = "Postprocessing"
    elif "HTTP Error 503: Service Unavailable" in error.args[0]:
        return
    elif "Video unavailable. The uploader has not made this video available in your country" in error.args[0]:
        key = "regionlocked"
    elif "Join this channel to get access to members-only content like this video, and other exclusive perks." in \
            error.args[0]:
        key = "membersonly"
    elif "This live event will begin" in error.args[0]:
        return
    elif "Premieres in" in error.args[0]:
        return
    elif "Video unavailable. This video is not available" in error.args[0]:
        key = "removed"
    else:
        print(error)
        print(error.args[0])
        print("this is a new one")
        key = error.args[0]
    if key not in broken_videos:
        broken_videos[key] = []
    broken_videos[key].append(entry['link'])
    save_broken_videos()


def is_short(entry):
    with YoutubeDL({"quiet": "true"}) as ydl:
        try:
            test = ydl.extract_info(str(entry['link']), download=False)
            if "live_status" in test and test['live_status'] == "is_live":
                print("livestream is still live")
                return True

            if 'duration' in test and test['duration'] <= 60:
                print(f"{entry['title']} is a short, skipping")
                get_ignored()[entry['title']] = 1
                return True

        except Exception as error:
            print("failed download:" + entry['title'] + " " + entry['link'])
            add_to_fail_category(error, entry)
            return True
    pass


def should_skip_keyword(entry, category, ignored):
    keywords_to_skip = get_keywords_to_skip()
    if 'skip_categories' in keywords_to_skip and category in keywords_to_skip['skip_categories']:
        if entry['author'] in keywords_to_skip['skip_categories'][category]:

            for keyword in keywords_to_skip['skip_categories'][category][entry['author']]:
                if keyword in entry['title']:
                    print("category and author based keyword: " + keyword + " is in " + entry['title'] + " by " + entry[
                        'author'] + ", skipping")
                    ignored[entry['title']] = 1
                    return True
        if 'skip_in_this_category' in keywords_to_skip['skip_categories'][category]:
            for keyword in keywords_to_skip['skip_categories'][category]['skip_in_this_category']:
                if keyword in entry['title']:
                    print("category keyword: " + keyword + " is in " + entry['title'] + " by " + entry[
                        'author'] + ", skipping")
                    ignored[entry['title']] = 1
                    return True
    if 'skip_in_all_categories' in keywords_to_skip:
        for keyword in keywords_to_skip['skip_in_all_categories']:
            if keyword in entry['title']:
                print(
                    "global keyword: " + keyword + " is in " + entry['title'] + " by " + entry['author'] + ", skipping")
                ignored[entry['title']] = 1
                return True
    return False


def has_skip_reason(entry, category):
    ignored = get_ignored()
    broken_videos = get_broken_videos()
    if should_skip_keyword(entry, category, ignored):
        return True
    if entry['title'] in ignored:
        return True
    if category in broken_videos and entry['title'] in broken_videos[category]:
        return True  # I think this works
    if is_short(entry):
        return True
    return False


def should_skip(entry, category):
    if has_skip_reason(entry, category):
        ignored = get_ignored()
        ignored[entry['title']] = 1
        save_ignored()
        return True
    already_watched = get_already_watched()
    if entry['author'] in already_watched and entry['title'] in already_watched[entry['author']]:
        return True
    pass


def get_rate():
    begin_time: time = time(6, 0)
    end_time: time = time(23, 0)
    rate = 10000000 + 900000000000000000000000000000000000
    alternative_rate = 9999999999999999999999999999999999
    check_time = datetime.now().time()
    if begin_time < end_time:
        if begin_time <= check_time <= end_time:
            return rate
    else:  # crosses midnight
        if check_time >= begin_time or check_time <= end_time:
            return rate
    return alternative_rate


def setup_downloader_options(entry):
    # todo add subtitle language options with/out auto generated?
    rate = get_rate()
    ydl_opts = {'writeinfojson': True, 'writethumbnail': True, 'outtmpl': '%(title)s.%(ext)s', 'format': 'best',
                'ratelimit': rate, 'quiet': True, 'subtitleslangs': ["en"], 'writesubtitles': (True,)}
    return ydl_opts


def download(entry, ydl_opts, category):
    title_key = entry['title']
    author_key = entry['author']
    with YoutubeDL(ydl_opts) as ydl:
        try:

            print(f"Downloading {title_key} by {author_key} from category {category}")
            # download the video and the metadata
            ydl.extract_info(entry['link'], download=True)
            print(f"Downloaded {title_key} by {author_key}")
        except Exception as e:
            add_to_fail_category(e, entry)
            print("Failed download:" + entry['title'] + " " + entry['link'])
            return False
    return True

def download_video(entry, category):
    if should_skip(entry, category):
        return
    ydl_opts = setup_downloader_options(entry)
    sponsorblock_segments = None
    try:
        sponsorblock_segments = sponsorblocker.get_segments_to_remove(entry['link'])
    except:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(entry['link'], False)
            if not datetime.strptime(info['upload_date'], "%Y%m%d") < datetime.now() - timedelta(days=7):
                return

    if not download(entry, ydl_opts, category):
        return
    author_key = entry['author']
    title_key = entry['title']
    actual_file = sponsorblocker.handle_video(author_key, title_key, entry, sponsorblock_segments)
    already_watched =  get_already_watched()
    if author_key not in already_watched:
        already_watched[author_key] = {}
    already_watched[author_key][title_key] = 1
    print("New video from " + author_key + ": " + actual_file + " has been downloaded and cut")
    save_downloaded_list()


def download_and_sponsorblock():
    today = datetime.today().strftime('%Y-%m-%d')
    channels = get_channels()
    for category in channels:
        if pathlib.Path(category).is_dir() is False:
            os.mkdir(category)
        os.chdir(category)
        if pathlib.Path(today).is_dir() is False:
            os.mkdir(today)
        os.chdir(today)
        for channel in channels[category]:
            channel_rss_feed = get_channel_feed(channels[category][channel])
            for entry in channel_rss_feed.entries:
                download_video(entry, category)

        os.chdir("../..")
    pass


def start_download():
    os.chdir("../videos")
    download_and_sponsorblock()
    pass
