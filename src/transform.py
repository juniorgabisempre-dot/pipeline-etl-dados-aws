"""
transform.py
------------
Etapa de transformação (T do ETL): limpa os dados brutos de vendas com
pandas e gera uma agregação de receita diária por categoria e região.

Regras de limpeza aplicadas:
  1. Remove linhas duplicadas.
  2. Remove linhas com quantidade nula (não é possível calcular receita).
  3. Garante tipos corretos (date -> datetime, quantity -> int).
  4. Calcula a coluna derivada `revenue` = quantity * unit_price.

Saída: data/daily_revenue_by_category_region.csv
"""
from pathlib import Path

import pandas as pd

RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "raw_sales.csv"
CLEAN_PATH = Path(__file__).resolve().parent.parent / "data" / "clean_sales.csv"
AGG_PATH = Path(__file__).resolve().parent.parent / "data" / "daily_revenue_by_category_region.csv"


def clean(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    df = df.drop_duplicates()
    df = df.dropna(subset=["quantity"])

    df["date"] = pd.to_datetime(df["date"])
    df["quantity"] = df["quantity"].astype(int)
    df["unit_price"] = df["unit_price"].astype(float)

    df["revenue"] = df["quantity"] * df["unit_price"]

    after = len(df)
    print(f"[transform] limpeza: {before} -> {after} linhas "
          f"({before - after} removidas por duplicidade/nulos)")
    return df


def aggregate_daily_revenue(df: pd.DataFrame) -> pd.DataFrame:
    agg = (
        df.groupby([pd.Grouper(key="date", freq="D"), "category", "region"])["revenue"]
        .sum()
        .reset_index()
        .sort_values("date")
    )
    agg["revenue"] = agg["revenue"].round(2)
    return agg


def run_transform(raw_path: Path = RAW_PATH) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_raw = pd.read_csv(raw_path)
    df_clean = clean(df_raw)
    df_agg = aggregate_daily_revenue(df_clean)

    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(CLEAN_PATH, index=False)
    df_agg.to_csv(AGG_PATH, index=False)
    print(f"[transform] dados limpos salvos em {CLEAN_PATH}")
    print(f"[transform] agregação salva em {AGG_PATH}")

    return df_clean, df_agg


if __name__ == "__main__":
    run_transform()
