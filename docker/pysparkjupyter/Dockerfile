FROM quay.io/jupyter/pyspark-notebook

ARG spark_version=4.0.0
ARG hadoop_version=3
ARG delta_version=4.0.0
ARG postgres_version=42.7.7

USER root

# ---------------------------------------------------------
# Install Java 17 + Maven (required for Spark 4 + dependency download)
# ---------------------------------------------------------
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk maven wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# ---------------------------------------------------------
# Remove pre-installed Spark 3.x from base image
# ---------------------------------------------------------
RUN rm -rf /usr/local/spark

# ---------------------------------------------------------
# Copy Spark 4.0.0 (already extracted on host)
# ---------------------------------------------------------
COPY pysparkjupyter/spark-4.0.0-bin-hadoop3 /usr/local/spark

ENV SPARK_HOME=/usr/local/spark
ENV PATH="$SPARK_HOME/bin:$PATH"

# ---------------------------------------------------------
# Install Python dependencies
# ---------------------------------------------------------
RUN pip install --no-cache-dir delta-spark==${delta_version} findspark

# ---------------------------------------------------------
# Download JAR dependencies (Delta, Kafka, Postgres)
# ---------------------------------------------------------
COPY pysparkjupyter/pom.xml /tmp/pom.xml

RUN \
    # 1. Dynamically find JAVA_HOME regardless of amd64 or arm64
    export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java)))) && \
    export PATH="$JAVA_HOME/bin:$PATH" && \
    \
    # 2. Ensure the output directory exists
    mkdir -p /usr/local/spark/jars && \
    \
    # 3. Run Maven with the --errors flag for better debugging if it fails
    mvn -f /tmp/pom.xml dependency:copy-dependencies \
        -DoutputDirectory=/usr/local/spark/jars \
        --errors && \
    \
    # 4. Cleanup
    rm -rf /root/.m2

# ---------------------------------------------------------
# Spark configuration
# ---------------------------------------------------------
ENV PYSPARK_SUBMIT_ARGS="pyspark-shell"

USER ${NB_UID}
