import os
import numpy as np
import pandas
from functools import wraps

from .datamodels import OCRDataFrame
from .targets import ParquetWriter


def rectangle_overlap(X: pandas.DataFrame,
                      Y: pandas.DataFrame = None,
                      normalize_by_X: bool = False):

    if Y is None:
        Y = X

    if normalize_by_X:
        Xvol = np.ones((X.shape[0], 1), dtype=float)

    overlap = np.ones((X.shape[0], Y.shape[0]), dtype=float)

    for _, start, ext in zip(range(2), ["left", "top"], ["width", "height"]):

        Xmin = X[start].values[:, np.newaxis]
        Xmax = Xmin + X[ext].values[:, np.newaxis]

        if normalize_by_X:
            Xvol *= (Xmax - Xmin)

        Ymin = Y[start].values[:, np.newaxis]
        Ymax = Ymin + Y[ext].values[:, np.newaxis]

        Xmin, Ymin = np.meshgrid(Xmin, Ymin)
        Xmax, Ymax = np.meshgrid(Xmax, Ymax)

        init = Xmin * (Xmin >= Ymin) + Ymin * (Ymin > Xmin)
        end = Xmax * (Xmax <= Ymax) + Ymax * (Ymax < Xmax)

        overlap_ = end - init
        overlap_[overlap_ < 0] = 0

        overlap *= overlap_.T

    if normalize_by_X:
        overlap = overlap / Xvol

    return overlap


def label_csv_to_ocr_dataframe(csvfile):

    columns = ["labels", "left", "top", "width", "height", "file",
               "image_width", "image_height"]

    X = pandas.read_csv(csvfile, header=None)
    X.columns = columns

    X["x"] = (X["left"] + X["width"] / 2)
    X["y"] = (X["top"] + X["height"] / 2)

    X["text"] = X["labels"]

    return X


def add_labels(X: OCRDataFrame, y: pandas.DataFrame, min_overlap=0.9):

    X["labels"] = None

    if y.shape[0]:

        if "labels" not in y:
            raise KeyError(
                "DataFrame y must contain column 'labels' for label "
                "assignment associated with X!")

        overlap = rectangle_overlap(X, y)
        overlap[overlap < min_overlap] = 0

        i = np.arange(overlap.shape[0])
        j = np.argmax(overlap, axis=1)
        overlap = overlap[i, j]
        i = i[overlap > 0]
        j = j[overlap > 0]

        labels = y.iloc[j]
        X["labels"].iloc[i] = labels["labels"].values

    return X


def batch(function: callable, errors="ignore"):

    @wraps(function)
    def apply_to_batch(X):

        out = []
        for x in X:
            if errors == "ignore":
                try:
                    single = function(x)
                except:
                    continue
            elif errors == "print":
                try:
                    single = function(x)
                except Exception as e:
                    message = (
                        f"Error processing X = {x}:\n"
                        f"{e.__class__.__name__}({str(e)})"
                    )
                    out.append(message)
                    continue
            else:
                single = function(x)
            out.append(single)

        return out

    return apply_to_batch


def io_wrapper(
    function: callable,
    errors="ignore"):

    @wraps(function)
    def apply_to_batch(
        input_directory,
        output_directory
    ):

        for inputfile in os.listdir(input_directory):

            print(f"Processing inputfile {inputfile}...")

            if errors == "ignore":
                try:
                    x = os.path.join(
                        input_directory, 
                        inputfile
                    )
                    single = function(x)
                except:
                    continue
            elif errors == "print":
                try:
                    x = os.path.join(
                        input_directory, 
                        inputfile
                    )
                    single = function(x)
                except Exception as e:
                    message = (
                        f"Error processing X = {x}:\n"
                        f"{e.__class__.__name__}({str(e)})"
                    )
                    continue
            else:
                single = function(x)

            ParquetWriter(output_folder=output_directory).transform(single)

    return apply_to_batch


def strip_suffix(filename):

    return ".".join(
        filename.split(".")[:-1]
    )


def remove_surplus_images(table_directory, image_directory):

    table_files = [
        strip_suffix(file_) for file_ in os.listdir(table_directory)]

    for image_file in os.listdir(image_directory):
        if strip_suffix(image_file) not in table_files:
            print(f"Removing image file {image_file}...")
            os.remove(
            os.path.join(image_directory, image_file)
        )
