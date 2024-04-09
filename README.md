## Three possible ways to implement incremental load

This repository describes three different ways to implement an incremental load and enhace the data processing of your data pipeline: Bookmark table; Merge into; 

## The Difference Between Full and Incremental load
**Full load**: When a data pipeline uses a full load, the entire dataset is loaded from the source which means that the source and the target are always in sync. Full load option is justified in a cases, for example, where there are not so many rows to be loaded or we don't want to store row-level history.

An example could be that we have a grocery store and the entrepreneur wants to know the current state of the warehouse when opening the store. Then, in the ETL process, we could just perform a full load and see the current state from the data. For example, if the warehouse has 20 apples on Sunday morning and 5 of them were sold during the day, the reading is 15 in Monday morning. This is just a simple example without any additional requirements, but the basic idea is explained. 

**Incremental load**: As the name suggests, the data is processed incrementally, meaning that the ETL process only loads the difference between the source and the target. 

Following the example above, if our ETL process has incremental load, it would check that there are 15 apples in the warehouse but 20 in the target. Then it only reduce the 5 apples from the target, rather than load all rows in the source. This is much faster way to perform a load operation, but on the other hand, it requires more maintenance. 


## ETL Process and Medallion Architecture

### ETL Process
Before moving on, let's briefly discuss about the ETL process to get a better understanding of the end to end process. ETL stands fro **Extract**, **Transform** and **Load**. 

**Extract**: During the extract step, data is ingested from the source and stored into a landing database. In the landing stage, data is in a raw format and usually not consumed by any end-users. 

**Transform**: In a transformation step, some changes are made to the data. Such changes could be, for example, drop PII data, rename columns or even make aggregations. 

**Load**: The data is loaded to a location where end-users can consume the data. 

### Medallion Architecture
Understading medallion architecture inspired by Databricks, is crucial, as loads can be implemented in a different stages of the ETL process. In medallion architecture we have three data layers which represents data at different stages. 

**Bronze layer** 
Ingest data from the source to bronze layer. In this layer, the data is in a raw state.  

**Silver layer**
Enrich and validate the data into a condition where end-users can use it.  

**Gold layer** 
Provide aggregated and pre-computed data to end-users, such as data analysts and BI dashboards. 

## Incremental load

### Bookmark Table

### Merge Into

### Incremental with SDC 2

