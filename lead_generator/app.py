from apify_client import ApifyClient
import time

# Initialize the ApifyClient
client = ApifyClient('apify_api_gK18DAYeTpaDac0JlVYnzAkZQep72r2cKEuA')

# Set up the API request for running the task
task_client = client.task('mrigaanksh~google-maps-scraper-task')  # Replace with your actual task ID

# Define task input parameters
task_input = {
    "locationQuery": "Ghaziabad, India",
    "searchStringsArray": ["restaurant"]
}

# Trigger the task
try:
    # Run the task and get the run details
    run = task_client.call(
        task_input=task_input,  # Pass the task input here
        timeout_secs=60,  # Timeout in seconds
        memory_mbytes=512  # Memory limit in megabytes
    )

    print(f"Task Run ID: {run['id']} - Status: {run['status']}")

    # Wait for the task to complete (Polling)
    while run['status'] != 'SUCCEEDED' and run['status'] != 'FAILED':
        print(f"Waiting for task to complete... Current status: {run['status']}")
        time.sleep(5)  # Sleep for 5 seconds before checking again
        run = task_client.get_run(run['id'])  # Fetch the latest run status

    if run['status'] == 'SUCCEEDED':
        # Once the task is done, fetch the dataset items
        dataset = client.dataset(run['defaultDatasetId'])
        items = []
        offset = 0
        limit = 1000

        while True:
            current_items = dataset.list_items(offset=offset, limit=limit).items
            items.extend(current_items)

            if len(current_items) < limit:
                break

            offset += limit

        print(f"Retrieved {len(items)} items from the dataset.")
        # Return the items or process them as needed
        print(items)

    else:
        print(f"Task failed with status: {run['status']}")

except Exception as e:
    print(f"An error occurred: {str(e)}")
