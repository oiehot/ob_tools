import os
import subprocess


def makedir(path):
    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass


def explore_path(path: str) -> None:
    if not path or path == "":
        return
    if os.name == "nt":  # Windows
        subprocess.run(["explorer", path])
    elif os.name == "posix":  # macOS, Linux
        subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", path])
