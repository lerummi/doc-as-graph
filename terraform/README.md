### Concepts

- [Terraform_overview](../1_terraform_overview.md)
- [Audio](https://drive.google.com/file/d/1IqMRDwJV-m0v9_le_i2HA_UbM_sIWgWx/view?usp=sharing)

### Prerequisities

In order to be able to utilize terraform for constructing your GC
infrastructure, create a .env file in the root folder (check the [.env.dist](../.env.dist) as
template) and at least set the following variables

```
GCP_PROJECT_ID=
GCP_GCS_BUCKET=
BIGQUERY_DATASET=

TF_VAR_region=  # GC region
TF_VAR_project=  # Same as GCP_PROJECT_ID, however, can not be inherited from variable above
TF_VAR_BQ_DATASET=  # Same as BIGQUERY_DATASET, however, can not be inherited from variable above
TF_VAR_bucket=  # Same as BIGQUERY_DATASET, however, can not be inherited from variable above
```

To read from the file, within your terminal run the script

```
source ./read_dotenv.sh
```

### Execution

```shell
# Refresh service-account's auth-token for this session
gcloud auth application-default login &

# Initialize state file (.tfstate)
terraform init

# Check changes to new infra plan
terraform plan
```

```shell
# Create new infra
terraform apply
```

```shell
# Delete infra after your work, to avoid costs on any running services
terraform destroy
```
