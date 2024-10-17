import asyncio
import logging
import random
import time

from pysqlx_engine._core.apool import PySQLXEnginePool  # Adjust the import as per your package structure

logging.basicConfig(level=logging.DEBUG)

MAX_CONCURRENT_WORKERS = 50
semaphore = asyncio.Semaphore(MAX_CONCURRENT_WORKERS)


# Simulating work with an async connection
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
