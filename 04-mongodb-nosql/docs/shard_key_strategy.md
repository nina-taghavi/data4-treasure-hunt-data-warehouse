# MongoDB Shard Key Strategy for CATCHEM Treasures

Based on the denormalized JSON structure where `location` and `stages` are embedded directly into the Treasure document, here is an analysis of the best shard key criteria and options.

## Example Document Structure
```json
{
    "id": "AAA+LLFAQbGX8AAzwJfgcA==",
    "hex_id": "00003E2CB14041B197F00033C097E070",
    "difficulty": 3,
    "terrain": 1,
    "location": {
        "city_name": "Gurah",
        "country_name": "Pakistan",
        "postal_code": "48411",
        "coordinates": {
            "latitude": 32.6417,
            "longitude": 73.4833
        }
    },
    "stages": [ ... ]
}
```

## Critical Constraints
**You Cannot Shard on Arrays:** In MongoDB, a shard key cannot be an array or a field inside an array. This means you immediately cannot use `stages` or anything inside `stages` (like `stages.id` or `stages.sequence_number`) as your shard key.

## Evaluation Criteria Applied to This Structure

### 1. Read Routing (Query Patterns)
This is the most important factor for a geocaching app. 
*   **Geographic Searches:** ("Show me all treasures in Pakistan" or "in Gurah"). If you don't include location in your shard key, every map search will query *every single shard* (Scatter-Gather), which is very slow.
*   **ID Searches:** Searching by `id` or `hex_id` is fast.
*   *Note:* You cannot use a Geospatial index (`location.coordinates`) as a shard key in MongoDB.

### 2. Cardinality (Uniqueness)
The key must have enough unique values to split the data.
*   `difficulty` (1-5) or `terrain` (1-5) have terrible cardinality.
*   `location.country_name` or `location.city_name` alone have bad cardinality. If you used `city_name`, all treasures in "Gurah" would be stuck on one shard forever.
*   `id` or `hex_id` have massive cardinality (perfect uniqueness).

### 3. Write Distribution (Avoiding Hotspots)
*   If your `id` is randomly generated, writes will naturally distribute across all shards.
*   If users are creating lots of treasures in one city at the same time, sharding purely by `location.city_name` creates a bottleneck.

## Recommended Shard Key Options

### Option A: The "Geographic" Compound Key (Best for Map-Based Apps)
**Key:** `{ "location.country_name": 1, "location.city_name": 1, "id": 1 }`

*   **Why choose this:** In a treasure-hunting app, most queries are geographic ("Find treasures in my city"). By putting country and city first, all treasures for a specific city are kept together on the same shard. The router immediately knows which shard holds the data for a given location.
*   **Why the `id` is at the end:** Because `country + city` doesn't have enough uniqueness (cardinality). Adding `id` at the end guarantees that if a city gets millions of treasures, MongoDB can still split the chunk into smaller pieces using the unique `id`.

### Option B: The "Even Distribution" Hashed Key (Best for pure Write Speed / ID Lookups)
**Key:** `{ "id": "hashed" }` (or `{ "hex_id": "hashed" }`)

*   **Why choose this:** If your main goal is to balance the storage space and write operations perfectly equally across all servers. It takes the `id`, hashes it, and assigns it to a random shard. 
*   **The Downside:** If a user searches for `{"location.city_name": "Gurah"}`, the MongoDB router doesn't know which shard holds Gurah. It must broadcast that query to *all* shards. 

### Final Recommendation
For a geocaching application where this JSON structure represents the main entity, **Option A (`{ "location.country_name": 1, "location.city_name": 1, "id": 1 }`) is usually the best choice.** It perfectly supports hierarchical location queries while maintaining high cardinality to prevent un-splittable chunks.
