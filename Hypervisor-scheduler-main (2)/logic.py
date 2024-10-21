import datetime
from threading import Thread, Lock, Event
from queue import SimpleQueue,PriorityQueue
import time
import pandas as pd
import math
import schedule
first_instance=[]
global instance_true
instance_true=True
global time_gone
# Define function execution times and intervals
functions_info = {}
global functions_in_call
functions_in_call=[]

# Define a generic function executor
def execute_function(func_name):
    global time_gone,functions_in_call
    
    """Generic function executor based on the function name."""
    # Fetch the duration for the specific function
    duration = functions_info[func_name]['duration']
    periodicity=functions_info[func_name]['interval']
    debt = 0 
    min_time=time_gone+duration
    for func,info in  functions_info.items():
        if func == func_name:
            continue

        # print(time_gone+duration,info['last_run']+info['interval'])
        if time_gone+duration>info['next_time']:  
            print("info time",info['next_time'])          
            min_time = min(min_time, info['next_time'])

            print(time_gone+duration-min_time)    
    print("runtime is",min_time)  
    runtime = min_time - time_gone
    
   
    print(time_gone)    
    if functions_info[func_name]['debt_time'] > 0 and functions_info[func_name]['debt_time'] < runtime:
        

        print("Running debt")
        log_function_info(func_name, 'started.', functions_info[func_name]['debt_time'],periodicity)
        time.sleep(functions_info[func_name]['debt_time'])
        
        time_gone+=functions_info[func_name]['debt_time']
        functions_info[func_name]['debt_time']=0
    else:
        
        
       
        min_run_time = 0.02  # 2 ms

        if runtime <= 0:
            print("Insufficient time to run the function; running for minimum time.")
            log_function_info(func_name, 'started.', min_run_time, periodicity)
            time.sleep(min_run_time)
            time_gone += min_run_time
        else:
            print("Function can run.")
            functions_info[func_name]['debt_time']=duration-runtime
            log_function_info(func_name, 'started.', runtime, periodicity)
            time.sleep(runtime)
            time_gone += runtime

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
global scheduled_functions
# Queue to manage the function execution order
execution_queue = SimpleQueue()
scheduled_functions = set()  # Set to keep track of scheduled functions

# List to collect log entries
log_entries = []




time_gone=0
global lcm
lcm=0
global identification
identification=1
def log_function_info(func_name, action, duration,periodicity):
    global time_gone, identification ,instance_true
    """Log the start and finish times of functions."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if action==("started."):
    
            log_entries.append({'ID':identification ,'Time Lapsed':time_gone ,'Duration': duration,'Function': func_name[-1],'Periodicity':periodicity})
            identification+=1
    print(f"{timestamp} - {func_name} {action} Duration: {duration} seconds")

def run_function(func_name):
    """Run the specified function."""
    with lock:
        functions_info[func_name]['last_run'] = time_gone
        # Run the function based on the map
        function_map[func_name]() # Execute the function



def scheduler():
    global instance_true
    """Scheduler that adds functions to the execution queue based on their intervals."""
    global time_gone, lcm
    scheduled_function = []
    while True:
        now = time_gone
        with lock:
            for func_name, info in functions_info.items():
                if now >= info['next_time']:
                    info['next_time'] = info['next_time'] + info['interval']
                    print("next time", func_name, info['next_time'])
                    first_instance.append(func_name)
                    scheduled_functions.add(func_name)
                    scheduled_function = (sorted(scheduled_functions, key=lambda x: functions_info[x]['next_time']))

                    # Trigger the event
                    execution_event.set()
            while not execution_queue.empty():
                execution_queue.get()
            # print("queue, should be empty", execution_queue.qsize())
            for func_name in scheduled_function:
                execution_queue.put(func_name)
            # print("should have something", execution_queue.qsize())

            # If no functions are ready, sleep for a short time and check again
            if time_gone < lcm:
                print(time_gone)
                time_gone = time_gone + 0.1
                time.sleep(0.1)  # Check every second
            else:
                break
        # Add a small delay before clearing the execution event
        time.sleep(0.1)
        execution_event.clear()

def worker():
    """Worker that processes functions from the execution queue."""
    while True:
        # Wait for the execution event to be set
        execution_event.wait()
        while execution_event.is_set():
            # Get a function from the queue
            func_name = execution_queue.get()
            # Execute the function
            run_function(func_name)
            # Remove the function from the set after execution
            with lock:
                print("removing", func_name)
                scheduled_functions.remove(func_name)
        # Clear the event after all functions have been executed
        execution_event.clear()
