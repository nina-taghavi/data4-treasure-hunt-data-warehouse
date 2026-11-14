# Oral Exam Preparation - DWH Concepts

## DWH (Data Warehouse)

### 1. Demonstrate that your Type 2 dimension works correctly by changing some source data.
**Answer:**
In our project, we implemented SCD Type 2 for `dim_user` using Delta Tables. If a user's source data changes (e.g., they change their city or experience level):
1. **Detect Changes**: Our incremental ETL job joins the new transformed data from the source with the current active records (`current = true`) in the DWH on `user_id`. It filters for records where any monitored attribute (like `city_name`, `country_name`, `experience_level`, or `dedicator`) has changed.
2. **Prepare Upserts**:
   - For the changed records, we create an **Update** record. We take the *existing* active DWH record, set `scd_end` to the current timestamp, and `current` to `false`.
   - We create an **Insert** record containing the *new* source values, setting `scd_start` to the current timestamp, `scd_end` to `null`, and `current` to `true`.
3. **Merge**: We use the `DeltaTable.merge()` operation to apply these changes. It updates the matched old records and inserts the new active records, effectively maintaining the history of the dimension.

To demonstrate, we can update a row in the operational database (e.g., set `city_name` to a new value for a user) and then run the `09_DIM_USER_INCREMENTAL_DF.ipynb` notebook. The `dim_user` table will then contain two rows for that `user_id`: one historical (`current=false`, with an `scd_end` date) and one current (`current=true`, with `scd_end=null`).

### 2. Suppose you want to extend a Type 2 dimension with field X. How would you approach this?
**Answer:**
To add a new field 'X' to an existing SCD Type 2 dimension (like `dim_user`):
1. **Update Delta Table Schema**: Add the new column to the Delta Table schema. If using `ALTER TABLE`, it would be `ALTER TABLE dim_user ADD COLUMNS (X dataType)`. For Delta Lake, we can also use schema evolution (`mergeSchema=True`) during the next write if we rewrite the historical data.
2. **Update Initial/Historical Load**: We need to decide how to backfill historical data. If the historical data for 'X' is available, we would write a script to update the existing records. If not, the old records would have `null` or a default value for 'X'.
3. **Update Incremental ETL Logic**:
    *   **Transform**: Update the source transformation logic to pull and transform field 'X'.
    *   **Detect Changes**: Add field 'X' to the condition checking for changes: `(F.col("dwh.X") != F.col("source.X"))`. This ensures that a change in 'X' triggers an SCD Type 2 update (closing the old record and inserting a new one).
    *   **Upserts & Merge**: Include field 'X' in both the `whenMatchedUpdate` and `whenNotMatchedInsert` clauses in the `DeltaTable.merge()` statement so the new values are correctly written.

### 3. We add an extra “analysis question.” Go through the steps to determine whether it can be answered and describe the required changes to the star schema and ETL jobs.
**Answer:**
**Scenario Analysis Question**: *What is the total duration of treasure hunts completed by users in specific cities, broken down by season?*

**Steps to evaluate and implement:**
1. **Determine if it can be answered**:
    *   **Required Data**: Total duration (`fact_treasure_hunt.duration_minutes`), user city (`dim_user.city_name`), and season (`dim_season.season_name`).
    *   **Current Schema Check**: Our star schema currently has `dim_user` (which contains `city_name`), `dim_season`, and `fact_treasure_hunt` (which contains `duration_minutes`). So, yes, it can be answered without structural changes!
2. **Required Changes (If Data was missing - e.g., if we needed 'Weather Condition' but didn't have it)**:
    *   **Star Schema**: We would need to add a `weather_sk` foreign key to `fact_treasure_hunt` and create a new `dim_weather` table.
    *   **ETL Jobs**:
        *   Create an ETL job to populate `dim_weather` from the source data.
        *   Update the ETL job for `fact_treasure_hunt` to perform a lookup against `dim_weather` (based on the hunt date/time and location) to retrieve the correct `weather_sk` and insert it into the fact table.

### 4. We ask for a small functional change to the data warehouse and ask how you would solve it.
**Answer:**
**Functional Change Request**: *Instead of just keeping the active and historical records, we want to know the "Reason for Change" for SCD Type 2 updates in `dim_user`.*

**Solution:**
1. **Schema Update**: Add a new column `change_reason` (String) to `dim_user`.
2. **ETL Logic Update (Incremental)**:
    *   In the "Detect Changes" phase, we evaluate *which* column changed.
    *   We can use PySpark's `when().otherwise()` logic when constructing the "Insert" DataFrame to populate `change_reason`. For example:
        ```python
        F.when(F.col("dwh.city_name") != F.col("source.city_name"), "City Moved")
        .when(F.col("dwh.experience_level") != F.col("source.experience_level"), "Experience Changed")
        # ... etc.
        .alias("change_reason")
        ```
    *   Update the `DeltaTable.merge()` operation to include `change_reason` in the `whenNotMatchedInsert` clause. The initial load or historical records would have this field as "Initial Load" or `null`.
