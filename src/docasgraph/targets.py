import os
from google.cloud import storage
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


def upload_to_gcs(bucket, local_directory, target_directory):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    for input_file in os.listdir(local_directory):

        output_file = os.path.join(target_directory, input_file)
        input_file = os.path.join(local_directory, input_file)

        blob = bucket.blob(output_file)
        blob.upload_from_filename(input_file)
