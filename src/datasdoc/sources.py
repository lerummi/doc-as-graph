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
        query, 
        limit, 
        output_dir, 
        adult, 
        timeout, 
        properties=BingImageProperties()
        ):

        self.query = query
        self.output_dir = output_dir
        self.adult = adult
        self.properties = properties

        assert type(limit) == int, "limit must be integer"
        self.limit = limit
        assert type(timeout) == int, "timeout must be integer"
        self.timeout = timeout

        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0)" "Gecko/20100101 Firefox/60.0"
        }

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

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

    def download_image(self, link):

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
                    self.output_dir, 
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

    def download_images(self, links):

        for link in links:
            self.download_image(link)

    def get_url(self, start_at=None):

        query = urllib.parse.quote_plus(self.query)

        return (
            "https://www.bing.com/images/async?"
            f"q={query}"
            f"&count={self.limit}"
            f"&first={start_at}"
            f"&adlt={self.adult}"
        )

    def get_links(self, start_at=0):

        print(
            "\n\n[!!]Indexing page: {}\n"
            .format(start_at)
        )
        # Parse the page source and download pics

        request = urllib.request.Request(
            self.get_url(start_at=start_at), 
            None,
            headers=self.headers
        )

        response = urllib.request.urlopen(request)
        html = response.read().decode("utf8")
        links = re.findall("murl&quot;:&quot;(.*?)&quot;", html)
        links = [
            link for link in links 
            for suffix in self.properties.file_type
            if link.endswith(suffix)
        ]

        return links

    def run(self, start_at=0):

        links = self.get_links(start_at=start_at)

        for link in links:
            self.download_image(link)


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
