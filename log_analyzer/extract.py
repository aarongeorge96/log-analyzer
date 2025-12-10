import requests
import gzip
import re
import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"

# Nasa log file URL
LOG_URL = "ftp://ita.ee.lbl.gov/traces/NASA_access_log_Jul95.gz"

# Backup URL in case FTP doesn't work
BACKUP_URL = "https://raw.githubusercontent.com/elastic/examples/master/Common%20Data%20Formats/apache_logs/apache_logs"

# Download the NASA log file
def download_logs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DATA_DIR / "nasa_log.txt"

    if filepath.exists():
        print(f"Log file already exists: {filepath}")
        return filepath
    print("Downloading NASA logs...")

    try:
        response = requests.get(BACKUP_URL, timeout=30)
        response.raise_for_status()

        with open(filepath, "w", encoding="utf-8", errors="ignore") as f:
            f.write(response.text)

        print(f"Downloaded: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error downloading: {e}")
        return None
"""
Parse a single log line in Apache Common Log Format.
    
Example line:
199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/apollo/ HTTP/1.0" 200 6245
    
Fields:
- IP address: who made the request
- identd: usually "-" (not used)
- userid: usually "-" (not authenticated)
- timestamp: when the request happened
- request: what they asked for (method, path, protocol)
- status: HTTP response code (200=OK, 404=not found, etc.)
- size: bytes returned
"""

def parse_log_line(line):
    # Regex pattern for Apache Common Log Format
    pattern = r'^(\S+) \S+ \S+ \[([^\]]+)\] "([^"]*)" (\d{3}|-) (\d+|-)'
    match = re.match(pattern, line)
    if not match:
        return None

    ip, timestamp, request, status, size = match.groups()

    # Parse the request into method, path, protocol
    request_parts = request.split(" ")
    if len(request_parts) >= 2:
        method = request_parts[0]
        path = request_parts[1]
    else:
        method = ""
        path = request

    # Convert status and size to integers
    status = int(status) if status != "-" else None
    size = int(size) if size != "-" else 0

    return {
        "ip": ip,
        "timestamp": timestamp,
        "method": method,
        "path": path,
        "status": status,
        "size": size,
        "raw_request": request
    }

# Parse all log lines into a dataframe
def parse_logs(filepath):
    print(f"Parsing {filepath}...")
    parsed_lines = []
    errors = 0
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            parsed = parse_log_line(line)
            if parsed:
                parsed_lines.append(parsed)
            else:
                errors += 1
            if (i + 1) % 100000 == 0:
                print(f"Processed {i + 1} lines...")
    print(f"Parsed {len(parsed_lines)} lines, {errors} errors")
    df = pd.DataFrame(parsed_lines)
    df["extracted_at"] = datetime.now()
    return df

def save_to_parquet(df, filename="nasa_logs.parquet"):
    """Save parsed logs to parquet."""
    filepath = DATA_DIR / filename
    df.to_parquet(filepath, index=False)
    print(f"Saved: {filepath}")
    return filepath

if __name__ == "__main__":
    log_file = download_logs()
    
    if log_file:
        df = parse_logs(log_file)
        
        print()
        print("Sample data:")
        print(df.head())
        
        print()
        save_to_parquet(df)
        
        print()
        print("Extraction complete!")

