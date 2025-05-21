from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp
from pyspark.sql.types import StructType, StringType, DoubleType, TimestampType

spark = SparkSession.builder \
    .appName("SensorStreamingKelembaban") \
    .master("local[*]") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

schema_kelembaban = StructType() \
    .add("gudang_id", StringType()) \
    .add("timestamp", StringType()) \
    .add("kelembaban", DoubleType())

df_kelembaban = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "sensor-kelembaban-gudang") \
    .load()

parsed_kelembaban = df_kelembaban.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json("json", schema_kelembaban).alias("data")) \
    .select("data.*") \
    .withColumn("timestamp", to_timestamp("timestamp"))  # ubah jadi timestamp tipe

query = parsed_kelembaban.writeStream \
    .outputMode("append") \
    .format("console") \
    . trigger(processingTime="10 seconds") \
    .start()

query.awaitTermination()
