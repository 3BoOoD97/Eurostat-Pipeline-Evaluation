import sys
from pathlib import Path

import duckdb


def sql_path(path: Path) -> str:
    """Prepare a safe file path for DuckDB SQL."""
    return str(path.resolve()).replace("'", "''")


def get_schema(connection, relation: str):
    result = connection.execute(
        f"DESCRIBE SELECT * FROM {relation}"
    ).fetchall()

    return [
        (row[0], row[1])
        for row in result
    ]


def get_null_counts(connection, relation: str, columns):
    expressions = []

    for column in columns:
        safe_column = column.replace('"', '""')

        expressions.append(
            f'SUM(CASE WHEN "{safe_column}" IS NULL '
            f'THEN 1 ELSE 0 END) AS "{safe_column}"'
        )

    query = (
        "SELECT "
        + ", ".join(expressions)
        + f" FROM {relation}"
    )

    result = connection.execute(query).fetchone()

    return dict(zip(columns, result))


def main():
    dataset_name = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "migr_asyappctzm_100"
    )

    project_root = Path(__file__).resolve().parent
    processed_dir = project_root / "output" / "processed"

    memory_file = (
        processed_dir
        / f"{dataset_name}_processed.parquet"
    )

    chunked_file = (
        processed_dir
        / f"{dataset_name}_chunked_processed.parquet"
    )

    print("=" * 70)
    print(f"Validating dataset: {dataset_name}")
    print("=" * 70)

    missing_files = [
        str(path)
        for path in [memory_file, chunked_file]
        if not path.exists()
    ]

    if missing_files:
        print("FAILED: The following output files are missing:")

        for path in missing_files:
            print(f"- {path}")

        sys.exit(1)

    connection = duckdb.connect()

    memory_relation = (
        f"read_parquet('{sql_path(memory_file)}')"
    )

    chunked_relation = (
        f"read_parquet('{sql_path(chunked_file)}')"
    )

    # 1. Compare row counts
    memory_rows = connection.execute(
        f"SELECT COUNT(*) FROM {memory_relation}"
    ).fetchone()[0]

    chunked_rows = connection.execute(
        f"SELECT COUNT(*) FROM {chunked_relation}"
    ).fetchone()[0]

    rows_match = memory_rows == chunked_rows

    print("\n1. Row count")
    print(f"In-Memory : {memory_rows:,}")
    print(f"Chunked   : {chunked_rows:,}")
    print(f"Result    : {'MATCH' if rows_match else 'MISMATCH'}")

    # 2. Compare schema
    memory_schema = get_schema(
        connection,
        memory_relation,
    )

    chunked_schema = get_schema(
        connection,
        chunked_relation,
    )

    schema_match = memory_schema == chunked_schema

    print("\n2. Schema")
    print(
        f"Result    : "
        f"{'MATCH' if schema_match else 'MISMATCH'}"
    )

    if not schema_match:
        print("\nIn-Memory schema:")

        for column in memory_schema:
            print(column)

        print("\nChunked schema:")

        for column in chunked_schema:
            print(column)

    # 3. Compare null counts
    memory_columns = [
        column_name
        for column_name, _ in memory_schema
    ]

    nulls_match = False

    if schema_match:
        memory_nulls = get_null_counts(
            connection,
            memory_relation,
            memory_columns,
        )

        chunked_nulls = get_null_counts(
            connection,
            chunked_relation,
            memory_columns,
        )

        nulls_match = memory_nulls == chunked_nulls

        print("\n3. Null counts")
        print(
            f"Result    : "
            f"{'MATCH' if nulls_match else 'MISMATCH'}"
        )

        if not nulls_match:
            for column in memory_columns:
                if memory_nulls[column] != chunked_nulls[column]:
                    print(
                        f"{column}: "
                        f"In-Memory={memory_nulls[column]}, "
                        f"Chunked={chunked_nulls[column]}"
                    )

    # 4. Exact comparison independent of row order
    exact_match = False
    memory_only_rows = None
    chunked_only_rows = None

    if schema_match:
        memory_only_rows = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT *
                FROM {memory_relation}

                EXCEPT ALL

                SELECT *
                FROM {chunked_relation}
            ) AS differences
            """
        ).fetchone()[0]

        chunked_only_rows = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT *
                FROM {chunked_relation}

                EXCEPT ALL

                SELECT *
                FROM {memory_relation}
            ) AS differences
            """
        ).fetchone()[0]

        exact_match = (
            memory_only_rows == 0
            and chunked_only_rows == 0
        )

        print("\n4. Exact content comparison")
        print(
            f"Rows only in In-Memory : "
            f"{memory_only_rows:,}"
        )
        print(
            f"Rows only in Chunked   : "
            f"{chunked_only_rows:,}"
        )
        print(
            f"Result                 : "
            f"{'MATCH' if exact_match else 'MISMATCH'}"
        )

    # 5. Check aggregate codes
    print("\n5. Geographical aggregate check")

    aggregate_result = connection.execute(
        f"""
        SELECT
            country_code,
            is_aggregate,
            COUNT(*) AS row_count
        FROM {memory_relation}
        WHERE country_code IN (
            'EU27_2020',
            'EA',
            'EA19',
            'EA20',
            'EU28'
        )
        GROUP BY
            country_code,
            is_aggregate
        ORDER BY
            country_code
        """
    ).fetchall()

    if aggregate_result:
        for country_code, is_aggregate, row_count in aggregate_result:
            print(
                f"{country_code}: "
                f"is_aggregate={is_aggregate}, "
                f"rows={row_count:,}"
            )
    else:
        print("No selected aggregate codes were found.")

    overall_match = (
        rows_match
        and schema_match
        and nulls_match
        and exact_match
    )

    print("\n" + "=" * 70)

    if overall_match:
        print("FINAL RESULT: PASS")
        print(
            "In-Memory and Chunked outputs are equivalent."
        )
    else:
        print("FINAL RESULT: FAIL")
        print(
            "The outputs are not fully equivalent."
        )

    print("=" * 70)

    connection.close()

    if not overall_match:
        sys.exit(1)


if __name__ == "__main__":
    main()