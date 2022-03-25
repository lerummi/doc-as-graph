import string
import pyspark
from pyspark.sql import functions as F
from pyspark.sql import types


def spacy_word2vec_grouped(cat_list):
    
    import spacy
    nlp = spacy.load('en_core_web_sm')
    
    output = list()
    for cat in cat_list:
        doc = nlp(cat[3])
        vector = doc.vector.tolist()
        if sum(vector) != 0.0:
            output.append((cat[0], cat[1], cat[2], cat[3], vector))
            

    return output


def remove_punctuation(texts):
    
    return texts.translate(
        str.maketrans("", "", string.punctuation)
    )


def lowercase(texts):
    
    return texts.lower()

spacy_word2vec_grouped_udf = F.udf(
    spacy_word2vec_grouped, 
    types.ArrayType(
        types.StructType([
            types.StructField('id', types.LongType()), 
            types.StructField("documentId", types.StringType()),
            types.StructField("documentType", types.StringType()),
            types.StructField('text', types.StringType()), 
            types.StructField('vector', types.ArrayType(types.DoubleType()))
        ])
    )
)


remove_punctuation_udf = F.udf(
    remove_punctuation, 
    returnType=types.StringType()
)


lowercase_udf = F.udf(
    lowercase, 
    returnType=types.StringType()
)
