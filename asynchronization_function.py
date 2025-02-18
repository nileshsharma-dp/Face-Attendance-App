import asyncio

# Asynchronous function
async def fetch_data():
    print("Fetching data...")
    await asyncio.sleep(5)  # Simulate a delay (e.g., downloading data)
    print("Data fetched")

# Another async function
async def process_data():
    print("Processing data...")
    await asyncio.sleep(3)  # Simulate processing time
    print("Data processed")

# Main asynchronous function that runs the tasks
async def main():
    # Run both async functions concurrently
    await asyncio.gather(fetch_data(), process_data())
    print("All tasks completed")

# Run the event loop
asyncio.run(main())
