import os


def get_file(title, link):
    files = os.listdir(".")
    names = title.split(" ")
    for name in names:
        tmp = files
        files = list(filter(lambda x: name in x and not x.endswith(".txt"), files))
        if len(files) == 0:
            files = tmp

        if len(files) == 1:
            break
        if len(files) == 0:
            raise FileNotFoundError("something went wrong, please create an issue with the link: " + link)
    actual_file = files[0]
    file_type = actual_file.split(".")[len(actual_file.split(".")) - 1]
    return [actual_file, file_type]
