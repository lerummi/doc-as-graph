
import os
import numpy as np
import datetime
from airflow import DAG
from airflow.models.param import Param
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCreateExternalTableOperator, 
    BigQueryInsertJobOperator
)
from docasgraph.config.general import Settings
from docasgraph.pipeline import image_to_table
from docasgraph.sources import Bing
from docasgraph.targets import upload_to_gcs
from docasgraph.utils import io_wrapper, remove_surplus_images


PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET")
BUCKET = os.environ.get("GCP_GCS_BUCKET")


bing = Bing(
    adult="off",
    timeout=60,
    search_delimiter=","
)

image_to_table_pipe = io_wrapper(
        image_to_table().transform,
        errors="print"
    )

params = {
    "keywords": Param(
        default="application, application letter, application example, application template",
        type="string",
        description=
            "Keys to search images for. Must be string "
            "of comma-separated keywords."
    ),
    "max_items": Param(
        default=100,
        type="integer", 
        description="Maximum number of items to be downloaded per search key."
    ),
    "save_key": Param(
        default="test",
        type="string", 
        description="Path to save images & data to."
    )
}


with DAG(
    dag_id="download_and_ocr_images",
    start_date=datetime.datetime.today(),
    schedule_interval=None,
    catchup=False,
    max_active_runs=10,
    params=params,
    render_template_as_native_obj=True,
    tags=["bing", "download", "ocr"]
) as dag:


    local_image_folder = os.path.join(
        Settings.IMAGES_DOWNLOAD_PATH, 
        "images",
        "{{ params.save_key }}"
    )

    local_tables_folder = os.path.join(
        Settings.IMAGES_DOWNLOAD_PATH, 
        "tables",
        "{{ params.save_key }}"
    )

    gcp_image_folder = os.path.join(
        "images",
        "{{ params.save_key }}"
    )

    gcp_tables_folder = os.path.join(
        "tables",
        "{{ params.save_key }}"
    )

    create_bq_table_query = (
        f"CREATE OR REPLACE TABLE {BIGQUERY_DATASET}"
        ".{{ params.save_key }}_partitioned " 
        "PARTITION BY DATE(execution_date) "
        "CLUSTER BY id, page_num, block_num AS "
        f"SELECT * FROM {BIGQUERY_DATASET}"
        ".{{ params.save_key }}_external"
    )

    keywords = "{{ params.keywords }}"

    download_links = PythonOperator(
        task_id="download_links",
        python_callable=bing.get_links,
        op_kwargs={
            "limit": "{{ params.max_items | int }}", 
            "query": keywords,
            "save": True
        }
    )

    download_images = PythonOperator(
        task_id=f"domnload_images",
        python_callable=bing.download_images,
        op_kwargs={
            "output_dir": local_image_folder
        }
    )

    image2table = PythonOperator(
        task_id=f"image_to_table",
        python_callable=image_to_table_pipe,
        op_args=(
            local_image_folder,
            local_tables_folder
        )
    )

    remove_surplus = PythonOperator(
        task_id="remove_surplus_images",
        python_callable=remove_surplus_images,
        op_args=(
            local_tables_folder,
            local_image_folder,
        )
    )

    local_to_gcs_images_task = PythonOperator(
        task_id="local_to_gcs_images_task",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "local_directory": local_image_folder,
            "target_directory": gcp_image_folder
        },
    )


    local_to_gcs_tables_task = PythonOperator(
        task_id="local_to_gcs_tables_task",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "local_directory": local_tables_folder,
            "target_directory": gcp_tables_folder
        },
    )

    bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "{{ params.save_key }}_external",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/{gcp_tables_folder}/*.parquet"],
            },
        },
    )

    bq_create_partitioned_table_job = BigQueryInsertJobOperator(
            task_id=f"bq_create_partitioned_table_task",
            configuration={
                "query": {
                    "query": create_bq_table_query,
                    "useLegacySql": False,
                }
            }
        )

    download_links >> \
    download_images >> \
    image2table >> \
    remove_surplus >> \
    local_to_gcs_images_task >> \
    local_to_gcs_tables_task >> \
    bigquery_external_table_task >> \
    bq_create_partitioned_table_job
