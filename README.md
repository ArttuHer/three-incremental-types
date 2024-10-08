## Three possible ways to implement incremental load

This document describes three different ways to implement an incremental load and it is motivated by Databricks medallion architecture and features. Incremental load types are: **Bookmark table**; **Merge into** and **Slowly Chaning Dimensions type 2**.

## ETL Process
Before moving on, let's briefly discuss about the ETL process to get a better understanding of the end to end process. ETL stands for **Extract**, **Transform** and **Load**. 

**Extract** \
During the extract step, data is ingested from the source system and stored in a raw format. A common practice is to add metadata, such as loaded timestamps and other useful information. Data is not usually consumed by end-users at this stage. 

**Transform** \
In the transformation step, some changes are made to the data. Such changes could be, for example, droping personal information and renaming columns.

**Load** \
The data is loaded to a location where end-users can consume the data. 

## The Difference Between Full and Incremental load
**Full load**: When an ETL process uses a full load, the entire dataset is loaded from the source which means that the source and the target are always in sync. Full load option is justified in cases, for example, where there are not so many rows to be loaded or we want that target represents the source.

An example could be that we have a grocery store and the entrepreneur wants to know the current state of the warehouse every morning. Then, in the ETL process, we could just perform a full load and see the current state from the data. For example, if the warehouse has 20 apples on Sunday morning and 5 of them were sold during the day, the amount is 15 in Monday morning. 

**Incremental load**: As the name suggests, the data is processed incrementally, meaning that the ETL process only loads the difference between the source and the target. 

Following the example above, if we have configured incremental load, it would check that there are 15 apples in the warehouse but 20 in the target table. Then, 5 apples is reduced from the target table, rather than loading all rows from the source and replace the target.

## Medallion Architecture

Understading medallion architecture inspired by Databricks is crucial, as different load types can be implemented in different layers. In medallion architecture we have three data layers which represents data at different stages. 

**Bronze layer** \
The table in bronze layer correspond to the source system in addition to potential metadata columns capturing, for example, load time and the name  of the source system. For instance, bronze layer could act as an archive (cold storage) of the source system and is therefore the most important and protected layer in the architecture.

**Silver layer** \
In the Silver layer, some modifications to data are made, to give an enterprise view of the data to stakeholders. The Silver layer could provide data for reporting, ML and more complex analytics and can be used as a source for any other type of projects as well. 

**Gold layer** \
Lastly, data in the Gold layer is ready for consumption and usually stored into a project-specific databases. 

## An example from Layers

**Source system**

We have the following information in the source system:

 |-- product: string   
 |-- product_category: integer   
 |-- price: integer  
 |-- handler: string  
 |-- warehouse: string  
 |-- product_added: timestamp

| product | product_category   | price | handler |warehouse|product_added|
|---------|------|-------|---------|---------|---------|
| apple   | 1289 | 20    | Arnold Assistant       |B2C1|2024-06-13T05:19:05|
| apple   | 1289 | 20    | George Grocery       |A1C2|2024-06-12T05:19:05|

**Bronze layer**

In the Bronze layer, we have added additional metadata to capture, when was the last time when this data was updated. 

| product | product_category   | price | handler |warehouse|product_added| loaded_to_bronze |
|---------|------|-------|---------|---------|---------|---------|
| apple   | 1289 | 20    | Arnold Assistant       |B2C1|2024-06-13T05:19:05|2024-06-13T08:33:05|
| apple   | 1289 | 20    | George Grocery       |A1C2|2024-06-12T05:19:05|2024-06-13T08:33:05|

**Silver layer**

In the Silver we have made some changes: changed column names, added metadata and dropped handler column due to GDPR. 

| product_name | product_category   | price |warehouse|product_added| loaded_to_bronze | loaded_to_silver |
|---------|------|-------|---------|---------|---------|---------|
| apple   | 1289 | 20    |B2C1| 2024-06-13T05:19:05|2024-06-13T08:33:05|2024-06-13T08:36:07|
| apple   | 1289 | 20    |A1C2| 2024-06-12T05:19:05|2024-06-13T08:33:05|2024-06-13T08:36:07|

**Gold layer**

Now the store manager wants to see how many apples there are in all warehouses. For reporting purposes, we could group this data by product name to show aggregated values. It is a good habit to give pre-calculated data to BI report, because usually data analytics engines, such as Apache Spark, can make aggregations faster than regural BI tools. 

This query can be used to create this example table:  
`SELECT product_name, product_category, price, units
FROM <table_name> GROUP BY product_name`

| product_name | product_category   | price | units |
|---------|------|-------|---------|
| apple   | 1289 | 20    | 2 |


## Incremental load
Let's image that source system does not store values for a long time and for reporting purposes, we need data from a longer period. Previously we just performed a full load to show the status in the warehouse, but now the store manager wants to make a figure to show how volumes in the warehouse have changed over time. 

### Bookmark Table
Bookmark table is a table which tracks the latest update in the target table. In our example, it could have the following information: 

 |-- db_name: string   
 |-- table: integer   
 |-- sequence_by: string    
 |-- sequence_by_value: string  
 |-- created_at: timestamp    
 |-- modified_at: timestamp

From now on, the name of the source database is 'inventory_management_db' and table name is 'products'.  
Our bookmark table could look like this, based on the state of the source system above: 

| db_name | table   | sequence_by | sequence_by_value |created_at|modified_at|
|---------|------|-------|---------|---------|---------|
| inventory_management_db   | products | product_added    | 2024-06-13T05:19:05 | 2024-06-13T08:33:05|2024-06-13T08:33:05|


A new row has been added to the source database (the last row). Instead of full load, we could append the latest row to the target table. 
| product | product_category   | price | handler |warehouse|product_added|
|---------|------|-------|---------|---------|---------|
| apple   | 1289 | 20    | Arnold Assistant       |B2C1|2024-06-13T05:19:05|
| apple   | 1289 | 20    | George Grocery       |A1C2|2024-06-12T05:19:05|
| orange   | 1210 | 5    | Arnold Assistant       |A2C1|**2024-06-14T08:24:05**|

Firstly, our code checks that the previous sequence by value in the bookmark table is **2024-06-13T05:19:05**. Secondly, it would load values that has been wrote after the value in the bookmark table. Lastly, bookmark table is updated. 

**Now bronze looks like this**
| product | product_category   | price | handler |warehouse|product_added| loaded_to_bronze |
|---------|------|-------|---------|---------|---------|---------|
| orange   | 1210 | 5    | Arnold Assistant       |A2C1|**2024-06-14T08:24:05**|2024-06-14T08:33:05|
| apple   | 1289 | 20    | Arnold Assistant       |B2C1|2024-06-13T05:19:05|2024-06-13T08:33:05|
| apple   | 1289 | 20    | George Grocery       |A1C2|2024-06-12T05:19:05|2024-06-13T08:33:05|

**Bookmark table is updated**
| db_name | table   | sequence_by | sequence_by_value |created_at|modified_at|
|---------|------|-------|---------|---------|---------|
| inventory_management_db   | products | product_added    | **2024-06-14T08:24:05** | 2024-06-12T07:19:05| 2024-06-14T08:33:05|

### Merge Into
We can use merge into (inspired by Databricks https://docs.databricks.com/en/sql/language-manual/delta-merge-into.html) to perform an incremental load. 
Let's imagine that there is another table called 'product_log' which have two columns: product_category and log_id to capture some information about the process. Rows are deleted from the source periodically and we need to store historical values for further processing. 

In the previous example, it was assumed that there is a column which can be used to order the data to descending order. However, in this case, we don't have such column and need to change our approach to handle the incremental load. 
Databricks merge into can help us to tackle this problem. 

We need to have two tables: one table performing full load every load time and the other table, where rows are incrementally added. 

**product_log** full load table from the source: 
| product_category | log_id   | explanation |
|---------|------| ------|
| 1210   | 4459 | fruits|
| 1289   | 4459 | fruits|

Let's assume that delete and insert statements are performed against the source system. Now full load table is updated: 
| product_category | log_id   | explanation |
|---------|------| ------|
| 1210   | 4459 | fruits|
| 1215   | 4450 | bread|

We can see that  product_category **1289** was dropped and **1215** was added. Now our code will compare the full load table and target table and see that product_category and log_id combination **1215** and **4450** is not there. 
As a result, new row will be added to the target: 

| product_category | log_id   | explanation |
|---------|------| ------|
| 1210   | 4459 | fruits|
| 1289   | 4459 | fruits|
| 1215   | 4450 | bread|

How about updates? We can also configure that updates are added as a new row, if there is a use case where row-level history is needed. 
Bread category is updated in the source: 

| product_category | log_id   | explanation |
|---------|------| ------|
| 1210   | 4459 | fruits|
| 1215   | 4450 | artisan-bread|

Now target table is updated: 

| product_category | log_id   | explanation |
|---------|------| ------|
| 1210   | 4459 | fruits|
| 1289   | 4459 | fruits|
| 1215   | 4450 | bread|
| 1215   | 4450 | artisan-bread|

#### Pros and cons in Merge into
**Pros**
- Easy configuration for DML statements
- Allows other configuration options, like schema evolution and not matched/matched
- No need to worry about columns used to ordering
  
**Cons**
- Full load is performed every time
- If source table is big, it can take some time to perform full load
### Incremental with SDC 2
The last example is done with using slowly changing dimensions (inspired by Databricks https://docs.databricks.com/en/delta-live-tables/cdc.html) and its' option 2. Option 1 overwrites a row and option 2 adds a new row and accumulate row-level history. 
We could have a use case where the store manager want's to keep historical values for future usage but in the current report, she wants to use only the latest value of each row. 

We could use incremental load with bookmark table on the Bronze layer and on the Silver layer we have one "staging" table, which has all Bronze layer data (+ additional metadata / other changes) with row-level history and a table which has only the latest record of each item and consumed by the manager. 

In the simplest terms, we could use Databricks Delta Live Tables to apply these changes from this staging table to Silver table. We just need to define a combination of keys which can be used to determine which row is the latest. In this example, we could use **product_category** and **product_added**. 

**Staging table** could look like this. We can see that there are two apples and two oranges added at different times. 
| product | product_category   | price | handler |warehouse|product_added|
|---------|------|-------|---------|---------|---------|
| apple   | 1289 | 20    | Arnold Assistant       |B2C1|2024-06-13T05:19:05|
| apple   | 1289 | 20    | George Grocery       |A1C2|2024-06-12T05:19:05|
| orange   | 1210 | 5    | Arnold Assistant       |A2C1|2024-06-14T08:24:05|
| orange   | 1210 | 5    | Arnold Assistant       |A2C1|2024-06-14T10:24:05|

With Delta Live tables, we could read from this staging table and create the silver table containing only the latest rows. 

**Silver table**. Now the store manager would see the current status of his warehouse, without removing any data, leaving it for future usage and avoiding full load to source system. 
| product | product_category   | price | handler |warehouse|product_added|
|---------|------|-------|---------|---------|---------|
| apple   | 1289 | 20    | Arnold Assistant       |B2C1|2024-06-13T05:19:05|
| orange   | 1210 | 5    | Arnold Assistant       |A2C1|2024-06-14T10:24:05|

