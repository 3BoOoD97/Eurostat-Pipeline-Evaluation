from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.python import BranchPythonOperator
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime

DATASET_NAME= "migr_asydcfsta"
OUTPUT_PATH = "/run/desktop/mnt/host/c/Users/Hp/Desktop/THESIS/CODE/output:/app/output"

def decide_if_transform(ti):
    # Get the last line of extract_pipeline task
    update_status = ti.xcom_pull(task_ids="extract_pipeline")
    if update_status == "UPDATED=false":
        return "skip_transform"
    else:
        return "transform_pipeline"

with DAG(
    dag_id="Eurostat_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    extract_pipeline = BashOperator(
        task_id="extract_pipeline",
        bash_command=f"docker run --rm -v {OUTPUT_PATH} code-extract {DATASET_NAME}",
        # Save the last line of the output
        do_xcom_push = True,
    )

    transform_pipeline = BashOperator(
        task_id="transform_pipeline",
        bash_command=f"docker run --rm -v {OUTPUT_PATH} code-transform {DATASET_NAME}"
    )

    skip_transform = EmptyOperator(
        task_id="skip_transform"
    )

    check_update = BranchPythonOperator(
        task_id="check_update",
        python_callable=decide_if_transform,
    )

    extract_pipeline >> check_update >> [transform_pipeline, skip_transform]