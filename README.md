\# Log Analyzer



A security-focused log analysis pipeline that parses web server logs, loads them into BigQuery, and identifies suspicious activity.



\## Overview



This project:

1\. Downloads Apache web server access logs

2\. Parses raw log lines into structured data

3\. Loads the data into Google BigQuery

4\. Analyzes traffic patterns and detects potential security threats



\## What You Can Detect



\- \*\*Bot activity\*\*: IPs making unusually high numbers of requests

\- \*\*WordPress attacks\*\*: Scans for `/wp-login.php`, `/wp-admin/`

\- \*\*Admin probing\*\*: Attempts to access `/admin`, `/administrator`

\- \*\*Injection attempts\*\*: Suspicious characters in URLs

\- \*\*Unusual patterns\*\*: Single IPs hitting the same page repeatedly



\## Log Format



Apache Common Log Format:

```

83.149.9.216 - - \[17/May/2015:10:05:03 +0000] "GET /path HTTP/1.1" 200 203023

```



Fields parsed:

\- `ip`: Client IP address

\- `timestamp`: Request time

\- `method`: HTTP method (GET, POST, etc.)

\- `path`: Requested URL path

\- `status`: HTTP response code

\- `size`: Response size in bytes



\## Setup



1\. Clone the repository

2\. Create virtual environment: `python -m venv venv`

3\. Activate: `venv\\Scripts\\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)

4\. Install dependencies: `pip install -r requirements.txt`

5\. Copy `.env.example` to `.env` and add your Google Cloud project ID

6\. Add your `service-account.json` file



\## Usage



Extract and parse logs:

```bash

python -m log\_analyzer.extract

```



Load to BigQuery:

```bash

python -m log\_analyzer.load

```



Then run queries from `sql/analysis.sql` in BigQuery console.



\## Sample Findings



From analyzing 10,000 log entries:

\- 1,753 unique visitors

\- 1,498 unique pages accessed

\- Multiple IPs attempting WordPress admin access

\- Bot making 364 requests to single RSS feed



\## Project Structure

```

log-analyzer/

├── log\_analyzer/

│   ├── \_\_init\_\_.py

│   ├── extract.py      # Download and parse logs

│   └── load.py         # Load to BigQuery

├── sql/

│   └── analysis.sql    # Security analysis queries

├── data/               # Downloaded log files

├── .env.example

├── requirements.txt

└── README.md

```



\## Technologies



\- Python (pandas, requests, regex)

\- Google BigQuery

\- SQL

