from apify_client import ApifyClient
import time
import csv

# Initialize the ApifyClient
client = ApifyClient('apify_api_gK18DAYeTpaDac0JlVYnzAkZQep72r2cKEuA')

# Set up the API request for running the task
task_client = client.task('mrigaanksh~google-maps-scraper-task')  # Replace with your actual task ID

# Define task input parameters
task_input = {
    "locationQuery": "Ghaziabad, India",
    "searchStringsArray": ["restaurant"]
}

# Define CSV file name and open it for writing (will append in the loop)
csv_filename = "lead.csv"

# Open the CSV file once outside the loop for writing
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    # Create CSV DictWriter and write the header
    writer = None

    for i in range(5):  # Loop to fetch data 5 times
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
                items_dict = {}  # Create a dictionary to store items

                offset = 0
                limit = 5  # Fetch exactly 5 items
                counter = 1  # Counter for assigning keys in dictionary

                # Retrieve up to 5 items in total (across multiple API calls if necessary)
                while len(items_dict) < limit:
                    current_items = dataset.list_items(offset=offset, limit=limit - len(items_dict)).items
                    for item in current_items:
                        # Save each item in the dictionary with a unique key
                        items_dict[f"Lead {counter}"] = item
                        counter += 1
                    
                    offset += len(current_items)  # Increment the offset to fetch next batch

                    # If we've reached the limit, stop fetching more items
                    if len(current_items) < (limit - len(items_dict)):
                        break

                print(f"Retrieved {len(items_dict)} items from the dataset.")

                # If this is the first time writing to the CSV, write the header
                if writer is None:
                    writer = csv.DictWriter(file, fieldnames=items_dict["Lead 1"].keys())
                    writer.writeheader()

                # Write each item to the CSV
                for key, item in items_dict.items():
                    writer.writerow(item)

                print(f"Leads saved to {csv_filename}")

            else:
                print(f"Task failed with status: {run['status']}")

        except Exception as e:
            print(f"An error occurred during iteration {i + 1}: {str(e)}")
