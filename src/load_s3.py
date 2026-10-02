"""
load_s3.py
----------
Etapa de carga (L do ETL): envia o arquivo transformado para um bucket
S3 usando boto3.

Este script é pensado para funcionar em dois modos, sem exigir nenhuma
configuração extra para ser demonstrado:

  - Modo AWS: se as variáveis de ambiente AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY e S3_BUCKET_NAME estiverem definidas, o
    arquivo é enviado para o bucket informado, em s3://<bucket>/sales/.

  - Modo local (fallback): se as credenciais/bucket não estiverem
    presentes, ou se o upload falhar por qualquer motivo (permissão,
    bucket inexistente, sem internet etc.), o script simplesmente copia
    o arquivo para a pasta local `output/` e imprime um aviso claro.
    Isso garante que o pipeline sempre roda de ponta a ponta, mesmo sem
    uma conta AWS configurada.
"""
import os
import shutil
from pathlib import Path

SOURCE_FILE = Path(__file__).resolve().parent.parent / "data" / "daily_revenue_by_category_region.csv"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
S3_KEY = "sales/daily_revenue_by_category_region.csv"


def _load_local_fallback(source: Path, reason: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT_DIR / source.name
    shutil.copyfile(source, destination)
    print(f"[load_s3] AVISO: {reason}")
    print(f"[load_s3] Executando em modo local. Arquivo salvo em {destination}")
    return destination


def load_to_s3(source: Path = SOURCE_FILE) -> Path:
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    bucket_name = os.getenv("S3_BUCKET_NAME")

    if not (access_key and secret_key and bucket_name):
        return _load_local_fallback(
            source,
            "credenciais AWS ou S3_BUCKET_NAME não encontrados nas variáveis de "
            "ambiente (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME).",
        )

    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError

        s3 = boto3.client("s3")
        s3.upload_file(str(source), bucket_name, S3_KEY)
        print(f"[load_s3] Upload concluído: s3://{bucket_name}/{S3_KEY}")
        return source
    except ImportError:
        return _load_local_fallback(source, "boto3 não está instalado.")
    except (BotoCoreError, ClientError, Exception) as exc:  # noqa: BLE001
        return _load_local_fallback(source, f"falha no upload para S3 ({exc}).")


if __name__ == "__main__":
    load_to_s3()
