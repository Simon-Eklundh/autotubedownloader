from config_reader import read_config
from downloader import start_download


# youtube downloader

# check each video to see if it should be downloaded
# create category directory
# create date repository inside category directory
# download videos
# sponsorblock videos
# save downloaded videos, ignored, broken


# files:

# main DONE
# config reader DONE
# youtube downloader TODO
# sponsorblocker TODO






# start app
def main():
    read_config()
    start_download()


if __name__ == "__main__":
    main()