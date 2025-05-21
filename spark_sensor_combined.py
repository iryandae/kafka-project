from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, window, when
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

spark = SparkSession.builder \
    .appName("SensorStreamingKelembaban") \
    .master("local[*]") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

suhu_schema = StructType([
    StructField("gudang_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("suhu", IntegerType(), True)
])

kelembaban_schema = StructType([
    StructField("gudang_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("kelembaban", IntegerType(), True)
])

suhu_stream = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "sensor-suhu-gudang") \
    .load() \
    .selectExpr("CAST(value AS STRING) as json") \
    .select(from_json("json", suhu_schema).alias("data")) \
    .select("data.*") \
    .withColumn("timestamp", to_timestamp("timestamp")) \
    .withWatermark("timestamp", "1 minute") \
    .withColumn("window", window(col("timestamp"), "10 seconds"))

kelembaban_stream = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "sensor-kelembaban-gudang") \
    .load() \
    .selectExpr("CAST(value AS STRING) as json") \
    .select(from_json("json", kelembaban_schema).alias("data")) \
    .select("data.*") \
    .withColumn("timestamp", to_timestamp("timestamp")) \
    .withWatermark("timestamp", "1 minute") \
    .withColumn("window", window(col("timestamp"), "10 seconds"))

joined_stream = suhu_stream.join(
    kelembaban_stream,
    on=["gudang_id", "window"],
    how="inner"
).select(
    suhu_stream.gudang_id,
    suhu_stream.window,
    suhu_stream.suhu,
    kelembaban_stream.kelembaban
)

joined_stream = joined_stream.withColumn(
    "status",
    when((col("suhu") > 80) & (col("kelembaban") > 70), "Bahaya tinggi! Barang berisiko rusak")
    .when((col("suhu") > 80) & (col("kelembaban") <= 70), "Suhu tinggi, kelembaban normal")
    .when((col("suhu") <= 80) & (col("kelembaban") > 70), "Kelembaban tinggi, suhu aman")
    .otherwise("Aman")
)

query = joined_stream.writeStream.format("console") \
    .outputMode("append") \
    .start()

query.awaitTermination()
