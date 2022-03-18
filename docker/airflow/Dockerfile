# First-time build can take upto 10 mins.

FROM apache/airflow:2.2.3

ENV AIRFLOW_HOME=/opt/airflow

ARG DOCKER_DIRECTORY ${DOCKER_DIRECTORY}

USER root

RUN apt-get update -qq && \
    apt-get install vim -qqq && \
    apt-get install --no-install-recommends -y \
    build-essential && \
    apt-get autoremove -yqq --purge && \
    apt-get clean && \
    apt-get install -y tesseract-ocr tesseract-ocr-deu && \
    apt-get install ffmpeg libsm6 libxext6 -y && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ${AIRFLOW_HOME}/
COPY ${CODE_DIRECTORY} ${AIRFLOW_HOME}/

# Ref: https://airflow.apache.org/docs/docker-stack/recipes.html

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

ARG CLOUD_SDK_VERSION=322.0.0
ENV GCLOUD_HOME=/home/google-cloud-sdk

ENV PATH="${GCLOUD_HOME}/bin/:${PATH}"
ENV PYTHONPATH="${PYTHONPATH}:${AIRFLOW_HOME}/src/"

RUN DOWNLOAD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/google-cloud-sdk.tar.gz" \
    && mkdir -p "${GCLOUD_HOME}" \
    && tar xzf "${TMP_DIR}/google-cloud-sdk.tar.gz" -C "${GCLOUD_HOME}" --strip-components=1 \
    && "${GCLOUD_HOME}/install.sh" \
       --bash-completion=false \
       --path-update=false \
       --usage-reporting=false \
       --quiet \
    && rm -rf "${TMP_DIR}" \
    && gcloud --version

COPY ./docker/airflow/scripts/entrypoint.sh ${AIRFLOW_HOME}/entrypoint.sh

RUN chmod +x ${AIRFLOW_HOME}/entrypoint.sh

WORKDIR ${AIRFLOW_HOME}

USER ${AIRFLOW_UID}

RUN pip install --no-cache-dir --user -r requirements.txt

RUN python -m spacy download de_core_news_sm
RUN python -m spacy download en_core_web_sm
