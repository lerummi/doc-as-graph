# Data crawling and push to cloud using Airflow

The first step of the workflow is to crawl data from Bing and ingest this data into Google Cloud Storage and BigQuery. We utilize Airflow for this procedure.

## Prerequisities

To be able to carry out the following steps, first

- Follow the **Prerequisies** stated in the project root directory and
- User **terraform** (parallel directory) to build your cloud environment if not available.

## Start Airflow Webserver

Use the provided docker-compose file in the project root directory to build and run airflow. Environmental variables should be fine, when specified in the `.env` file.

```
../docker-compose up --build
```

Build should take a while.

## Airflow UI

1. When successfully running the docker containers, open your web-browser and navigate to http://localhost:8080.
2. Login using the `user=airflow` and `password=airflow` and open the `download_and_ocr_images` DAG item. This dag is configured to only run once when triggered.
3. Click the `|>` button and `Trigger DAG w/ config`. You can specify the image `keywords` to search for (provide comma-separated list to apply multiple queries) as well `max_items` i.e. as the number of images to download per query. The `save_key` string defines the output object name, i.e. an identier for the Google Cloud Storage bucket folder & the BigQuery (partitioned) table for storing the tokens extracted from the images after OCR.
4. Click `Trigger` to launch the process.
5. Repeat the process multiple times using different `keywords` and `save_key` to download and ingest data associated with different document types.

**Note: Sometimes the DAG gets stuck right at the beginning, stating `Status: success` without doing anything. If so, delete the DAG (waste bin at the rhs) wait a few seconds, refresh and start from 3. again. I think this has something to do with the `start_date` but did not figure out a solution for now.**

### Explanation: Clustering and partitioning the output table

Partitioning: execution_data -> for fast querying by insert date frames
Clustering:

- documentId -> Filter for specific documents
- pageNum -> Filter for specific document pages
- blockNum -> Filter for specific boxes in documents

### Usage Example

In step 3. use the following queries subsequently to ingest documents for

- **application letters**

```
{
    "keywords": "application, application letter, application example, application template",
    "max_items": 15,
    "save_key": "application"
}
```

- **invoice letters**

```
{
    "keywords": "invoice, invoice letter, invoice example, invoice template",
    "max_items": 15,
    "save_key": "invoice"
}
```

- **termination letters**

```
{
    "keywords": "termination, termination letter, termination example, termination template",
    "max_items": 20,
    "save_key": "termination"
}
```

Depending on your internet connection, this may take a while.
When running locally, the downloaded images can be found in your `/tmp/docs/images/{save_key}` directories.
In the end partitioned tables **{save_key}\_partitioned** are created, containing the OCRed results. These can be transformed furtheron using spark (checkout `../spark/README.md`)
