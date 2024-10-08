import concurrent.futures
import logging
import random
import time

from pysqlx_engine._core.pool.pool import PySQLXEnginePoolSync

logging.basicConfig(level=logging.DEBUG)


# Assuming you have a method in the pool to acquire and release connections
def simulate_work(pool: PySQLXEnginePoolSync):
	try:
		with pool.connection() as conn:
			# Simulate some work with the connection
			resp = conn.query_first("SELECT 1 as a")
			assert resp.a == 1
			time.sleep(random.uniform(0.1, 0.5))
	except Exception as e:
		logging.error(f"Error occurred: {e}")


def stress_test_sync_pool(pool, num_threads=50, num_requests=1000):
	with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
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
