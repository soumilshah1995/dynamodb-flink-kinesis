
# Real Time,  Low latency Stream Pipeline with HUDI, Flink and Kinesis 
![hudi drawio](https://user-images.githubusercontent.com/39345855/212422470-2e341fa2-e4ef-470f-8719-0d78a930a1f0.png)



# Steps
### Step 1:Deploy the stack 
```
npx serverless config credentials --provider aws --key XXXXX  --secret XXX -o

npx sls deploy
```
### step 2: upload the jar provided to S3 in folder called Jar/

#### Download links
```
https://repo1.maven.org/maven2/org/apache/flink/flink-s3-fs-hadoop/1.13.0/flink-s3-fs-hadoop-1.13.0.jar


https://repo1.maven.org/maven2/org/apache/hudi/hudi-flink-bundle_2.12/0.10.1/hudi-flink-bundle_2.12-0.10.1.jar

```

### step 3: Head over to Kinesis Data Analytics and create a Notebook and upload the jar files while creating notebook

### step 4 : Execute sql commands

#### Execute Cell 1:
```
%flink.conf
execution.checkpointing.interval 5000
```

#### Execute Cell 3: Creating table for HUDI and Kinesis 

```
%flink.ssql(type=update)

DROP TABLE if exists tbl_orders;
CREATE TABLE tbl_orders (
    orderid VARCHAR,
    customer_id VARCHAR,
    ts TIMESTAMP(3),
    order_value DOUBLE,
    priority VARCHAR,
    WATERMARK FOR ts AS ts - INTERVAL '5' SECOND

)
WITH (
    'connector' = 'kinesis',
    'stream' = 'order_streams',
    'aws.region' = 'us-east-1',
    'scan.stream.initpos' = 'TRIM_HORIZON',
    'format' = 'json',
    'json.timestamp-format.standard' = 'ISO-8601'
    );
    


DROP TABLE if exists orders;
CREATE TABLE orders(
    orderid VARCHAR PRIMARY KEY NOT ENFORCED,
    customer_id VARCHAR,
    ts TIMESTAMP(3),
    order_value DOUBLE,
    priority VARCHAR
)
WITH (
    'connector' = 'hudi',
    'path' = 's3a://XXXXXXXXXXXX/tmp/',
    'table.type' = 'MERGE_ON_READ' ,
    'hoodie.embed.timeline.server' = 'false'

);
```



#### Execute Cell 4: Inserting from kinesis into HUDI
```
%ssql
INSERT INTO orders SELECT * FROM tbl_orders;
```

#### Insert data into DynamoDB 
```
Python dynamodb-insert.py

```
#### Athena tables
```
CREATE EXTERNAL TABLE `nonpartition_mor`(
  `_hoodie_commit_time` string, 
  `_hoodie_commit_seqno` string, 
  `_hoodie_record_key` string, 
  `_hoodie_partition_path` string, 
  `_hoodie_file_name` string, 
  `orderid` string, 
  `customer_id` string, 
  `priority` string,
   `ts` timestamp 
  )
ROW FORMAT SERDE 
  'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe' 
STORED AS INPUTFORMAT 
  'org.apache.hudi.hadoop.HoodieParquetInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat' 
LOCATION
  's3://XXXXXXXXXXXX/tmp'
  
```
## Enjoy 
