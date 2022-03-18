import os
from sklearn.base import BaseEstimator, TransformerMixin
import pyarrow as pa
import pyarrow.parquet as pq

from .datamodels import OCRDataFrame


class ParquetWriter(BaseEstimator, TransformerMixin):

    def __init__(self, output_folder="/data/test_3"):

        self.output_folder = output_folder
        super().__init__()

    def fit(self, X, y=None):

        return self

    def transform(self, X: OCRDataFrame):

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        outputfile = X.attrs["name"]
        outputfile = ".".join(
            outputfile.split(".")[:-1]
        ) + ".parquet"

        table = pa.Table.from_pandas(X)

        pq.write_table(
            table, 
            os.path.join(
                self.output_folder, 
                outputfile
            )
        )
