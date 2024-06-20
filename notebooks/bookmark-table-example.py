# Databricks notebook source
# MAGIC %md
# MAGIC ## Imports

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, NullType
from pyspark.sql import functions as F
from datetime import datetime

# COMMAND ----------

# MAGIC %md
# MAGIC ## Variables

# COMMAND ----------

source_db = 'inventory_management_db'
table_name = 'products'
sequence_by = 'product_added'

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define functions to create data

# COMMAND ----------

def define_source_data(source_data):
  source_schema = StructType([
      StructField("product", StringType(), True),
      StructField("product_category", IntegerType(), True),
      StructField("price", IntegerType(), True),
      StructField("handler", StringType(), True),
      StructField("warehouse", StringType(), True),
      StructField("product_added", StringType(), True)
  ])

  products_source = spark.createDataFrame(source_data, source_schema)
  #products_source = products_source.withColumn('product_added', F.to_timestamp('product_added'))
  products_source.display()
  products_source = products_source.orderBy(F.desc('product_added'))
  return products_source

# COMMAND ----------

def define_bookmark_table(bookmark_data):
  bookmark_schema = StructType([
    StructField("db_name", StringType(), True),
    StructField("table", StringType(), True),
    StructField("sequence_by", StringType(), True),
    StructField("sequence_by_value", StringType(), True),
    StructField("created_at", StringType(), True),
    StructField("modified_at", StringType(), True)
])
  bookmark_table = spark.createDataFrame(bookmark_data, bookmark_schema)
  return bookmark_table, bookmark_schema

# COMMAND ----------

def append_row(row, df):
  new_row_df = spark.createDataFrame(row, df.schema)
  df_appended = df.union(new_row_df)
  df_appended = df_appended.orderBy(F.desc('sequence_by_value'))
  return df_appended

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define data for the first time

# COMMAND ----------

data_source = [
    ('apple',1289,20, 'Arnold Assistant', 'B2C1', '2024-06-13T05:19:05.000+00:00'),
    ('apple',1289,20, 'George Grocery', 'A1C2', '2024-06-12T05:19:05.000+00:00')
  ]

products_source = define_source_data(data_source)

data_bookmark = [
]
bookmark_table, bookmark_schema = define_bookmark_table(data_bookmark)

# COMMAND ----------

# MAGIC %md # 1. Bookmark table example

# COMMAND ----------

# MAGIC %md
# MAGIC ## Update bookmark table

# COMMAND ----------

def get_bookmark_value(bookmark_table,bookmark_schema, source_db, table_name, sequence_by):
  if bookmark_table.count() == 0:
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_row = [(source_db, table_name, sequence_by, 0, current_time, current_time)]
    new_row_df = spark.createDataFrame(new_row, bookmark_schema)
    bookmark_table = bookmark_table.union(new_row_df)

# COMMAND ----------

get_bookmark_value(bookmark_table, bookmark_schema, source_db, table_name, sequence_by)

# COMMAND ----------

## Add new row to the source system
data_source = [
  ('orange',1210,5, 'Arnold Assistant', 'A2C1', '2024-06-14T08:24:05.000+00:00')
]
products_source_updated = append_row(data_source, products_source)
products_source_updated.orderBy(F.desc('product_added')).display()