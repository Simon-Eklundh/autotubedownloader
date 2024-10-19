from config_reader import read_config
from downloader import start_download


# youtube downloader

# start app
# read in channel list
# read in new channels to add to channel list
# add new channels to channel list
# read watched videos
# read ignored
# read broken
# check each video to see if it should be downloaded
# create category repository
# create date repository inside category repository
# download videos
# sponsorblock videos


# files:

# main
# config reader
# youtube downloader
# sponsorblocker






# start app
def main():
    read_config()
    start_download()


if __name__ == "__main__":
    main()