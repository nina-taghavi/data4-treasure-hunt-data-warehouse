from configparser import ConfigParser
from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession
import os
import subprocess

# ENVIRONMENT DIRECTORIES
#### Not needed when running with the JUPYTER DOCKER CONTAINER################################
# Change to the root path of you installation directories. (ex. c:\\tools\bigdatatools\spark-3.5.2-bin-hadoop3)
spark_home = f"C:{os.sep}DevApps{os.sep}bigdatatools{os.sep}spark-3.5.2-bin-hadoop3"  # Change to own hadoop-folder. Use double slashes when needed. You can also use os.sep instead of the double slaches.
hadoop_home = f"C:{os.sep}DevApps{os.sep}bigdatatools{os.sep}hadoop-3.4.0-win10-x64"  # For windows: use the hadoop folder in bigdatatools. For linux/mac: Try with provided hadoop folder in bigdatatools, if that doesn't work, download hadoop from the apache website: https://hadoop.apache.org/release/3.4.0.html
# java_home = "C:"+ os.sep + "Program Files" + os.sep +"Java" +os.sep + "jdk-11"
java_home = "/usr/lib/jvm/java-17-openjdk-amd64"
#### Not needed when running with the JUPYTER DOCKER CONTAINER################################

# DO NOT CHANGE ANYTHING BELOW THIS LINE
# Configparser is a helper class to read properties from a configuration file
config = ConfigParser()
config.read('config.ini')  # Define connection properties is the config file
cn = "default"  # This is the default connection-name. Create a "default" profile in config.ini


# This function can be used to set systemvariables before running code. This eliminates the need to set the variables in the os.
def setupEnvironment():
    # If running in Docker (usually 'jovyan' user or SPARK_HOME is /usr/local/spark)
    # we don't need to manually set these variables as they are in the image.
    if os.environ.get("SPARK_HOME") == "/usr/local/spark":
        print("Running in Docker environment.")
        # Detect actual JAVA_HOME in the container
        potential_java_homes = [
            "/usr/lib/jvm/java-17-openjdk-arm64",
            "/usr/lib/jvm/java-21-openjdk-arm64",
            "/usr/lib/jvm/java-17-openjdk-amd64",
            "/usr/lib/jvm/java-17-openjdk",
            "/usr/lib/jvm/openjdk-17"
        ]
        for path in potential_java_homes:
            if os.path.exists(path):
                print(f"Setting JAVA_HOME to {path}")
                os.environ["JAVA_HOME"] = path
                break

        # Ensure python paths are consistent
        if "PYSPARK_PYTHON" not in os.environ:
            os.environ["PYSPARK_PYTHON"] = "python3"
        if "PYSPARK_DRIVER_PYTHON" not in os.environ:
            os.environ["PYSPARK_DRIVER_PYTHON"] = "python3"

        return

    # os.environ["PYSPARK_PYTHON"] = "python"
    # #### Not needed when running with the JUPYTER DOCKER CONTAINER################################
    # os.environ["SPARK_HOME"] = spark_home
    # os.environ["HADOOP_HOME"] = hadoop_home
    # os.environ["PYSPARK_HADOOP_VERSION"] ="3"
    # os.environ["JAVA_HOME"] = java_home + os.sep
    # pathlist = [spark_home + os.sep + "bin", hadoop_home + os.sep +  "bin", java_home + os.sep + "bin"]
    ##### Not needed when running with the JUPYTER DOCKER CONTAINER################################
    pathlist = [java_home + os.sep + "bin"]
    os.environ["PATH"] += os.pathsep + os.pathsep.join(pathlist)
    print("Environment variables are set...")


# This function can be used to list all environment variables.
def listEnvironment():
    import os
    for key, value in os.environ.items():
        print(f'{key}: {value}')


def startLocalCluster(appName, partitions=4):
    # Detect Java Home dynamically if not set or invalid
    if "JAVA_HOME" not in os.environ or not os.path.exists(os.environ["JAVA_HOME"]):
        try:
            # Try macOS way
            java_home_cmd = subprocess.check_output(["/usr/libexec/java_home"], text=True).strip()
            os.environ["JAVA_HOME"] = java_home_cmd
        except:
            # Fallback for Linux/Docker
            potential_java_homes = [
                "/usr/lib/jvm/java-17-openjdk-arm64",
                "/usr/lib/jvm/java-21-openjdk-arm64",
                "/usr/lib/jvm/java-17-openjdk-amd64",
                "/usr/lib/jvm/java-17-openjdk",
                "/usr/lib/jvm/openjdk-17",
                "/usr/lib/jvm/default-java"
            ]
            for path in potential_java_homes:
                if os.path.exists(path):
                    os.environ["JAVA_HOME"] = path
                    break

    # If JAVA_HOME is still not found, try 'which java'
    if "JAVA_HOME" not in os.environ or not os.path.exists(os.environ["JAVA_HOME"]):
        try:
            java_path = subprocess.check_output(["which", "java"], text=True).strip()
            # Resolve symlinks and go up twice to get the HOME (bin/java -> HOME)
            resolved_path = os.path.realpath(java_path)
            os.environ["JAVA_HOME"] = os.path.dirname(os.path.dirname(resolved_path))
        except:
            pass

    # Additional Java options to fix Java 17+ issues and module access
    extra_java_options = (
        "-Djava.security.manager=allow "
        "--add-opens=java.base/java.lang=ALL-UNNAMED "
        "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED "
        "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED "
        "--add-opens=java.base/java.io=ALL-UNNAMED "
        "--add-opens=java.base/java.net=ALL-UNNAMED "
        "--add-opens=java.base/java.nio=ALL-UNNAMED "
        "--add-opens=java.base/java.util=ALL-UNNAMED "
        "--add-opens=java.base/java.util.concurrent=ALL-UNNAMED "
        "--add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED "
        "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED "
        "--add-opens=java.base/sun.nio.cs=ALL-UNNAMED "
        "--add-opens=java.base/sun.security.action=ALL-UNNAMED "
        "--add-opens=java.util/java.util=ALL-UNNAMED "
        "--add-opens=java.base/sun.util.calendar=ALL-UNNAMED "
        "-Djdk.reflect.useDirectMethodHandle=false"
    )

    # If running inside Docker
    if os.environ.get("SPARK_HOME") == "/usr/local/spark":
        print("Running in Docker: using pre-installed Spark + JARs")
        return (
            SparkSession.builder
            .appName(appName)
            .master("local[*]")
            .config("spark.driver.memory", "6g")
            .config("spark.driver.host", "127.0.0.1")
            .config("spark.driver.bindAddress", "127.0.0.1")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .config("spark.sql.shuffle.partitions", partitions)
            .config("spark.driver.extraJavaOptions", extra_java_options)
            .getOrCreate()
        )

    # If running locally (Windows/Mac)
    extra_packages = [
        "org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0",
        "org.postgresql:postgresql:42.7.7"
    ]

    builder = (
        SparkSession.builder
        .appName(appName)
        .master("local[*]")
        .config("spark.driver.memory", "6g")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.shuffle.partitions", partitions)
        .config("spark.driver.extraJavaOptions", extra_java_options)
    )

    builder = configure_spark_with_delta_pip(builder, extra_packages=extra_packages)
    return builder.getOrCreate()


def create_jdbc():
    return get_Property("url")


# Set the connectionName that has to be used (if you don't want to use the default profile
def set_connectionProfile(connectionName):
    global cn
    cn = connectionName


# Returns a specific property from the connection profile in the config.ini
def get_Property(propertyName):
    return config.get(cn, propertyName)


def delete_delta_table(spark, tableName):
    # Define the table
    dwh_location = "./spark-warehouse/" + tableName

    # 1. Drop from Spark Catalog
    spark.sql(f"DROP TABLE IF EXISTS {tableName}")

    # 2. Use a standard Python utility to wipe the folder
    import shutil
    import os

    if os.path.exists(dwh_location):
        shutil.rmtree(dwh_location)
        print(f"Successfully deleted metadata and files for {tableName}")
    else:
        print(f"Table {tableName} was already deleted or does not exist.")

    # Instead of sys.exit(), just let the cell finish or use:
    # raise Exception("Manual Stop: Table Deleted") # If you want to force-stop the run


def delete_parquet_table(parquet_path):
    import shutil
    import os

    if os.path.exists(parquet_path):
        shutil.rmtree(parquet_path)
        print(f"Deleted old parquet at {parquet_path}")
    else:
        print(f"No old parquet at {parquet_path}, skipping deletion")


def read_postgres_without_partition(spark, table_name):
    full_table_path = f"{get_Property('schema')}.{table_name}"

    return spark.read \
        .format("jdbc") \
        .option("driver", get_Property("driver")) \
        .option("url", get_Property("url")) \
        .option("user", get_Property("username")) \
        .option("password", get_Property("password")) \
        .option("dbtable", full_table_path) \
        .load()


from datetime import datetime


def get_date_bounds(spark, table_name, date_col):
    schema = get_Property("schema")

    # We cast to EXTRACT(EPOCH...) to get a numeric value directly from Postgres
    # This avoids type conversion issues between JDBC and Python
    query = f"""
    (SELECT 
        EXTRACT(EPOCH FROM MIN({date_col}))::bigint as min_ts, 
        EXTRACT(EPOCH FROM MAX({date_col}))::bigint as max_ts 
     FROM {schema}.{table_name}) as bounds
    """

    df_bounds = spark.read \
        .format("jdbc") \
        .option("url", get_Property("url")) \
        .option("dbtable", query) \
        .option("user", get_Property("username")) \
        .option("password", get_Property("password")) \
        .load()

    row = df_bounds.collect()[0]

    # Provide defaults if table is empty
    min_val = row['min_ts'] if row['min_ts'] is not None else 0
    max_val = row['max_ts'] if row['max_ts'] is not None else 0

    return min_val, max_val


def read_postgres_by_date(spark, table_name, date_col, num_partitions=4):
    min_val, max_val = get_date_bounds(spark, table_name, date_col)
    schema = get_Property("schema")

    # CRITICAL: We wrap the table in a subquery that casts the timestamp to a BIGINT
    # so Spark's partitionColumn (which expects numeric) can map to it correctly.
    partition_query = f"""
    (SELECT *, EXTRACT(EPOCH FROM {date_col})::bigint as {date_col}_int 
     FROM {schema}.{table_name}) as sub
    """
    # EXTRACT(EPOCH FROM ...): Instead of returning a standard human-readable timestamp (like 2026-06-10 14:00:00),
    # this function converts the time into a Unix Epoch. This is the total number of seconds that have passed since
    # January 1, 1970.

    return spark.read \
        .format("jdbc") \
        .option("url", get_Property("url")) \
        .option("user", get_Property("username")) \
        .option("password", get_Property("password")) \
        .option("dbtable", partition_query) \
        .option("partitionColumn", f"{date_col}_int") \
        .option("lowerBound", str(min_val)) \
        .option("upperBound", str(max_val)) \
        .option("numPartitions", str(num_partitions)) \
        .load() \
        .drop(f"{date_col}_int")  # Clean up the helper column


def check_postgres_connection():
    import socket
    try:
        # Try to open a TCP connection to the Postgres container
        sock = socket.create_connection(("postgres-data4", 5432), timeout=5)
        print("✅ SUCCESS: Jupyter can see the Postgres container on the network!")
        sock.close()
    except Exception as e:
        print(f"❌ FAILED: Cannot reach the database. Error: {e}")


def spark_db_connection_healthcheck(spark):
    try:
        # Attempt to read just 1 row from the country table
        test_df = spark.read \
            .format("jdbc") \
            .option("driver", get_Property("driver")) \
            .option("url", get_Property("url")) \
            .option("user", get_Property("username")) \
            .option("password", get_Property("password")) \
            .option("dbtable", f'{get_Property("schema")}."country"') \
            .load()

        # Trigger an action to force the connection
        count = test_df.limit(1).count()
        print(f"✅ Connection Successful! Found {count} row(s) in the country table.")

    except Exception as e:
        print("❌ Connection Failed!")
        print(f"Error details: {e}")
