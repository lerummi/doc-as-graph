import cv2
from sklearn.base import BaseEstimator, TransformerMixin

from .datamodels import ImageArray


class ImagePreprocessor(BaseEstimator, TransformerMixin):

    def __init__(self, method: callable = None, **method_kwargs):

        super().__init__()
        self.method = method
        self.method_kwargs = method_kwargs

    def transform(self, X: ImageArray):

        name = X.name #"-".join([X.name, self.__class__.__name__])

        transformed = self.method(X, **self.method_kwargs)
        return ImageArray(transformed, name=name)


class AdaptiveThreshold(ImagePreprocessor):

    def __init__(self, **method_kwargs):

        self.defaults.update(**method_kwargs)

        super().__init__(cv2.adaptiveThreshold, **self.defaults)

    @property
    def defaults(self):

        return {"maxValue": 255,
                "adaptiveMethod": cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                "thresholdType": cv2.THRESH_BINARY,
                "blockSize": 11,
                "C": 2}


class OtsuThreshold(ImagePreprocessor):

    def __init__(self, **method_kwargs):

        self.defaults.update(**method_kwargs)
        
        method = lambda x, **kwargs: cv2.threshold(x, **kwargs)[1]

        super().__init__(method, **self.defaults)

    @property
    def defaults(self):

        return {"thresh": 0,
                "maxval": 255,
                "type": cv2.THRESH_BINARY + cv2.THRESH_OTSU}
