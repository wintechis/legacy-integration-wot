# Performance Evaluation

## Setup
<img src="./RetroWoT Middleware.png" width="100%" alt="description">

To evaluate our approach, we designed a performance benchmark as illustrated in the figure above. Our setup uses a legacy device, specifically a Micro:Bit V2, which does not provide a Thing Description. We measure the time required in different components of our middleware (t1, t2, t3, t4).

The Micro:Bit V2 was chosen for its flexibility, allowing us to modify it to test a variety of services. This versatility enables us to evaluate our middleware against the primary variable in legacy device integration: the number of available services.

For our evaluation, we developed:
- An Arduino IDE script that sets up different numbers of services on the Micro:Bit V2. (See bluetooth-device-setup.ino for implementation details)
- A Python program to measure performance within the middleware. (see [performance-study-retrowot.py](../../implementation/retrowot/retrowot/performance-study-retrowot.py))

To maintain consistency, we ensured that the service enrichment component is always active. 
This was achieved by using only services from a Standardization Organization for which we had created Thing Models based on their Service specifications.



## Results

- The raw data can be found under [performance-evaluation-raw-data.txt](./performance-evaluation-raw-data.txt).
- The prepared data can be found under [performance-evaluation.xlsx](./performance-evaluation.xlsx).