import os
import pandas
import spacy
import numpy as np
import pytesseract
from pytesseract import image_to_data, Output
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.manifold import MDS
from scipy.spatial import Delaunay

from .datamodels import ImageArray, OCRDataFrame


# Try to find executable on system
tesseract_path = os.popen("which tesseract") \
                   .read() \
                   .replace("\n", "")
if not tesseract_path:
    raise ValueError("Tesseract executable does not seem installed!")
pytesseract.pytesseract.tesseract_cmd = tesseract_path

EPS = 1e-16


class TesseractOCR(BaseEstimator, TransformerMixin):

    def __init__(self,
                 dropna: bool=True,
                 dropempty: bool=True,
                 lang="eng"):

        super().__init__()
        self.dropna = dropna
        self.dropempty = dropempty
        self.lang = lang

    def fit(self, X, y=None):

        return self

    def transform(self, X: ImageArray):

        data = image_to_data(
            X, 
            output_type=Output.DATAFRAME,
            lang=self.lang
        )

        if self.dropna:
            data = data.pipe(lambda x: x[~x["text"].isna()])

        if self.dropempty:
            # Remove items with text purely composed of whitespace
            data = data.pipe(lambda x: x[x["text"].str.count(" ") != \
                                       x["text"].apply(len)])

        data["x"] = data["left"] + data["width"] / 2
        data["y"] = data["top"] + data["height"] / 2

        data.index = ["-".join([X.name, str(i)]) for i in range(data.shape[0])]

        return OCRDataFrame(data, image_size=X.shape, name=X.name)


class TriangulationGenerator(BaseEstimator, TransformerMixin):

    def __init__(self, metric="l2_box"):

        super().__init__()
        self.metric = metric

    def _compute_distance_matrix(self, data: pandas.DataFrame):

        x = data["x"].values[:, np.newaxis]
        y = data["y"].values[:, np.newaxis]

        dx = data["width"].values
        dy = data["height"].values

        if self.metric == "l1":
            return abs(x - x.T) + abs(y - y.T)

        # Squared distance matrix from center to center
        distance_0 = np.sqrt((x - x.T) ** 2 + (y - y.T) ** 2)

        if self.metric == "l2":
            return distance_0

        # Unit vector connecting boxes pairwise
        e = np.array([x - x.T, y - y.T])
        e = e / (np.linalg.norm(e, axis=0) + 1e-16)

        # Unit vector connecting center point to edge
        e_edge = np.array([dx / 2, dy / 2])
        e_edge = e_edge / (np.linalg.norm(e_edge, axis=0) + 1e-16)
        # compare x - components of e and e_edge: If abs(e_x) > e_edge_x,
        # vertical rectangle box is crosses
        crosses_vertical_1 = np.abs(e[0, ...]) > e_edge[0, :, np.newaxis]
        crosses_vertical_2 = np.abs(e[0, ...]) > e_edge[0, np.newaxis, :]

        # Corrected distance reduced by distance to rectangle edges
        distance = distance_0 - \
                   crosses_vertical_1 * (dx[..., np.newaxis] / 2) / (
                               np.abs(e[0, ...]) + 1e-16) - \
                   (~crosses_vertical_1) * (dy[..., np.newaxis] / 2) / (
                               np.abs(e[1, ...]) + 1e-16) - \
                   crosses_vertical_2 * (dx[np.newaxis, ...] / 2) / (
                               np.abs(e[0, ...]) + 1e-16) - \
                   (~crosses_vertical_2) * (dy[np.newaxis, ...] / 2) / (
                               np.abs(e[1, ...]) + 1e-16)
        distance[np.eye(distance.shape[0], dtype=bool)] = 0
        distance[distance < 0] = 0  # Overlapping

        return distance

    def _create_triangulation(self, distance_matrix: np.ndarray):

        mds = MDS(n_components=2, dissimilarity="precomputed", eps=1e-4)
        Xt = mds.fit_transform(distance_matrix)

        return Delaunay(Xt)

    def transform(self, X: OCRDataFrame):

        # Add bbox to input dataframe
        bbox = X.create_bbox()
        Xbbox = pandas.concat([X, bbox], axis=0)

        distance = self._compute_distance_matrix(Xbbox)
        triangulation = self._create_triangulation(distance)

        # Find all simplices containing a bounding box point
        box_simp = (triangulation.simplices >= X.shape[0]).any(axis=1)

        # Remove image bounding box from triangulation
        triangulation.simplices = triangulation.simplices[~box_simp]

        triangulation.point_names = X.index

        return triangulation

    
class SpacyWordEmbedding(BaseEstimator, TransformerMixin):
    
    def __init__(self, 
                 model_name: str = None, 
                 text_column: str = "text"):

        super().__init__()
        self.model_name = model_name

        self.model = spacy.load(model_name)
        
        self.text_column = text_column

    def fit(self, X, y=None):

        return self
        
    def transform(self, X: OCRDataFrame):
        
        texts = self.model.pipe(X[self.text_column])
        name = X.attrs["name"]
        
        vectors = np.vstack([
            text.vector for text in texts
        ])

        columns = [
            f"word_embedding_{comp}"
            for comp in range(vectors.shape[1])
        ]

        embedding = pandas.DataFrame(
            vectors.tolist(),
            columns=columns,
            index=X.index
        )

        X = pandas.concat([X, embedding], axis=1)
        
        return OCRDataFrame(
            X, 
            image_size=X.shape,
            name=name
        )
