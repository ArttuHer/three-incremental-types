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

Understading medallion architecture inspired by Databricks is crucial, as different load types can be implemented in a different stages of the ETL process. In medallion architecture we have three data layers which represents data at different stages. 

**Bronze layer** \
The table in bronze layer correspond to the source in addition to potential metadata columns capturing, for example, load time and source system. For instance, bronze layer could be an archive of source system and is therefore the most important and protected layer in the architecture.

In our grocery store example, this could mean that the Bronze layer stores data for inserts (new items) but also if some value in a row is changed (e.g. price is changed). 

**Example**

| product | id   | price | version |
|---------|------|-------|---------|
| apple   | 1289 | 20    | 0       |

The entrepreneur updates price

| product | id   | price | version |
|---------|------|-------|---------|
| apple   | 1289 | 20    | 0       |
| apple   | 1289 | 15    | 1       |

We can see that now data in the Bronze layer have an updated version of the product with id 1289. 

**Silver layer** \
In the Silver layer, some modifications to data are made, to give an enterprise view of the data to stakeholders. The Silver layer could provide data for reporting, ML and more complex analytics and can be used as a source for any other type of projects as well. 

**Gold layer** \
Lastly, data in the Gold layer is ready for consumption and usually stored into a project-specific databases. 

## An example from Layers

**Source system**

We have the following information in the source system, representing the product, product category, price, and the handler who put the product to the enterprise resource system (ERP). 

| product | product_category   | price | handler |
|---------|------|-------|---------|
| apple   | 1289 | 20    | George Grocery       |
| apple   | 1289 | 20    | Arnold Assistant       |

**Bronze layer**

In the Bronze layer, we have added additional metadata to capture, when was the last time when this data was updated. 

| product | product_category   | price | handler | loaded_to_bronze |
|---------|------|-------|---------|---------|
| apple   | 1289 | 20    | George Grocery       |2024-06-13T08:33:05.000+00:00|
| apple   | 1289 | 20    | Arnold Assistant       |2024-06-13T08:33:05.000+00:00|

**Silver layer**

In the Silver we have made some changes: changed column names, added metadata and dropped handler column due to GDPR. 

| product_name | product_category   | price | loaded_to_bronze | loaded_to_silver |
|---------|------|-------|---------|---------|
| apple   | 1289 | 20    | 2024-06-13T08:33:05.000+00:00|2024-06-13T08:36:07.000+00:00|
| apple   | 1289 | 20    | 2024-06-13T08:33:05.000+00:00|2024-06-13T08:36:07.000+00:00|

**Gold layer**

Now the store manager wants to see how many apples there are in the warehouse. For reporting purposes, we could group this data to show aggregated values. It is a good habit to give pre-calculated data to BI report, because usually data analytics engines, such as Apache Spark, can make aggregations faster than regural BI tools. 

| product_name | product_category   | price | units |
|---------|------|-------|---------|
| apple   | 1289 | 20    | 2 |


## Incremental load

### Bookmark Table

### Merge Into

### Incremental with SDC 2

