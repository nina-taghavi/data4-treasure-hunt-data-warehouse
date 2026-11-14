

# 📘 Restoring a PostgreSQL Database Inside a Docker Container

This guide explains how to import a large `.sql` dump file into a PostgreSQL database running inside a Docker container.  
It uses two reliable steps:

1. **Copy the SQL file into the container**  
2. **Execute the SQL file using `psql` inside the container**

This method avoids slow PowerShell streaming and works well for large backups.

---

## 📥 1. Copy the SQL File Into the Container

Use `docker cp` to transfer the file from your host machine into the container:

```bash
docker cp catchem-database/catchem_backup.sql postgres-data4:/catchem_backup.sql
```

After this step, the file will be available inside the container at:

```
/catchem_backup.sql
```

---

## 🛠️ 2. Run the SQL File Inside the Container
Create a new database named `catchem` if it doesn't exist:
```bash
docker exec -it postgres-data4 psql -U postgres -c "CREATE DATABASE catchem;"
````
Execute the SQL file using `psql`:

```bash
docker exec -it postgres-data4 psql -U postgres -d catchem -f /catchem_backup.sql
```

This command:

- Connects to the `catchem` database  
- Runs every statement in the SQL file  
- Creates tables, inserts data, and restores the schema

---

## 🔍 Optional Checks

### Verify the file exists inside the container
```bash
docker exec -it postgres-data4 ls -lh /
```

### List tables after import
```bash
docker exec -it postgres-data4 psql -U postgres -d catchem -c "\dt"
```

---

## 🧹 Cleanup (Optional)

If you want to remove the SQL file from the container after restoring:

```bash
docker exec -it postgres-data4 rm /catchem_backup.sql
```

---
