import fnmatch
import os
import re
import subprocess
import sponsorblock as sb

from file_handler import get_file
client = sb.Client()

def get_segments_to_remove(link):
    # get sponsor segments from sponsorblock (including sponsors, intro, outro and interaction reminders)
    segments = client.get_skip_segments(link,
                                        categories=["sponsor", "selfpromo", "interaction", "intro", "outro", "preview"])
    return segments


def handle_video(author_key, title_key, entry, segments):
    file_array = get_file(title_key, entry['link'])
    file_name = file_array[0]
    file_type = file_array[1]

    tmp = "file." + file_type
    os.rename(file_name, tmp)
    print(f"cutting {title_key} by {author_key}")
    cut_sponsored_segments(re.sub(f".{file_type}", "", tmp), file_type, segments)
    print(f"done cutting {title_key} by {author_key}")
    new_title = file_name
    if file_name in os.listdir():
        new_title = get_new_title(file_name)
    os.rename(tmp, new_title)
    return file_name


def cut_sponsored_segments(file_name, file_type, sponsorblock_segments):
    if sponsorblock_segments is None:
        return
    create_clips_of_the_parts_to_leave_in(file_name, sponsorblock_segments, file_type)

    create_clip_file_list(file_name)
    # concatenate all the clips in order into a single video
    subprocess.call(f"ffmpeg -safe 0 -y -f concat -i {file_name}_list.txt -c copy {file_name}.{file_type} ")

    for file in os.listdir():
        if file.startswith(file_name + "_"):
            os.remove(file)


def get_new_title(new_title):
    count = 0
    tmp = new_title + "_" + str(count) + ".webm"
    while tmp in os.listdir():
        count += 1
        tmp = new_title + "_" + str(count) + ".webm"
    return tmp


def fix_segments(segments):
    new_segments = []
    for segment in segments:
        skip = False
        for seg in new_segments:
            if segment.start > seg.start and seg.end > segment.end:
                skip = True
                break

            if seg.start < segment.start < seg.end < segment.end:
                seg.end = segment.end
                skip = True
        if not skip:
            new_segments.append(segment)

    return new_segments


def create_clips_of_the_parts_to_leave_in(file_name, segments, file_type):
    current_start: float = 0.0
    os.rename(file_name + "." + file_type, file_name + "_0." + file_type)
    clip_index = 1
    segments = fix_segments(segments)
    for segment in segments:
        start: float = segment.start
        end: float = segment.end

        subprocess.call(
            f"""ffmpeg -y -ss {current_start} -to {start} -i "{file_name}_0.{file_type}" -c copy "{file_name}_{clip_index}.{file_type}" """
        )
        clip_index += 1
        current_start: float = end
    # No end time to get the final part of the video
    subprocess.call(
        f"""ffmpeg -y -ss {current_start} -i "{file_name}_0.{file_type}" -c copy "{file_name}_{clip_index}.{file_type}" """
    )
    for file in os.listdir('.'):
        if fnmatch.fnmatch(file, file_name + "_[^1-9]." + file_type):
            os.remove(file_name + "_0." + file_type)
            return


def create_clip_file_list(file_name):
    files = []
    for file in os.listdir():
        if file.startswith(file_name + "_"):
            files.append(file)
    # sorting is actually unnecessary but it's for good measure
    files.sort(key=file_sorter)
    # open file_name_list.txt and write the list of files to it
    with open(file_name + "_list.txt", 'a') as file:
        for f in files:
            file.write(f"file '{f}'\n")


# because python sorts files like this: file_1.mp4 file_10.mp4 file_2.mp4, we force python to sort by the "part number"
# in other words: sort by X where X is a number in file_X.mp4
def file_sorter(e: str):
    out = e.split("_")
    key: int = int(out[len(out) - 1].split(".")[0])
    return key
