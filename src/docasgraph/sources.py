import cv2
import os
import hashlib
import urllib.request
import urllib
import imghdr
import posixpath
import re
from sklearn.base import BaseEstimator, TransformerMixin

from .datamodels import ImageArray


class BingImageProperties:

    file_type = ["jpeg", "bmp", "png", "jpg", "gif"]
    min_size_mb = 0.02


class Bing:
    def __init__(
        self, 
        adult, 
        timeout, 
        links_file="/tmp/query.links",
        properties=BingImageProperties(),
        search_delimiter=",",
    ):

        self.links_file = links_file
        self.adult = adult
        self.properties = properties
        self.search_delimiter = search_delimiter

        assert type(timeout) == int, "timeout must be integer"
        self.timeout = timeout

        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0)" "Gecko/20100101 Firefox/60.0"
        }

    def save_image(self, link, file_path):

        request = urllib.request.Request(link, None, self.headers)
        image = urllib.request.urlopen(request, timeout=self.timeout).read()
        if not imghdr.what(None, image):
            print("[Error]Invalid image, not saving {}\n".format(link))
            raise

        if len(image) / 1e6 < self.properties.min_size_mb:
            raise ValueError(
                "File does not fulfil image size properties."
            )
        
        with open(file_path, "wb") as f:
            f.write(image)

        if os.path.getsize(file_path) / 1e6 < self.properties.min_size_mb:
            os.remove(file_path)
            raise ValueError(
                "File does not fulfil image size properties."
            )

    @staticmethod
    def filename(link, file_type):

        return ".".join([
            hashlib.md5(link.encode()).hexdigest(),
            file_type
        ])

    def download_image(self, link, output_dir):

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Get the image link
        try:
            path = urllib.parse.urlsplit(link).path
            filename = posixpath.basename(path).split("?")[0]
            file_type = filename.split(".")[-1]
            if file_type.lower() not in self.properties.file_type:
                raise ValueError(
                    "File does not fulfil file_type properties."
                )

            filename = self.filename(link, file_type)

            # Download the image
            print(
                f"[%] Downloading Image from {link}\n"
                f"[%] Filename {filename}"
            )

            self.save_image(
                link, 
                os.path.join(
                    output_dir, 
                    filename
                )
            )

            print("[%] File Downloaded !\n")
        except Exception as e:
            print(
                f"[!] Issue getting: {link}\n"
                f"[!] Error:: {e}"
            )

        print(
             f"[%] Done. Downloaded images from {link}."
        )

    def download_images(self, output_dir):

        if not os.path.exists(self.links_file):
            raise IOError(
                f"Need to read url links from file {self.links_file} "
                "as specified by the appropriate input parameter. "
                "However, file does not exist!"
            )

        with open(self.links_file, "r") as links_file:
            links = links_file.readlines()

        print("Links that have been loaded", links)

        for link in links:
            self.download_image(link, output_dir)

    def get_url(self, query, start_at=None, limit=150):

        query = urllib.parse.quote_plus(query)

        return (
            "https://www.bing.com/images/async?"
            f"q={query}"
            f"&count={limit}"
            f"&first={start_at}"
            f"&adlt={self.adult}"
        )

    def get_links(
        self,
        query,
        limit=150,
        start_at=0,
        save=True
    ):

        limit = int(limit)

        query = query.split(self.search_delimiter)

        links = []

        for q in query:

            q = q.replace(" ", "")

            if limit > 150:
                start_at = 0
                while start_at < limit:
                    links_ = self.get_links(
                        query=q,
                        limit=min(limit - start_at, 150), 
                        start_at=start_at,
                        save=False, 
                    )
                    start_at += 150
                    links += list(set(links_))

            else:

                print(
                    "\n\n[!!]Indexing page: {}\n"
                    .format(start_at)
                )

                request = urllib.request.Request(
                    self.get_url(
                        q, 
                        start_at=start_at, 
                        limit=limit
                    ), 
                    None,
                    headers=self.headers
                )

                response = urllib.request.urlopen(request)
                html = response.read().decode("utf8")
                links_ = re.findall("murl&quot;:&quot;(.*?)&quot;", html)
                links_ = [
                    link for link in links_ 
                    for suffix in self.properties.file_type
                    if link.endswith(suffix)
                ]

                links += list(set(links_))

        if save:
            with open(self.links_file, "w") as links_file:
                for link in links:
                    links_file.write(link)
                    links_file.write("\n")
        else:
            return links


class ImageSource(BaseEstimator, TransformerMixin):

    def __init__(self, gray: bool = True):

        super().__init__()
        self.gray = gray

    def transform(self, imagefile: str):

        if not os.path.exists(imagefile):
            raise IOError(
                f"Image file {imagefile} does not exist!"
            )

        img = cv2.imread(imagefile)
        if self.gray:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        return ImageArray(img, name=os.path.split(imagefile)[-1])
