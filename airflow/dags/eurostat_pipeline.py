from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="Eurostat_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    task_1 = BashOperator(
        task_id="Extract_pipline",
        bash_command="docker run --rm -v /run/desktop/mnt/host/c/Users/Hp/Desktop/THESIS/CODE/output:/app/output code-extract migr_asyapp1mp"
    )

    task_2 = BashOperator(
        task_id="Transform_pipline",
        bash_command="docker run --rm -v /run/desktop/mnt/host/c/Users/Hp/Desktop/THESIS/CODE/output:/app/output code-transform migr_asyapp1mp"
    )


    task_1 >> task_2