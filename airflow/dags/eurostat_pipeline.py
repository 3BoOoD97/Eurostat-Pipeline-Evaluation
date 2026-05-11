import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.python import BranchPythonOperator
from airflow.providers.standard.operators.bash import BashOperator

OUTPUT_PATH = os.getenv(
    "EUROSTAT_OUTPUT_VOLUME",
    "/run/desktop/mnt/host/c/Users/Hp/Desktop/THESIS/CODE/output:/app/output"
)


# Dataset configuration dictionary
DATASETS_CONFIG = {
    "migr_asyappctzm": { # Monthly data about asylum applicants
        "schedule": "0 0 1,15 * *",  # Run on day 1 and 15 each month
        "description": "Monthly Asylum Applications",
        "tags": ["eurostat", "monthly", "asylum"]
    },
    "migr_asyappctza": {  # Annual data about asylum applicants
        "schedule": "0 0 1 * *",  # Run every first day of each month
        "description": "Annual Asylum Applications",
        "tags": ["eurostat", "annual", "asylum"]
    },
    "migr_asydcfsta": { # Asylum decisions by citizenship, age, sex, and decision type.
        "schedule": "0 0 1 * *",  # Run every first day of each month
        "description": "Decisions",
        "tags": ["eurostat", "decisions", "asylum"]
    },
    "migr_asyapp1mp": { # Asylum applicants per 1,000 inhabitants
        "schedule": "0 0 1 * *",  # Run every first day of each month
        "description": "First-time asylum applicants per 1000",
        "tags": ["eurostat", "annual", "indicator"]
    }
}

# Function to check if the data needs update or not
def decide_if_transform (dataset_name, **kwargs):
    ti = kwargs["ti"]
    # Pull the last line of the output command
    status = (ti.xcom_pull(task_ids="extract_pipeline") or "").strip()

    processed_parquet = f"/opt/airflow/output/processed/{dataset_name}_processed.parquet"
    processed_csv = f"/opt/airflow/output/processed/{dataset_name}_processed.csv"

    if status == "UPDATED=true":
        return 'transform_pipeline'
    if not os.path.exists(processed_csv) or not os.path.exists(processed_parquet):
        return 'transform_pipeline'
    else:
        return 'skip_transform'


DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# Loop through all datasets in the configuration dictionary
for dataset_name, config in DATASETS_CONFIG.items():
    with DAG(
            dag_id=f"eurostat_{dataset_name}",
            default_args=DEFAULT_ARGS,
            start_date=datetime(2026, 1, 1),
            schedule=config["schedule"],
            catchup=False,
            max_active_runs=1,
            tags=config["tags"],
            description=config["description"],
    ) as dag:


        extract_pipeline = BashOperator(
            task_id="extract_pipeline",
            bash_command=f"docker run --rm -v {OUTPUT_PATH} code-extract {dataset_name}",
            do_xcom_push=True, # To save the last line of the output to xcom
        )

        transform_pipeline = BashOperator(
            task_id="transform_pipeline",
            bash_command=f"docker run --rm -v {OUTPUT_PATH} code-transform {dataset_name}",
        )

        skip_transform = EmptyOperator(
            task_id="skip_transform",
        )

        check_update = BranchPythonOperator(
            task_id="check_update",
            op_kwargs={"dataset_name": dataset_name},
            python_callable=decide_if_transform,
        )

        extract_pipeline >> check_update >> [transform_pipeline, skip_transform]

    globals()[dag.dag_id] = dag

