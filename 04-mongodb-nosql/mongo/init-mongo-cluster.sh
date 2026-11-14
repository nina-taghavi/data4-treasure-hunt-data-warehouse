#!/usr/bin/env bash

# -----------------------------
# Color definitions
# -----------------------------
GREEN="\033[32m"
RED="\033[31m"
YELLOW="\033[33m"
BLUE="\033[34m"
CYAN="\033[36m"
RESET="\033[0m"

ok()    { echo -e "${GREEN}[OK]${RESET} $1"; }
info()  { echo -e "${CYAN}[INFO]${RESET} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${RESET} $1"; }
error() { echo -e "${RED}[ERROR]${RESET} $1"; }

# -----------------------------
# Helper: run command with color
# -----------------------------
run() {
  echo -e "${BLUE}>>> Running:${RESET} $1"
  if eval "$1"; then
    ok "Command succeeded"
  else
    error "Command failed"
    return 1
  fi
}

# -----------------------------
# Helper: check if RS already initialized
# -----------------------------
check_rs() {
  local container=$1
  local port=$2

  docker exec "$container" mongosh --quiet --port "$port" --eval "rs.status().ok" 2>/dev/null
}

echo -e "${CYAN}"
echo "--------------------------------------------------"
echo " Initializing MongoDB Sharded Cluster"
echo "--------------------------------------------------"
echo -e "${RESET}"

# ============================================================
# 1. CONFIG SERVER
# t executes a command inside the mongo-config container to run rs.initiate().
# This tells that specific MongoDB instance: "You are now the Config Server Replica Set (configRS).
# Start keeping track of the cluster's metadata."
# ============================================================
info "STEP 1: Config Server Replica Set"

if check_rs "mongo-config" 27019 | grep -q "1"; then
  warn "ConfigRS already initialized — skipping"
else
  info "Initializing configRS..."
  run "docker exec mongo-config mongosh --port 27019 --eval '
  rs.initiate({
    _id: \"configRS\",
    configsvr: true,
    members: [
      { _id: 0, host: \"mongo-config:27019\" }
    ]
  })'"
fi

# ============================================================
# 2. SHARD REPLICA SETS
# It loops through this list. For each shard, it connects to the first node (e.g., mongo-shard1-a)
# and runs rs.initiate().
# This tells those two nodes: "You are now a team called shard1RS.
# Node A, talk to Node B and start replicating data between yourselves."
# ============================================================
info "STEP 2: Shard Replica Sets"

# Replaced associative array with a standard array for macOS compatibility
shards=(
  "shard1RS|mongo-shard1-a:27018,mongo-shard1-b:27018"
  "shard2RS|mongo-shard2-a:27018,mongo-shard2-b:27018"
  "shard3RS|mongo-shard3-a:27018,mongo-shard3-b:27018"
)

for shard_info in "${shards[@]}"; do
  # Split the string by the pipe character '|'
  rs="${shard_info%%|*}"
  hosts="${shard_info##*|}"
  primary=$(echo "$hosts" | cut -d',' -f1 | cut -d':' -f1)

  info "Checking $rs..."

  if check_rs "$primary" 27018 | grep -q "1"; then
    warn "$rs already initialized — skipping"
  else
    info "Initializing $rs..."
    members=""
    id=0
    for host in $(echo "$hosts" | tr ',' ' '); do
      members="$members{ _id: $id, host: \"$host\" },"
      id=$((id+1))
    done

    run "docker exec $primary mongosh --port 27018 --eval '
    rs.initiate({
      _id: \"$rs\",
      members: [ ${members%,} ]
    })'"
  fi
done

# ============================================================
# 3. ADD SHARDS TO ROUTER
# It tells the router: "Hey router, here are the three distinct storage buckets (shard1RS, shard2RS, shard3RS)
# you are allowed to use. Connect to them and start distributing data across them."
# ============================================================
info "STEP 3: Adding Shards to Mongos Router"

info "Waiting for mongo-router to be ready..."
until docker exec mongo-router mongosh --port 27017 --quiet --eval "db.adminCommand({ ping: 1 }).ok" &>/dev/null; do
  echo -n "."
  sleep 2
done
echo ""
ok "mongo-router is ready"

for shard_info in "${shards[@]}"; do
  rs="${shard_info%%|*}"
  hosts="${shard_info##*|}"
  shard_string="$rs/$hosts"

  info "Adding $shard_string"

  run "docker exec mongo-router mongosh --host mongo-router --port 27017 --eval '
  try {
    sh.addShard(\"$shard_string\")
  } catch(e) {
    if (e.codeName === \"ShardAlreadyExists\") {
      print(\"Shard already added — skipping\")
    } else {
      throw e
    }
  }'"
done

# ============================================================
# DONE
# ============================================================
echo -e "${GREEN}"
echo "--------------------------------------------------"
echo " MongoDB Sharded Cluster Initialization Complete"
echo "--------------------------------------------------"
echo -e "${RESET}"

info "Verify with:"
echo "  docker exec -it mongo-router mongosh --port 27017 --eval 'sh.status()'"
echo ""