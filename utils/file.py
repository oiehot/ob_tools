import os


def makedir(path):
    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass
