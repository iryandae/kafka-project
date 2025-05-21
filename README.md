# 🚨 Real-Time Warehouse Sensor Monitoring

Proyek ini bertujuan untuk memantau suhu dan kelembaban dari berbagai gudang secara real-time menggunakan **Apache Kafka** dan **Apache Spark Structured Streaming**. Sistem ini mampu mendeteksi kondisi kritis seperti suhu tinggi, kelembaban tinggi, atau keduanya secara bersamaan.

## Prasyarat

- Python 3.8+
- Apache Kafka
- Apache Spark 3.5.5
- Java 8 atau 11

## Struktur Proyek
```
├── venv-kafka/
    ├── bin/
    ├── include/
    ├── lib/
    ├── lib64/
    ├── share
    ├── pyvenv.cfg
├── producer_suhu.py
├── producer_kelembaban.py
├── spark_sensor_suhu.py
├── spark_sensor_kelembaban.py
├── spark_sensor_combined.py
├── docker-compose.yml
```
## Menjalankan Program

### 1. Jalankan Kafka & Zookeeper
Saya menggunakan docker untuk menjalankan Kafka dan Zookeeper dengan file `docker-compose.yml`
```
version: '3'
services:
  zookeeper:
    image: bitnami/zookeeper:3.8
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      - ALLOW_ANONYMOUS_LOGIN=yes

  kafka:
    image: bitnami/kafka:3.6
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      - KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper:2181
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
      - ALLOW_PLAINTEXT_LISTENER=yes
    depends_on:
      - zookeeper
```
File dijalankan pada terminal menggunakan command:
```bash
docker-compose up -d
```

### 2. Cek Topics pada Kafka
Masuk ke dalam kafka container
```bash
sudo docker exec -it <NAMA-KONTAINER> bash
```
Lalu cek `topics` yang ada dengan command:
```bash
kafka-topics.sh --bootstrap-server localhost:9092 --list
```
Pastikan nama yang muncul sama dengan nama yang ada di dalam file Python
![topics](https://github.com/user-attachments/assets/db3249e2-0a6d-4a4d-ad48-ebc6da19a964)
*Gambar 1: Kafka Topics*

Jika tidak ada output yang muncul, anda bisa menjalankan command berikut:
```bash
kafka-topics.sh --create --topic sensor-suhu-gudang --bootstrap-server localhost:9092
kafka-topics.sh --create --topic sensor-kelembaban-gudang --bootstrap-server localhost:9092
```
Cek kembali dan jika sudah berhasil kita bisa keluar dari container kafka dengan command `exit`

### 3. Masuk ke Virtual Environment
Sebelum menjalankan *producer* dan *consumer* saya menggunakan **virtual environment** untuk memastikan bahwa dependensi yang digunakan tidak tercampur dengan sistem Python global.
```bash
source venv-kafka/bin/activate
```
Tampilan akan beruhah seperti gambar di bawah jika sudah berhasil masuk ke virtual environment
![venv](https://github.com/user-attachments/assets/ebb3e6f3-e103-47a7-b837-00b322e74580)
*Gambar 2: Virtual Environment*

### 4. Jalankan Producer
Jalankan kedua *producer* pada terminal yang berbeda.
```bash
python producer_suhu.py
```

dan
```bash
python producer_kelembaban.py
```
*Producer* berhasil dijalankan ketika menghasilkan output seperti contoh di bawah:
![producer_suhu.py](https://github.com/user-attachments/assets/30210172-4646-448c-bdd0-44468ccc21ea)
*Gambar 3: Output producer_suhu.py*

![producer_kelembaban.py](https://github.com/user-attachments/assets/f93d8b52-30fb-4c43-a254-be85772ab1b9)
*Gambar 4: Output producer_kelembaban.py*

## 5. Jalankan PySpark Streaming
Setelah menjalankan producer, kita bisa menjalankan file sensor untuk menerima output dari producer dan mengolahnya. 
```bash
 python3 <NAMA-FILE>.py
```

Pada file `spark_sensor_suhu.py` dan `spark_sensor_kelembaban.py` akan muncul output seperti berikut:

```
-------------------------------------------
Batch: 1
-------------------------------------------
+---------+-------------------+----------+
|gudang_id|          timestamp|kelembaban|
+---------+-------------------+----------+
|       G2|2025-05-21 09:56:13|      66.0|
|       G1|2025-05-21 09:56:14|      69.0|
|       G3|2025-05-21 09:56:15|      70.0|
|       G2|2025-05-21 09:56:16|      75.0|
|       G1|2025-05-21 09:56:17|      72.0|
|       G3|2025-05-21 09:56:18|      74.0|
|       G2|2025-05-21 09:56:19|      69.0|
+---------+-------------------+----------+
```

Sedangkan output `spark_sensor_combined.py` akan memunculkan output berikut:

```
-------------------------------------------
Batch: 1
-------------------------------------------
+---------+--------------------+----+----------+--------------------+
|gudang_id|              window|suhu|kelembaban|              status|
+---------+--------------------+----+----------+--------------------+
|       G1|{2025-05-21 10:01...|  89|        68|Suhu tinggi, kele...|
|       G1|{2025-05-21 10:01...|  86|        68|Suhu tinggi, kele...|
|       G1|{2025-05-21 10:01...|  89|        65|Suhu tinggi, kele...|
|       G1|{2025-05-21 10:01...|  86|        65|Suhu tinggi, kele...|
|       G1|{2025-05-21 10:01...|  89|        74|Bahaya tinggi! Ba...|
|       G1|{2025-05-21 10:01...|  86|        74|Bahaya tinggi! Ba...|
|       G1|{2025-05-21 10:01...|  89|        80|Bahaya tinggi! Ba...|
|       G1|{2025-05-21 10:01...|  86|        80|Bahaya tinggi! Ba...|
|       G3|{2025-05-21 10:02...|  78|        70|                Aman|
|       G3|{2025-05-21 10:02...|  89|        70|Suhu tinggi, kele...|
|       G3|{2025-05-21 10:02...|  78|        65|                Aman|
|       G3|{2025-05-21 10:02...|  89|        65|Suhu tinggi, kele...|
|       G3|{2025-05-21 10:02...|  78|        78|Kelembaban tinggi...|
|       G3|{2025-05-21 10:02...|  89|        78|Bahaya tinggi! Ba...|
|       G3|{2025-05-21 10:02...|  78|        73|Kelembaban tinggi...|
|       G3|{2025-05-21 10:02...|  89|        73|Bahaya tinggi! Ba...|
|       G1|{2025-05-21 10:02...|  84|        68|Suhu tinggi, kele...|
+---------+--------------------+----+----------+--------------------+
```

