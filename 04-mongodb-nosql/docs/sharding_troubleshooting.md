# MongoDB Sharding Troubleshooting: All Data on One Shard

When testing MongoDB sharding locally, you might run the `db.collection.getShardDistribution()` command and see that 100% of your data is sitting on a single shard, looking something like this:

```text
[direct: mongos] catchem> db.treasures.getShardDistribution()
Shard shard1RS at shard1RS/mongo-shard1-a:27018,mongo-shard1-b:27018
{
  data: '128.59MiB',
  docs: 128294,
  chunks: 1,
  'estimated data per chunk': '128.59MiB',
  'estimated docs per chunk': 128294
}
---
Totals
{
  data: '128.59MiB',
  docs: 128294,
  chunks: 1,
  'Shard shard1RS': [
    '100 % data',
    '100 % docs in cluster',
    '1KiB avg obj size on shard'
  ]
}
```

## Why is this happening?

MongoDB distributes data by breaking it into pieces called **chunks**. The balancer then moves these chunks around to ensure every shard has an equal number of chunks.

However, **the default chunk size in MongoDB is 128 Megabytes**. 
If you look at the output above, the total data size is roughly **`128.59MiB`** and it explicitly says **`chunks: 1`**. 

Because your total dataset is roughly the size of a single default chunk, MongoDB currently sees no reason to split it or move it. The balancer only kicks in when there are multiple chunks and a significant imbalance between the number of chunks on each shard.

## How to Fix This (For Local Testing / Small Datasets)

To see the sharding mechanism work with a relatively small dataset (~128MB), you need to artificially lower the chunk size. If we lower the chunk size to `1 Megabyte`, MongoDB will split your data into roughly 128 chunks and immediately start distributing them across your available shards.

Run the following commands in your `mongosh` terminal (connected to the router):

### 1. Lower the chunk size to 1 MB
You must switch to the `config` database to update this setting.

```javascript
use config
db.settings.updateOne(
   { _id: "chunksize" },
   { $set: { _id: "chunksize", value: 1 } },
   { upsert: true }
)
```

### 2. Ensure the balancer is turned on
```javascript
sh.setBalancerState(true)
```

### 3. Wait for the balancer to do its job
Because MongoDB has to split that giant chunk and physically move the data over the network between the Docker containers, **it will take a few minutes**. 

You can watch the progress by switching back to your application database and periodically checking the distribution:

```javascript
use catchem
db.treasures.getShardDistribution()
```

## What to Expect

Within a couple of minutes, you should see the `chunks` count shoot up from 1 to over 100. Then, you will see your other shards (e.g., `shard2RS` and `shard3RS`) start to appear in the output as chunks are migrated to them. Eventually, the balancer will equalize the load to roughly 33% of the data on each of your 3 shards.