# Performance Evaluation

## Setup
<img src="./RetroWoT Middleware.png" width="100%" alt="description">

To evaluate our approach, we created a performance benchmark as shown in the figure. 
We used a legacy device that does not provide a Thing Description and measure in the different components of our middleware the required time.
(see t1, t2, t3, t4). 

We used as legacy device the Micro:Bit V2 during our evaluation.
The Micro:Bit allows to be modified, such that a variety of different service capabilities can be tested.
This allows to evaluate our middleware against the main factor that changes in the integration of legacy devices. 
The number of available services of a device.

To evaluate the performance, we created a arduino ide script that allows to setups with different numbers of service capabilities.

For details, see the [implementation.](./bluetooth-device-setup.ino)

The script, to measure the performance in the middleware is provided within the implementation as a python program. (see [performance-study-retrowot.py](../../implementation/retrowot/retrowot/performance-study-retrowot.py))

## Results

- The raw data can be found under [performance-evaluation-raw-data.txt](./performance-evaluation-raw-data.txt).
- The prepared data can be found under [performance-evaluation.xlsx](./performance-evaluation.xlsx).