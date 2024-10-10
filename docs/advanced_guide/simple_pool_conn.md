# **Simple pool with concurrent connections**

The PySQLXEngine allows you to create a pool of connections to the database. 
You can reuse and recycle connections to the database, which can improve the performance of your application.

This example will use the `SQLite` database.

Create a `main.py` file and add the code examples below.


=== "**Async**"
    ``` py
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

    ``` py
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
```

</div>