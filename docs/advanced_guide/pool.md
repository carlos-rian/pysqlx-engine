# **Create a pool with concurrent connections**

The PySQLXEngine allows you to create a pool of connections to the database. 
You can reuse and recycle connections to the database, which can improve the performance of your application.

This example will use the `SQLite` database.

## Introduction

The PySQLXEngine provides two types of pools: `PySQLXEnginePool` for asynchronous connections and `PySQLXEnginePoolSync` for synchronous connections.

Both work similarly, but the asynchronous pool is designed to work with `asyncio` and the synchronous pool with threads.

**Parameters**

- `uri: str`: Database URI, e.g. `sqlite:./dev.db`
- `min_size: int`: Minimum number of connections in the pool, you can start the pool with the minimum number of connections
- `max_size: int`: (default: 10): Maximum number of connections in the pool
- `conn_timeout: float`: (default: 30.0) Connection timeout in seconds, waiting for a connection to be available, case the timeout is reached, a `PoolTimeoutError` is raised
- `keep_alive: float`: (default: 60 * 15) Time to keep the connection alive in the pool
- `check_interval: float`: (default: 5.0) Interval to check the connections in the pool
- `monitor_batch_size: int`: (default: 10)  Number of connections to check per interval

Easily create a pool of connections and start reusing them in your application.


### Simple example

**Creating and starting the pool**

=== "**Async**"
    ```py linenums="1" hl_lines="6" title="main.py"
    import asyncio
    from pysqlx_engine import PySQLXEnginePool

    async def main():
        pool = PySQLXEnginePool(uri="sqlite:./dev.db", min_size=5)
        await pool.start() # Start the pool

    asyncio.run(main())
    ```
=== "**Sync**"
    ```py linenums="1" hl_lines="6" title="main.py"
    # import
    from pysqlx_engine import PySQLXEnginePoolSync

    def main():
        pool = PySQLXEnginePoolSync(uri="sqlite:./dev.db", min_size=5)
        pool.start() # Start the pool
    
    main()
    ```


**Taking a connection from the pool**

=== "**Async**"
    ```py linenums="1" hl_lines="8-11" title="main.py"
    import asyncio
    from pysqlx_engine import PySQLXEnginePool

    async def main():
        pool = PySQLXEnginePool(uri="sqlite:./dev.db", min_size=5)
        await pool.start() # Start the pool

        async with pool.connection() as conn:
            # Use the connection
            resp = await conn.query_first("SELECT 1 as a")
            print(resp) # Output: BaseRow(a=1)

    asyncio.run(main())
    ```
=== "**Sync**"
    ```py linenums="1" hl_lines="8-11" title="main.py"
    # import
    from pysqlx_engine import PySQLXEnginePoolSync

    def main():
        pool = PySQLXEnginePoolSync(uri="sqlite:./dev.db", min_size=5)
        pool.start() # Start the pool

        with pool.connection() as conn:
            # Use the connection
            resp = conn.query_first("SELECT 1 as a")
            print(resp) # Output: BaseRow(a=1)
    
    main()
    ```

**Stopping the pool**

=== "**Async**"
    ```py linenums="1" hl_lines="10" title="main.py"
    import asyncio
    from pysqlx_engine import PySQLXEnginePool

    async def main():
        pool = PySQLXEnginePool(uri="sqlite:./dev.db", min_size=5)
        await pool.start() # Start the pool

        # Use the pool

        await pool.stop() # Stop the pool

    asyncio.run(main())
    ```

=== "**Sync**"
    ```py linenums="1" hl_lines="10" title="main.py"
    # import
    from pysqlx_engine import PySQLXEnginePoolSync

    def main():
        pool = PySQLXEnginePoolSync(uri="sqlite:./dev.db", min_size=5)
        pool.start() # Start the pool

        # Use the pool

        pool.stop() # Stop the pool
    
    main()
    ```

**Complete example**

=== "**Async**"
    ```py title="main.py"
    import asyncio
    from pysqlx_engine import PySQLXEnginePool

    async def main():
        pool = PySQLXEnginePool(uri="sqlite:./dev.db", min_size=5)
        await pool.start() # Start the pool

        async with pool.connection() as conn:
            # Use the connection
            resp = await conn.query_first("SELECT 1 as a")
            print(resp) # Output: BaseRow(a=1)

        await pool.stop() # Stop the pool

    asyncio.run(main())
    ```

=== "**Sync**"
    ```py title="main.py"
    # import
    from pysqlx_engine import PySQLXEnginePoolSync

    def main():
        pool = PySQLXEnginePoolSync(uri="sqlite:./dev.db", min_size=5)
        pool.start() # Start the pool

        with pool.connection() as conn:
            # Use the connection
            resp = conn.query_first("SELECT 1 as a")
            print(resp) # Output: BaseRow(a=1)

        pool.stop() # Stop the pool

    main()
    ```


## Concurrent connections example

Create a `main.py` file and add the code examples below.


=== "**Async**"
    ```py title="main.py"
    import asyncio
    import logging
    import random
    import time

    from pysqlx_engine import PySQLXEnginePool, LOG_CONFIG

    LOG_CONFIG.PYSQLX_DEV_MODE = True
    LOG_CONFIG.PYSQLX_SQL_LOG = True
    LOG_CONFIG.PYSQLX_USE_COLOR = True
    LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True

    logging.basicConfig(level=logging.DEBUG)

    MAX_CONCURRENT_WORKERS = 50
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_WORKERS)


    async def simulate_work_async(pool: PySQLXEnginePool):
        async with semaphore:  # Limit the number of simultaneous workers
            try:
                async with pool.connection() as conn:
                    # Simulate some async work
                    resp = await conn.query_first("SELECT 1 as a")
                    assert resp.a == 1
                    await asyncio.sleep(random.uniform(0.1, 0.5))
            except Exception as e:
                logging.error(f"Error occurred: {e}")


    async def stress_test_async_pool(pool, num_requests=1000):
        tasks = [simulate_work_async(pool) for _ in range(num_requests)]
        await asyncio.gather(*tasks)


    if __name__ == "__main__":
        start = time.monotonic()

        async def main():
            # Initialize your async pool here
            pool = PySQLXEnginePool(
                uri="sqlite:./dev.db", min_size=5, max_size=30, conn_timeout=60, check_interval=0.5
            )  # Adjust parameters as needed
            await pool.start()  # Ensure to start the pool if there's such a method
            await stress_test_async_pool(pool)
            await pool.stop()  # Properly close the pool after testing

        asyncio.run(main())
        end = time.monotonic()
        logging.info(f"Time taken: {end - start:.2f} seconds")
    ```

=== "**Sync**"

    ```py title="main.py"
    import concurrent.futures
    import logging
    import random
    import time

    from pysqlx_engine import PySQLXEnginePoolSync, LOG_CONFIG

    LOG_CONFIG.PYSQLX_DEV_MODE = True
    LOG_CONFIG.PYSQLX_SQL_LOG = True
    LOG_CONFIG.PYSQLX_USE_COLOR = True
    LOG_CONFIG.PYSQLX_ERROR_JSON_FMT = True

    logging.basicConfig(level=logging.DEBUG)

    MAX_CONCURRENT_WORKERS = 50
    #


    def simulate_work(pool: PySQLXEnginePoolSync):
        try:
            with pool.connection() as conn:
                # Simulate some work with the connection
                resp = conn.query_first("SELECT 1 as a")
                assert resp.a == 1
                time.sleep(random.uniform(0.1, 0.5))
        except Exception as e:
            logging.error(f"Error occurred: {e}")


    def stress_test_sync_pool(pool, num_requests=1000):
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_WORKERS) as executor:
            # Submit multiple tasks to simulate concurrent connections
            futures = [executor.submit(simulate_work, pool) for _ in range(num_requests)]
            concurrent.futures.wait(futures)


    if __name__ == "__main__":
        # Initialize your pool here
        start = time.monotonic()
        pool = PySQLXEnginePoolSync(
            uri="sqlite:./dev.db", min_size=5, max_size=30, conn_timeout=60, check_interval=0.5
        )  # Adjust parameters as needed
        pool.start()
        stress_test_sync_pool(pool)
        pool.stop()
        end = time.monotonic()
        logging.info(f"Time taken: {end - start:.2f} seconds")
    ```

Running the code using the terminal

<div class="termy">

```console

$ python3 main.py
...

INFO:pysqlx_engine:Pool: Starting the connection pool.
DEBUG:pysqlx_engine:Pool: New connection created: <pysqlx_engine._core.apool.ConnInfo 'conn-1' at 0x7f24301e78c0> PoolSize: 1
...
INFO:pysqlx_engine:Pool: Initialized with 5 connections.
DEBUG:pysqlx_engine:Worker: Worker-1-ConnectionMonitor starting.
INFO:pysqlx_engine:Pool: Workers started.
DEBUG:pysqlx_engine:Async -> Starting task: ConnectionMonitor
DEBUG:pysqlx_engine:Async -> Running task: ConnectionMonitor
INFO:pysqlx_engine:Monitor: Started monitoring the pool.
...
DEBUG:pysqlx_engine:Getting a ready connection.
DEBUG:pysqlx_engine:Acquired semaphore in 0.00001 seconds
DEBUG:pysqlx_engine:Pool: Growing: False Waiting: 1
DEBUG:pysqlx_engine:Pool: Connection: <pysqlx_engine._core.apool.ConnInfo 'conn-1' at 0x7f24301e78c0> retrieved in 0.00018 seconds.
DEBUG:pysqlx_engine:Pool: Growing: False Waiting: 0
DEBUG:pysqlx_engine:Pool: Connection returned to pool: <pysqlx_engine._core.apool.ConnInfo 'conn-1' at 0x7f24301e78c0>
...
DEBUG:pysqlx_engine:Pool: Connection returned to pool: <pysqlx_engine._core.apool.ConnInfo 'conn-1' at 0x7f24301e78c0>
...
INFO:pysqlx_engine:Pool: Stopping the connection pool.
INFO:pysqlx_engine:Removed: <pysqlx_engine._core.apool.ConnInfo 'conn-1' at 0x7f24301e78c0> from pool, the conn was open for 5.36555 secs
...
DEBUG:pysqlx_engine:Worker: Worker-1-ConnectionMonitor finishing.
INFO:pysqlx_engine:Monitor: Stopped monitoring the pool.
DEBUG:pysqlx_engine:Async -> Stopping task: ConnectionMonitor
INFO:pysqlx_engine:Pool: All workers stopped and connections closed.
```
</div>