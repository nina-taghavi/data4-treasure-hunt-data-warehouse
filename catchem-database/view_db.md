# 📘 Viewing the Database Inside the PostgreSQL Docker Container

This guide explains how to start the PostgreSQL container, connect to the database using `psql`, and inspect tables and data.

---

## ▶️ 1. Start the PostgreSQL Container

```bash
docker start postgres
```

This ensures the container named `postgres` is running.

---

## 🐚 2. Enter the Container Shell

```bash
docker exec -it postgres /bin/sh
```

This opens an interactive shell inside the container.

---

## 🗄️ 3. Connect to the Database Using psql

```bash
psql -U postgres -d catchem
```

- `-U postgres` → login as the Postgres user  
- `-d catchem` → connect to the `catchem` database

---

## 📋 4. List All Tables

Inside `psql`, run:

```sql
\dt
```

This displays all tables in the current database.

---

## 🧱 5. Show Table Structure

```sql
\d table_name
```

Replace `table_name` with the actual table you want to inspect.

---

## 🔍 6. View Sample Data

```sql
SELECT * FROM treasure_log LIMIT 10;
```

This shows the first 10 rows from the `treasure_log` table.

