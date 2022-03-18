from multiprocessing.sharedctypes import Value
from sklearn.pipeline import Pipeline

from .sources import ImageSource
from .preprocessing import OtsuThreshold
from .feature_extraction import (
    TesseractOCR,
    SpacyWordEmbedding
)
from .targets import ParquetWriter

def image_to_table(
    language="eng+deu", 
    output_folder="/tmp"
    ):

    if language not in ["eng", "deu", "eng+deu"]:
        raise ValueError(
            "Currently only english or german models "
            "are available, i.e. set language to "
            "'eng' or 'deu'"
        )
    
    elif language == "eng":
        tesseract_lang = "eng"
        spacy_model = "en_core_web_sm"
    
    elif language == "deu":
        tesseract_lang = "deu"
        spacy_model = "de_core_news_sm"
    elif language == "eng+deu":
        tesseract_lang = "eng+deu"
        spacy_model = "de_core_news_sm"

    return Pipeline([
        ("load", ImageSource(gray=True)),
        ("preprocess", OtsuThreshold()),
        ("ocr", TesseractOCR(lang=tesseract_lang)),
        ("embedding", SpacyWordEmbedding(spacy_model)),
        ("write", ParquetWriter(output_folder=output_folder))
    ])
