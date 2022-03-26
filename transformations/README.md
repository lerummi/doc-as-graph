# Generate word embeddings

In this step, we combine extracted tokens from the partitioned tables into
a single table and generate word embeddings. To do so, we use `spark` for
applying the transformation and `spacy` to generate word embeddings.

## Prerequisites

First carry out installation of spark.

### Linux

Here we'll show you how to install Spark 3.0.3 for Linux.
We tested it on Ubuntu 20.04 (also WSL), but it should work
for other Linux distros as well

#### Installing Java

Download OpenJDK 11 or Oracle JDK 11 (It's important that the version is 11 - spark requires 8 or 11)

We'll use [OpenJDK](https://jdk.java.net/archive/)

Download it (e.g. to `~/spark`):

```
wget https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz
```

Unpack it:

```bash
tar xzfv openjdk-11.0.2_linux-x64_bin.tar.gz
```

define `JAVA_HOME` and add it to `PATH`:

```bash
export JAVA_HOME="${HOME}/spark/jdk-11.0.2"
export PATH="${JAVA_HOME}/bin:${PATH}"
```

check that it works:

```bash
java --version
```

Output:

```
openjdk 11.0.2 2019-01-15
OpenJDK Runtime Environment 18.9 (build 11.0.2+9)
OpenJDK 64-Bit Server VM 18.9 (build 11.0.2+9, mixed mode)
```

Remove the archive:

```bash
rm openjdk-11.0.2_linux-x64_bin.tar.gz
```

#### Installing Spark

Download Spark. Use 3.0.3 version:

```bash
wget https://dlcdn.apache.org/spark/spark-3.0.3/spark-3.0.3-bin-hadoop3.2.tgz
```

Unpack:

```bash
tar xzfv spark-3.0.3-bin-hadoop3.2.tgz
```

Remove the archive:

```bash
rm spark-3.0.3-bin-hadoop3.2.tgz
```

Add it to `PATH`:

```bash
export SPARK_HOME="${HOME}/bin/spark-3.0.3-bin-hadoop3.2"
export PATH="${SPARK_HOME}/bin:${PATH}"
```

#### Testing Spark

Execute `spark-shell` and run the following:

```scala
val data = 1 to 10000
val distData = sc.parallelize(data)
distData.filter(_ < 10).collect()
```

#### Access BigQuery from spark

In order to access Google BigQuery using spark, you need to install the [spark-bigquery-connector](https://cloud.google.com/dataproc/docs/tutorials/bigquery-connector-spark-example). To do so, first install `gsutil` using

```
pip install gsutil
```

Now go to the directory `${SPARK_HOME}/jars` and

```
gsutil cp gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar .
gsutil cp gs://hadoop-lib/gcs/gcs-connector-hadoop2-2.1.1.jar .
```

in oder to obtain the bigquery & hadoop GCS connectors and make it accessible to the
spark session worker.

### PySpark

This document assumes you already have python.

To run PySpark, we first need to add it to `PYTHONPATH`:

```bash
export PYTHONPATH="${SPARK_HOME}/python/:$PYTHONPATH"
export PYTHONPATH="${SPARK_HOME}/python/lib/py4j-0.10.9-src.zip:$PYTHONPATH"
```

Make sure that the version under `${SPARK_HOME}/python/lib/` matches the filename of py4j or you will
encounter `ModuleNotFoundError: No module named 'py4j'` while executing `import pyspark`.

For example, if the file under `${SPARK_HOME}/python/lib/` is `py4j-0.10.9.3-src.zip`, then the
`export PYTHONPATH` statement above should be changed to

```bash
export PYTHONPATH="${SPARK_HOME}/python/lib/py4j-0.10.9.3-src.zip:$PYTHONPATH"
```

Now you can run Jupyter or IPython to test if things work. Go to some other directory, e.g. `~/tmp`.

Download a CSV file that we'll use for testing:

```bash
wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv
```

Now let's run `ipython` (or `jupyter notebook`) and execute:

```python
import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()

df = spark.read \
    .option("header", "true") \
    .csv('taxi+_zone_lookup.csv')

df.show()
```

Test that writing works as well:

```python
df.write.parquet('zones')
```

### Create data in BigQuery

In order to have data available for usage, ingest data to BigQuery following [this guide](../airflow.README.md).

## Create virtual environment and start jupyter-lab

To start, create a virtual environment in the root directory

```
cd ..
python -m venv env
```

activate and create environment from `requirements.txt` and start `jupyter-lab`:

```
source env/bin/activate
pip install -r requirements.txt
jupyterlab &
```

Now open the browser and open `http://localhost:8888`. Open notebook `transformations/generate_word_embeddings.ipynb` and run the cells. The output of the notebook should be
similar to [generate_word_embeddings.html](./generate_word_embeddings.html)
