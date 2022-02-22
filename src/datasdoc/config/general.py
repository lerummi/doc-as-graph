import os

env = os.environ.get


class Settings(object):

    LOCAL_DATA_PATH = env("LOCAL_DATA_PATH", "/data")

    IMAGES_DOWNLOAD_PATH = os.path.join(
        LOCAL_DATA_PATH,
        "downloads"
    )
