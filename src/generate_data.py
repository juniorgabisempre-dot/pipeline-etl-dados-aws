"""
generate_data.py
-----------------
Gera dados sintéticos de transações de vendas usando a biblioteca Faker.

Nenhum dado real é utilizado: nomes de produtos, categorias, regiões e
identificadores de clientes são todos gerados artificialmente a cada
execução (uma seed fixa garante reprodutibilidade).

Saída: data/raw_sales.csv (colunas: date, product, category, customer_id,
quantity, unit_price, region)
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

SEED = 42
N_ROWS = 1000

CATEGORIES = {
    "Eletrônicos": ["Fone de Ouvido", "Carregador Portátil", "Mouse Sem Fio",
                     "Teclado Mecânico", "Caixa de Som Bluetooth", "Smartwatch"],
    "Casa e Cozinha": ["Panela Antiaderente", "Liquidificador", "Jogo de Talheres",
                        "Air Fryer", "Cafeteira Elétrica"],
    "Papelaria": ["Caderno Universitário", "Kit Canetas", "Mochila Escolar",
                  "Agenda 2026", "Organizador de Mesa"],
    "Esporte e Lazer": ["Tênis de Corrida", "Garrafa Térmica", "Bola de Futebol",
                         "Tapete de Yoga", "Mochila de Trilha"],
    "Moda": ["Camiseta Básica", "Jaqueta Corta-Vento", "Boné", "Mochila Casual", "Óculos de Sol"],
}

REGIONS = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "raw_sales.csv"


def generate_raw_sales(n_rows: int = N_ROWS, seed: int = SEED) -> list[dict]:
    """Gera `n_rows` transações de venda sintéticas."""
    fake = Faker("pt_BR")
    Faker.seed(seed)
    random.seed(seed)

    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_span_days = (end_date - start_date).days

    rows = []
    for _ in range(n_rows):
        category = random.choice(list(CATEGORIES.keys()))
        product = random.choice(CATEGORIES[category])
        sale_date = start_date + timedelta(days=random.randint(0, date_span_days))

        # injeta algumas imperfeições propositais para o transform.py tratar
        quantity = random.choice([1, 1, 2, 2, 3, 4, 5, None])
        unit_price = round(random.uniform(15.90, 899.90), 2)

        rows.append({
            "date": sale_date.strftime("%Y-%m-%d"),
            "product": product,
            "category": category,
            "customer_id": fake.uuid4()[:8],
            "quantity": quantity,
            "unit_price": unit_price,
            "region": random.choice(REGIONS),
        })

    # duplica ~2% das linhas de propósito (dado real raramente é perfeito)
    n_dupes = max(1, n_rows // 50)
    rows.extend(random.sample(rows, n_dupes))
    random.shuffle(rows)
    return rows


def save_csv(rows: list[dict], path: Path = OUTPUT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"[generate_data] {len(rows)} linhas geradas em {path}")


if __name__ == "__main__":
    data = generate_raw_sales()
    save_csv(data)
