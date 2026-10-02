"""
pipeline.py
-----------
Orquestra o pipeline ETL completo, em sequência: generate -> transform -> load.

Uso:
    python src/pipeline.py

Não usa nenhum orquestrador externo (Airflow/Prefect/Dagster) de propósito:
este é um projeto de portfólio focado em demonstrar a lógica do pipeline de
forma clara e legível, não uma infraestrutura de produção.
"""
from generate_data import generate_raw_sales, save_csv
from transform import run_transform
from load_s3 import load_to_s3


def main() -> None:
    print("=== ETAPA 1/3: EXTRACT (geração de dados sintéticos) ===")
    rows = generate_raw_sales()
    save_csv(rows)

    print("\n=== ETAPA 2/3: TRANSFORM (limpeza e agregação com pandas) ===")
    run_transform()

    print("\n=== ETAPA 3/3: LOAD (upload para S3 ou fallback local) ===")
    load_to_s3()

    print("\nPipeline concluído com sucesso.")


if __name__ == "__main__":
    main()
