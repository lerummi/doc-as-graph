## Create Dashoard

### Prerequisites

You must have applied to transformation as documented [here](../transformations/README.md).

### Google Data Studio

1. Go to [Google Data Studio](https://datastudio.google.com/).

2. Select Google BigQuery Connector, enter `ProjectId=${GCP_PROJECT_ID}`,
   choose `Data set=${BIGQUERY_DATASET}`, `Table=embedding`. The variable names
   you had entered into the [root .env file](../.env)

3. Create a dashboard including e.g.

- Number of records per `documentType`
- Most common tokens per `documentType`
- An aggregation of token positions (Token Apex on image)
- OCR confidence per `documentType`
- etc.

Check out this [dashboard](https://datastudio.google.com/reporting/6bda51f6-6592-4d0f-af89-92de9789981b/page/sA1oC). If link not working, it is also
added to the [code](./Doc-as-graph.pdf)
