import numpy as np
import pandas
from scipy.spatial.qhull import Delaunay


class ImageArray(np.ndarray):

    def __new__(cls, input_array, name=None):

        obj = np.asarray(
            input_array,
            dtype=input_array.dtype
        ).view(cls)
        obj.name = name
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.name = getattr(obj, 'name', None)
    

class OCRDataFrame(pandas.DataFrame):

    def __init__(self, data=None, index=None, columns=None, dtype=None,
                 copy=False, image_size=None, name=None):

        super().__init__(data=data, index=index, columns=columns, dtype=dtype,
                         copy=copy)

        self.attrs["image_size"] = image_size
        self.attrs["name"] = name

    def create_bbox(self):

        EPS = 1e-16

        if self.attrs["image_size"] is None:
            raise ValueError("Bounding box can not be created as attribute " 
                             "'image_size' is None!")

        Dx, Dy = self.attrs["image_size"]

        bbox = pandas.DataFrame([[EPS, EPS, 0,  0],
                                 [EPS, EPS, Dx, 0],
                                 [EPS, EPS, Dx, Dy],
                                 [EPS, EPS, 0,  Dy]],
                                 columns=["width", "height", "x", "y"],
                                 index=["box[UL]", "box[LL]",
                                        "box[UR]", "box[LR]"])

        return bbox
