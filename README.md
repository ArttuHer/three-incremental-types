## Three possible ways to implement incremental load

This repository describes three different ways to implement an incremental load and enhace the data processing of your data pipeline. 

### The Difference Between Full and Incremental load
**Full load**: When a data pipeline uses a full load, the entire dataset is loaded from the source which means that the source and the target are always in sync. Full load option is justified in a cases, for example, where there are not so many rows to be loaded or we don't want to store row-level history.

An example could be that we have a grocery store and the entrepreneur wants to know the current state of the warehouse when opening the store. Then, in the ETL process, we could just perform a full load and see the current state from the data. For example, if the warehouse has 20 apples on Sunday morning and 5 of them were sold during the day, the reading is 15 in Monday morning. This is just a simple example without any additional requirements, but the basic idea is explained. 

**Incremental load**: As the name suggests, the data is processed incrementally, meaning that the ETL process only loads the difference between the source and the target. 

Following the example above, if our ETL process has incremental load, it would check that there are 15 apples in the warehouse but 20 in the target. Then it only reduce the 5 apples from the target, rather than load all rows in the source. This is much faster way to perform a load operation, but on the other hand, it requires more maintenance. 