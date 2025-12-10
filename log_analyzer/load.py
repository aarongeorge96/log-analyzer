import pandas as pd
from google.cloud import bigquery
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
DATA_DIR = Path(__file__).parent.parent / "data"
DATASET_NAME = "web_logs"


def get_client():
    """Create BigQuery client."""
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH
    return bigquery.Client(project=PROJECT_ID)


def create_dataset(client):
    """Create dataset if it doesn't exist."""
    dataset_id = f"{PROJECT_ID}.{DATASET_NAME}"
    
    try:
        client.get_dataset(dataset_id)
        print(f"Dataset {DATASET_NAME} already exists")
    except Exception:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        client.create_dataset(dataset)
        print(f"Created dataset {DATASET_NAME}")


def load_table(client, filename, table_name):
    """Load a parquet file into a BigQuery table."""
    filepath = DATA_DIR / filename
    
    if not filepath.exists():
        print(f"File not found: {filepath}")
        return
    
    df = pd.read_parquet(filepath)
    
    table_id = f"{PROJECT_ID}.{DATASET_NAME}.{table_name}"
    
    job_config = bigquery.LoadJobConfig()
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
    
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    
    print(f"Loaded {len(df)} rows into {table_name}")


if __name__ == "__main__":
    client = get_client()
    
    create_dataset(client)
    
    load_table(client, "nasa_logs.parquet", "access_logs")
    
    print()
    print("Load complete!")