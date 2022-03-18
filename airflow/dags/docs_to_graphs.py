
import os
import numpy as np
import datetime
from airflow import DAG
from airflow.models.param import Param
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from datasdoc.config.general import Settings
from datasdoc.pipeline import image_to_table
from datasdoc.sources import Bing
from datasdoc.utils import batch


#local_image_folder = os.path.join(
#    Settings.IMAGES_DOWNLOAD_PATH, 
#    "images",
#    "Rechnung"
#)

#local_tables_folder = os.path.join(
#    Settings.IMAGES_DOWNLOAD_PATH, 
#    "tables",
#    "Rechnung"
#)

#keywords = [
#    "Rechnung",
#    "Rechnung Beispiel",
#    "Rechnung Brief",
#    "Rechnung Muster",
#    "Musterbrief Rechnung"
#]

max_items = 1000

params = {
    "keywords": Param(
        default="Rechnung, Rechnung Beispiel, Rechnung Brief, Musterbrief Rechnung",
        type="string",
        description=
            "Keys to search images for. Must be string "
            "of comma-separated keywords."
    ),
    "save_key": Param(
        default="test",
        type="string", 
        description="Path to save images & data to."
    )
}


with DAG(
    dag_id="download_images",
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
        "{{ dag_run.conf['save_key'] }}"
    )

    local_tables_folder = os.path.join(
        Settings.IMAGES_DOWNLOAD_PATH, 
        "tables",
        "{{ dag_run.conf['save_key'] }}"
    )

    pipe = batch(
        image_to_table(output_folder=local_tables_folder)
        .transform,
        errors="print"
    )

    keywords = "{{ params.keywords }}"

    links_buffer = []

    for keyword in keywords:
        bing = Bing(
            query=keyword, 
            limit=max_items,
            output_dir=local_image_folder,
            adult="off",
            timeout=60
        )

        for start_at in np.arange(0, max_items, 150):
            links = bing.get_links(start_at=start_at)
            links_buffer += links
        links_buffer = list(set(links_buffer))

    local_image_files = []
    for file in links_buffer:
        tmp = bing.filename(file, file.split(".")[-1])
        tmp = os.path.join(local_image_folder, tmp)
        local_image_files.append(tmp)

    download_images = PythonOperator(
        task_id=f"domnload_images",
        python_callable=bing.download_images,
        op_kwargs={"links": links_buffer}
    )

    image2table = PythonOperator(
        task_id=f"image_to_table",
        python_callable=pipe,
        op_args=(local_image_files, )
    )

    download_images >> image2table
