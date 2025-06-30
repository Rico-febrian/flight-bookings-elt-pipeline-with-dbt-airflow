# 🏁 Getting Started: Build an End-to-End ELT Pipeline with Airflow and dbt

**Welcome to my Learning Logs!** 

This project is part of my hands-on learning journey as I transition into Data Engineering. It demonstrates how to build an ELT pipeline using **Apache Airflow**, **DBT**, **PostgreSQL**, and **MinIO**.

---

## 🧠 Project Overview

This project demonstrates how to:

- Extract data from a source database to MinIO (object storage) as a data lake.
  
- Load the extracted data into a staging schema in warehouse database.

- Transform it into a final schema using DBT and

- Orchestrate the entire ELT process with Apache Airflow (Celery Executor)

- Setup DBT DAG, set variables/connections, and trigger downstream DAGs

- Send alerts via Slack using Webhooks
    
---

## 🔄 How the Pipeline Works

![elt-design](https://github.com/Rico-febrian/flight-bookings-elt-pipeline-with-dbt-airflow/blob/main/picts/elt-airflow-dbt.png)

- **Extract Task**: Pulls raw data from the source database and saves it as CSV files in MinIO.

- **Load Task**: Loads those CSV files from MinIO into the staging schema in the data warehouse.

- **Transform Task**: Runs DBT to transform staging data into final schema.

---

## ⚙️ Requirements

Before getting started, make sure your machine meets the following:

- Memory:
  Minimum 8GB RAM (Recommended: 16GB+, especially for Windows. On Linux, 8GB should be sufficient.)

- Docker (with WSL2 enabled if you're on Windows)

- Python 3.7+ (for generating Fernet key)

- Database Client (DBeaver or any PostgreSQL-compatible SQL client)

---

## 📁 Project Structure

```
elt-airflow-project/
├── dags/
│   └── flights_staging/             # Main DAG script
|   |   └── tasks/                   # Main task scripts
|   |       └── components           # Core task scripts (extract, load, transform)
│   └── flights_staging/             # Main DAG script
│   |   └── flights_dbt/             # Main DBT DAG
│   └── helper/                      # Helper functions (callbacks, utils, etc.)
├── dataset/
│   ├── source/                      # Source database init SQL
│   └── warehouse/                   # Warehouse schema init SQL (staging and final schema)
├── Dockerfile                       # Custom Airflow image
├── docker-compose.yml               # Docker Compose config
├── dbt-requirements.txt             # DBT packages for Airflow
├── requirements.txt                 # Python packages for Airflow
├── fernet.py                        # Python script to generate fernet key
└── README.md                        # This guide
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone git@github.com:Rico-febrian/flight-bookings-elt-pipeline-with-dbt-airflow.git
cd flight-bookings-elt-pipeline-with-dbt-airflow
```

### 2. Generate Fernet Key

This key encrypts credentials in Airflow connections.

```bash
pip install cryptography==45.0.2
python3 fernet.py
```

**Copy the output key** to the `.env` file.

### 3. Create `.env` File

Use the following template and update with your actual configuration:

```ini

# --- Airflow Core Configuration ---
AIRFLOW_UID=50000

# Fernet key for encrypting Airflow connections (generated using fernet.py script)
AIRFLOW_FERNET_KEY=YOUR_GENERATED_FERNET_KEY_HERE

# Secret key for Airflow Webserver session management (generate a strong random string)
AIRFLOW_WEBSERVER_SECRET_KEY=YOUR_AIRFLOW_WEBSERVER_SECRET_KEY_HERE

# Celery Executor backend and broker URLs (usually don't need to change unless you modify docker-compose.yml)
AIRFLOW_CELERY_RESULT_BACKEND=db+postgresql://airflow:airflow@airflow-metadata:5433/airflow
AIRFLOW_CELERY_BROKER_URL=redis://:@redis:6379/0

# Airflow metadata database connection URI (eg: postgresql+psycopg2://airflow:airflow@airflow_metadata:5433/airflow)
AIRFLOW_DB_URI=postgresql+psycopg2://<AIRFLOW_DB_USER>:<AIRFLOW_DB_PASSWORD>@<AIRFLOW_METADATA_CONTAINER_NAME>:<AIRFLOW_DB_PORT>/<AIRFLOW_DB_NAME>

# --- Airflow DB User & Password (used by Airflow itself) ---
AIRFLOW_DB_USER=airflow
AIRFLOW_DB_PASSWORD=airflow
AIRFLOW_DB_NAME=airflow

# --- Source Database Configuration (for your Flight Data) ---
FLIGHT_DB_NAME=flight-db-src
FLIGHT_DB_USER=postgres
FLIGHT_DB_PASSWORD=postgres123

# --- Data Warehouse (DWH) Configuration (for staging and final schemas) ---
DWH_DB_NAME=flight-db-dwh
DWH_DB_USER=postgres
DWH_DB_PASSWORD=postgres123

# --- MinIO Configuration (local object storage) ---
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minio123
```

### 4. Build and Start Services

```bash
docker-compose up --build -d
```

### 5. Open Airflow UI

Access the UI at: [http://localhost:8080](http://localhost:8080) (or your defined port).

Log in with the default credentials:

- Username: `airflow`
- Password: `airflow`
(These are defined in the `airflow-init` service within your `docker-compose.yml`).

---

## 🔌 Setup Airflow Connections

You need to create **four** essential connections within the Airflow UI to allow your DAGs to communicate with the **databases**, **MinIO**, and **Slack**. Navigate to **Admin** > **Connections** in the Airflow UI to set these up:

- `flight-db-src` and `flight-db-dwh`
    
    - **Type**: PostgreSQL
    - **Description**: Connection to source and warehouse database

      <img src="https://github.com/Rico-febrian/flight-bookings-elt-pipeline-with-dbt-airflow/blob/main/picts/db-conn.png" alt="db-conn" width="600"/>

- `minio`
    
    - **Type**: Amazon Web Service
    - **Description**: Connection to MinIO (used as object storage/data lake)

      <img src="https://github.com/Rico-febrian/flight-bookings-elt-pipeline-with-dbt-airflow/blob/main/picts/minio-conn.png" alt="minio-conn" width="600"/>

- `slack_notifier`

    - **Type**: HTTP
    - **Description**: Connection to a Slack channel for error alerts
    - **Setup Steps**:

      - **Log in** to your existing Slack account or **create** a new one if you don’t have it yet.
      - **Create a workspace** (if you don’t already have one) and create a dedicated Slack channel where you want to receive alerts.
      - **Create a Slack App**:

         - Go to https://api.slack.com/apps
         - Click **Create New App**
         - Choose **From scratch**
         - Enter your app name and select the workspace you just created or want to use
         - Click **Create App**
    
      4. **Set up an Incoming Webhook** for your app:

         - In the app settings, find and click on **Incoming Webhooks**
         - **Enable Incoming Webhooks** if it’s not already enabled
         - Click **Add New Webhook to Workspace**
         - Select the Slack channel you want alerts to go to and authorize
    
      5. **Copy the generated Webhook URL**

         <img src="https://github.com/Rico-febrian/flight-bookings-elt-pipeline-with-airflow/blob/main/pict/slack-webhook.png" alt="webhook-url" width="600"/>
         
      7. In your Airflow UI, create a new connection called `slack_notifier` with:

         - **Connection Type**: HTTP
         - **Password field**: paste the copied Webhook URL here

           <img src="https://github.com/Rico-febrian/flight-bookings-elt-pipeline-with-airflow/blob/main/pict/slack-connection.png" alt="slack-conn" width="600"/>
          
---

## 🔌 Setup Airflow Variables

You need to create **three** Airflow Variables via the **Admin** > **Variables** section in the Airflow UI. These variables provide dynamic configuration for your DAGs.

- `flight_staging_incremental_mode`

  <img src="https://github.com/Rico-febrian/flight-bookings-elt-pipeline-with-dbt-airflow/blob/main/picts/incremental-vars.png" alt="variables-list" width="700"/>

  - **Key**: `flight_staging_incremental_mode`
  - **Value**: `True` or `False`. Default value is `False`.
  - **Description**:

    - If set to `True`, the pipeline performs an **incremental Extract and Load process**. This means it only processes new or updated data based on created_at or updated_at columns in each table, optimizing performance.

    - If set to `False`, the pipeline will run a **full load**, extracting and loading all data every time, regardless of changes.

- `list_flight_table`

  <img src="https://github.com/Rico-febrian/flight-bookings-elt-pipeline-with-dbt-airflow/blob/main/picts/list-table-vars.png" alt="variables-list" width="700"/>
    
    - **Key**: `list_flight_table`
    - **Value**:

      ```bash
      ['aircrafts_data', 'airports_data', 'bookings', 'tickets', 'seats', 'flights', 'ticket_flights', 'boarding_passes']
      ```
    
    - **Description**: This variable will be used to create dynamic tasks during the data extraction process.

- `pkey_flight_table`

  <img src="https://github.com/Rico-febrian/flight-bookings-elt-pipeline-with-dbt-airflow/blob/main/picts/pkey-vars.png" alt="variables-list" width="700"/>

  - **Key**: `pkey_flight_table`
  - **Value**:

      ``` bash
      {
          "aircrafts_data": "aircraft_code",
          "airports_data": "airport_code",
          "bookings": "book_ref",
          "tickets": "ticket_no",
          "seats": ["aircraft_code", "seat_no"],
          "flights": "flight_id",
          "ticket_flights": ["ticket_no", "flight_id"],
          "boarding_passes": ["ticket_no", "flight_id"]
      }
      ```

    - **Description**:

      This variable will be used to create dynamic tasks during the data loading process to the staging area. The keys of the dictionary represent the table names, and the values represent the primary keys of those tables.

---

## ▶️ Run the DAG

- Open the Airflow UI (http://localhost:8080)

- Locate these two DAGs:

  - `flights_staging_pipeline`
  - `flights_warehouse_pipeline`

- Click the Play ▶️ button on flights_staging_pipeline to trigger the pipeline.

  <img src="https://github.com/Rico-febrian/flight-bookings-elt-pipeline-with-dbt-airflow/blob/main/picts/dags.png" alt="variables-list" width="700"/>

> [!Note]
> You don’t need to manually run flights_warehouse_pipeline. It will be triggered automatically after the staging pipeline completes.

---

## DAG Behavior (What to Expect)

- In `flights_staging_pipeline`:

  - Extract tasks run in parallel
  - Load tasks run sequentially (after extraction)
  - Once loading is done, it **triggers** `flights_warehouse_pipeline`

    <img src="https://github.com/Rico-febrian/flight-bookings-elt-pipeline-with-dbt-airflow/blob/main/picts/stg-full-graph.png" alt="dag-result" width="800"/>

- In `flights_warehouse_pipeline`:

  - DBT runs transformation models to create clean final tables in the warehouse

    <img src="https://github.com/Rico-febrian/flight-bookings-elt-pipeline-with-dbt-airflow/blob/main/picts/dwh-graph.png" alt="dag-result" width="800"/>

---

## ✅ Verify the Results

Since incremental mode and catchup are disabled (set to `False`), the pipeline will runs the **full load** process. So, you can just verify the result by open the database.

### Extracted Data in MinIO Bucket

- Log in to the MinIO console (eg. localhost:9000) using the username and password defined in your `.env` file.
- Navigate to the selected bucket.
- You should see the extracted data files in CSV format.

  <img src="https://github.com/Rico-febrian/flight-bookings-elt-pipeline-with-dbt-airflow/blob/main/picts/minio-result.png" alt="minio-result" width="600"/>

### Staging and Transformed data in Data Warehouse

To verify the data in your data warehouse:

- Open your preferred database client (e.g., DBeaver).
- Connect to your warehouse database.
- Check the following:

  - ✅ Raw data from the source should be available under the **staging** schema.
  - ✅ Transformed data should be available under the **final** schema.
        
---

## 📬 Feedback & Articles

**Thank you for exploring this project!** If you have any feedback, feel free to share, I'm always open to suggestions.

Additionally, I write about my learning journey on Medium. You can check out my articles [here](https://medium.com/@ricofebrian731). Let’s also connect on [LinkedIn](https://www.linkedin.com/in/ricofebrian).

---

Happy learning! 🚀
