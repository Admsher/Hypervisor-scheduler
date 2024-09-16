import datetime
from threading import Thread, Lock, Event
from queue import SimpleQueue
import time
import pandas as pd

# Define function execution times and intervals
functions_info = {
    'func1': {'last_run': 0, 'interval': 40, 'duration': 10},
    'func2': {'last_run': 0, 'interval': 20, 'duration': 5},
    'func3': {'last_run': 0, 'interval': 10, 'duration': 5},
    'func4': {'last_run': 0, 'interval': 10, 'duration': 5},
}

# Define a generic function executor
def execute_function(func_name):
    """Generic function executor based on the function name."""
    # Fetch the duration for the specific function
    duration = functions_info[func_name]['duration']
    log_function_info(func_name, 'started.', duration)
    time.sleep(duration)
    log_function_info(func_name, 'finished.', duration)

# Map function names to the generic function call
function_map = {
    'func1': lambda: execute_function('func1'),
    'func2': lambda: execute_function('func2'),
    'func3': lambda: execute_function('func3'),
    'func4': lambda: execute_function('func4'),
}

# Lock for thread-safe updates and event to manage function execution
lock = Lock()
execution_event = Event()
execution_event.set()  # Allow execution to start

# Queue to manage the function execution order
execution_queue = SimpleQueue()
scheduled_functions = set()  # Set to keep track of scheduled functions

# List to collect log entries
log_entries = []

def log_function_info(func_name, action, duration):
    """Log the start and finish times of functions."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entries.append({'Function': func_name, 'Action': action, 'Duration': duration})
    print(f"{timestamp} - {func_name} {action} Duration: {duration} seconds")

def run_function(func_name):
    """Run the specified function."""
    with lock:
        functions_info[func_name]['last_run'] = time.time()
        # Run the function based on the map
        function_map[func_name]()  # Execute the function

def scheduler():
    """Scheduler that adds functions to the execution queue based on their intervals."""
    while True:
        now = time.time()
        with lock:
            for func_name, info in functions_info.items():
                next_run_time = info['last_run'] + info['interval']
                if now >= next_run_time:
                    if func_name not in scheduled_functions:
                        execution_queue.put(func_name)
                        scheduled_functions.add(func_name)
        time.sleep(1)  # Check every second

def worker():
    """Worker that processes functions from the execution queue."""
    while True:
        # Wait for the execution event to be set
        execution_event.wait()
        func_name = execution_queue.get()
        # Set the event to block other function starts
        execution_event.clear()
        run_function(func_name)
        # Remove the function from the set after execution
        with lock:
            scheduled_functions.remove(func_name)
        # Re-set the event to allow the next function to start
        execution_event.set()

# if __name__ == "__main__":
#     # Start the scheduler and worker threads
#     Thread(target=scheduler, daemon=True).start()
#     Thread(target=worker, daemon=True).start()

#     # Run the main loop for 2 minutes
#     start_time = time.time()
#     total_duration = 2 * 60  # 2 minutes

#     while True:
#         elapsed_time = time.time() - start_time
#         if elapsed_time >= total_duration:
#             break
#         time.sleep(1)

#     # Save logs to Excel
#     df = pd.DataFrame(log_entries)
#     df.to_excel('function_logs.xlsx', index=False)

#     print("Log data has been written to function_logs.xlsx")
