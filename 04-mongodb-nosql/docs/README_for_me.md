# MongoDB Sharded Cluster – Case Study: CATCHEM Log Data

This guide covers the implementation of a local NoSQL document store using MongoDB Community Server, simulating a production-like environment with sharding and replication.

## 1. Project Overview
The goal is to create a sharded MongoDB cluster to store log data from an existing Postgres operational database (CATCHEM). The data is processed using PySpark to create a nested JSON structure.

### Cluster Architecture
The cluster consists of:
- **1 Config Server Replica Set** (`configRS`): Manages cluster metadata.
- **3 Shards**, each as a **2-node Replica Set** (`shard1RS`, `shard2RS`, `shard3RS`): Stores the actual data.
- **1 Mongos Router**: Routes queries to the appropriate shards.

---

## 2. Step 1: Installation and Setup
For this simulation, we use Docker to manage multiple MongoDB instances easily.
1. Ensure Docker and Docker Compose are installed.
2. The setup uses MongoDB version 8.0 (as specified in the assignment).
3. `mongosh` is used for all terminal-based configuration.

---

## 3. Step 2: Data Preparation (PySpark)
Data is extracted from Postgres and transformed into a nested JSON format using PySpark.
- **Notebook**: `export_data_in_json_file.ipynb`
- **Output**: A single JSON file containing treasures with their nested stages, logs (hunts), and location details (city, country, coordinates).

please check the `04-mongodb-nosql/treasures_export/first_row.json` file to see the structure of the exported JSON.

---

## 4. Step 3: Configure the Sharded Cluster
### 4.1 Start Containers
```bash
docker-compose up -d
```

### 4.2 Initialize Cluster
Use the provided automation script or run commands manually via `mongosh`.

#### Using Automation Script
The easiest way to initialize the cluster is by using the provided bash script.

```bash
# Navigate to the script location
cd 04-mongodb-nosql/mongo

# Ensure it's executable and run it
chmod +x init-mongo-cluster.sh
./init-mongo-cluster.sh
```

The script will:
- Initialize the Config Server Replica Set.
- Initialize all three Shard Replica Sets.
- Wait for the Router to be ready.
- Add the Shards to the Router.
- Handle cases where the cluster is already initialized.

#### Manual Initialization (Summary)
If you prefer manual steps, run these in `mongosh`:
1. **Config Server**: `rs.initiate()` on port 27019.
2. **Shards**: `rs.initiate()` on each shard replica set (port 27018).
3. **Router**: `sh.addShard()` to register all three replica sets with the `mongos` router (port 27017).

---

## 5. Step 4: Load Data into MongoDB
### 5.1 Copy JSON to Router
```bash
# check the file exists
docker exec mongo-router ls -l /tmp

# delete the file if it exists
docker exec mongo-router rm /tmp/treasures.json

# copy the file to the router
docker cp 04-mongodb-nosql/treasures_export/treasure.json mongo-router:/tmp/treasures.json
```

### 5.2 Import Data
```bash
docker exec -it mongo-router mongoimport --port 27017 --db catchem --collection treasures --file /tmp/treasures.json
```

### 5.3 Enable Sharding
Connect to `mongos`:
```bash
docker exec -it mongo-router mongosh --port 27017
```
Run:
```javascript
use catchem
sh.enableSharding("catchem")

// 1. Create an index on the shard key (REQUIRED before sharding)
db.treasures.createIndex({ "treasure_id": "hashed" })

// 2. Shard the collection
sh.shardCollection("catchem.treasures", { "treasure_id": "hashed" })
```
if you want to drop:
```
db.treasures.drop()

// Recreate the hashed index:
db.treasures.createIndex({ "treasure_id": "hashed" })

// Re-enable sharding for the collection:
sh.shardCollection("catchem.treasures", { "treasure_id": "hashed" })

// Re-run your mongoimport command from the terminal.
docker exec -it mongo-router mongoimport --port 27017 --db catchem --collection treasures --file /tmp/treasures.json
```


---

## 6. Step 5: Query and Explore
### 6.1 Example Queries
Run these in `mongosh` or MongoDB Compass:

**1. Find treasures in a specific city:**
```javascript
db.treasures.find({ "location.city_name": "Antwerp" })
```

**2. Filter treasures by country:**
```javascript
db.treasures.find({ "location.country_name": "Belgium" })

db.treasures.find({ "location.country_name": "Colombia" })
```

**3. Verify Sharding Distribution:**
```javascript
db.treasures.getShardDistribution()
```

---

### 6.2 Analyzing the Distribution
You might notice that the data is not perfectly even across shards (e.g., one shard having 50% and others 25%).

**Why is it "Good"?**
- **Chunk Count**: MongoDB balances by the number of chunks, not the raw data size. In a small dataset, you will have **1 chunk per shard**, which MongoDB considers perfectly balanced.
- **Hashed Sharding**: As more data is imported, these chunks will grow, split, and the balancer will automatically move them to equalize the load.

To verify the balancer:
```javascript
sh.getBalancerState()  // Should return true
sh.isBalancerRunning() // Returns true if it's currently moving data
```

---

## 7. Evaluation & Choices
### Shard Key Choice
- **Key**: `treasure_id` (Hashed)
- **Why**: Since the goal is even distribution and we have 3 shards, a hashed shard key on a unique identifier like `treasure_id` ensures that data is spread uniformly across the cluster, preventing "hot shards" during high-volume inserts.

### Nested Structure
- **Choice**: Storing stages and logs as nested arrays within the treasure document.
- **Why**: MongoDB excels at document-based models. Nesting related data (1-to-N) reduces the need for expensive joins and allows for atomic updates to a single treasure entity.

