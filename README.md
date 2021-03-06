# DOC-AS-GRAPH

Automatically evaluating document images is generally carried out using deep learning utilizing OCR + NLP methods, i.e. extracting text from them and trying to purely understand the
text.

Nowadays, also multi-modal evaluation will become a standard, using image and text information in a combined manner. However, still text and visual information is separated from each other, meaning the associated features are isolated.

This project, instead, goes back to an idea for understanding how documents are understood by humans: We analyze the visual information accompanied with the
text information including relative positions of known text patterns at once, rather than understanding the visual + text information separately and then combining this information like multi-model evaluation does. Our understanding
of documents is somewhat like interpreting a visual graph of text patterns.

Here, we aim to provide a data pipeline for creating the a basis for this manner: Data is downloaded, OCRed and stored in a data base. From here, there data graphs for training can be constructed, which is, however, out of scope for the project in the initial stage.

The following steps are carried out:

### Data Crawling

The web is full of document images suitable for extraction information. We use
Bing for downloading image sources to the local system.

### OCR

Downloaded images are OCRed and the text tokens incl. positions are carried out using [tesseract](https://github.com/tesseract-ocr/tesseract). The output is organized in parquet tables.

### Data ingestions

Images and tables are ingested into Google Cloud Storage and Google BigQuery.

### Transformations

The tables stored in Google BigQuery are concatenated and word embeddings are generated. This is carried out using `spark`.

### Visualization

From the concatenated data, some simple dashboards are created showing some insights about the data.

## Prerequisites

Create [Google Cloud account](https://cloud.google.com/docs/authentication/getting-started)
and place the JSON key file to `~/.google/credentials/google_credentials.json` so you
have full compatibility with the paths defined within this project.

## Getting Started

1. Set up Google Cloud infrastructure using terraform. Check out [README.md](./terraform/README.md).
2. Use Apache Airflow for data crawling, OCR and ingestion. Check out [README.md](./airflow/README.md).
3. Use spark to combine ingested data and compute word embeddings. Check out [README.md](./transformations/README.md).
4. Create some dashboards using Google Data Studio. Check out [README.md](./visualization/README.md).
