# 📘 Setting Up PostgreSQL in Google Cloud (Cloud SQL)

This guide walks you through creating, configuring, and connecting to a PostgreSQL database on Google Cloud Platform (GCP) using **Cloud SQL**, as well as importing data.

---

## 🚀 Method 1: Create via Google Cloud Console (Web UI)

### 1. Navigate to Cloud SQL
1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Select your Google Cloud Project.
3. In the navigation menu (left sidebar), go to **Storage** > **Cloud SQL** (or search for **SQL** in the top search bar).

### 2. Create Instance
1. Click **Create Instance**.
2. Choose **PostgreSQL** as the database engine.
3. Configure instance details:
   - **Instance ID**: e.g., `catchem-postgres`
   - **Password**: Set a strong password for the `postgres` default user (and save it). --> `YOUR_POSTGRES_PASSWORD`
   - **Database Version**: Select `PostgreSQL 15` or `PostgreSQL 16`.
   - **Cloud SQL Edition**: Choose **Enterprise** (or Enterprise Plus depending on needs).
   - **Preset**: Select **Development** (1 vCPU, 3.75 GB RAM) for cost-efficiency.
   - **Region and Zonal Availability**: Select your closest region (e.g., `europe-west1` or `us-central1`) and **Single zone** (to minimize costs).

### 3. Configure Connectivity & Authorized Networks
1. Expand **Connections** / **Customize your instance**:
   - Under **Connectivity**, check **Public IP**.
   - Under **Authorized networks**, click **Add network**:
     - **Name**: e.g., `My Local IP` or `Allow All (Dev only)`
     - **Network**: Enter your public IP address (e.g., `YOUR_PUBLIC_IP/32`) or `0.0.0.0/0` (for testing/development only).
2. Click **Create Instance** and wait a few minutes for provisioning to finish.

---

## ⚡ Method 2: Create via Google Cloud CLI (`gcloud`)

If you have the `gcloud` CLI installed or are using Google Cloud Shell:

### 1. Create the Cloud SQL Instance
```bash
gcloud sql instances create catchem-data4-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --storage-type=HDD \
    --region=europe-west1 \
    --storage-size=10GB \
    --root-password="YOUR_POSTGRES_PASSWORD"
```

### 2. Authorize Your IP Address
```bash
gcloud sql instances patch catchem-data4-postgres \
    --authorized-networks=YOUR_IP_ADDRESS/32
```
*(To allow all connections during dev: `--authorized-networks=0.0.0.0/0`)*
```bash
gcloud sql instances patch catchem-data4-postgres \
   --authorized-networks=0.0.0.0/0
```
---

## 🗄️ 3. Create Database and User

### Via Web Console:
1. Open your Cloud SQL instance details page.
2. Go to the **Databases** tab on the left menu -> Click **Create Database** -> Name: `catchem` -> Click **Create**.
3. Go to the **Users** tab -> (Optional) Create a new application user or use the default `postgres` user.

### Via `gcloud` CLI:
```bash
# Create database
gcloud sql databases create catchem --instance=catchem-data4-postgres

# Create user (optional)
gcloud sql users create appuser --instance=catchem-data4-postgres --password="YOUR_APP_USER_PASSWORD"
```

---

## 🔌 4. Connect to the Cloud SQL PostgreSQL Database

### Option A: Connect directly using `psql`
Get the **Public IP address** from the instance overview page:

```bash
psql "host=INSTANCE_PUBLIC_IP port=5432 dbname=catchem user=postgres sslmode=require"
```
Enter your password when prompted.

---

### Option B: Connect via Google Cloud Shell
1. Open Cloud Shell in your GCP Console.
2. Run:
```bash
gcloud sql connect catchem-data4-postgres --user=postgres --database=catchem
```

---

### Option C: Connect via Cloud SQL Auth Proxy (Most Secure)
1. Download and start the Cloud SQL Auth Proxy:
```bash
./cloud-sql-proxy PROJECT_ID:REGION:INSTANCE_NAME
```
2. Connect locally:
```bash
psql -h 127.0.0.1 -U postgres -d catchem
```

---

## 📥 5. Import / Restore SQL Dump

### Method 1: Via Google Cloud Storage Bucket (Recommended & Fastest for Large Dumps)
This is the native GCP method. It does not require `psql` locally and handles huge dumps without timeout or local network disconnects.

1. **Create a Cloud Storage Bucket**:
   ```bash
   gcloud storage buckets create gs://catchem-data-backup-bucket --location=europe-west1
   ```

2. **Upload your SQL dump to the bucket**:
   ```bash
   gcloud storage cp catchem-database/catchem_backup.sql gs://catchem-data-backup-bucket/catchem_backup.sql
   ```

3. **Grant Cloud SQL Service Account permission on the bucket**:
   Find your Cloud SQL instance service account:
   ```bash
   SERVICE_ACCOUNT=$(gcloud sql instances describe catchem-data4-postgres --format="value(serviceAccountEmailAddress)")
   ```
   Grant `roles/storage.objectViewer` to the service account:
   ```bash
   gcloud storage buckets add-iam-policy-binding gs://catchem-data-backup-bucket \
       --member="serviceAccount:${SERVICE_ACCOUNT}" \
       --role="roles/storage.objectViewer"
   ```

4. **Import the SQL file into PostgreSQL**:
   ```bash
   gcloud sql import sql catchem-data4-postgres gs://catchem-data-backup-bucket/catchem_backup.sql --database=catchem --user=postgres
   ```
   *(Or in GCP Console: Go to **Cloud SQL** -> click your instance -> click **Import** -> select Cloud Storage file and choose database `catchem`)*

---

### Method 2: Via Local `psql` / Docker
If you have local `psql` or run via Docker:

```bash
docker run -i --rm postgres:15 psql "host=INSTANCE_PUBLIC_IP port=5432 dbname=catchem user=postgres sslmode=require" < catchem-database/catchem_backup.sql
```

---

## 🔍 6. Verify the Connection & Tables

Inside `psql`:

```sql
-- List databases
\l

-- Connect to database
\c catchem

-- List all tables
\dt

-- Check sample data
SELECT * FROM treasure_log LIMIT 10;
```
