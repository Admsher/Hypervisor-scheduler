import datetime
from threading import Thread, Lock, Event
from queue import SimpleQueue,PriorityQueue
import time
import pandas as pd
import math
import schedule
import numpy as np
first_instance=[]
global instance_true
instance_true=True
global time_gone
# Define function execution times and intervals
functions_info = {}
global functions_in_call
functions_in_call=[]
global priorities
priorities=[]

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
            print("ignoring")
            continue
        print(time_gone,func,info['next_time'])
        print()
        if info['next_time'] == np.floor(time_gone):
                if priorities[int(func_name[-1])-1]<priorities[int(func[-1])-1]:
                    print(f"Ignoring {func_name} due to lower priorirty")
                    return 
        if time_gone+duration>info['next_time']:    
                print(f"{func_name} interfering with {func} reducing time")     
                min_time = min(min_time, info['next_time'])

    print(f"runtime is for {func_name} is",min_time-time_gone)  
    runtime = min_time - time_gone
    
   
    # print(time_gone)    
    if functions_info[func_name]['debt_time'] > 0 and functions_info[func_name]['debt_time'] < runtime:
        

        # print("Running debt")
        log_function_info(func_name, 'started.', functions_info[func_name]['debt_time'],periodicity)
        time.sleep(functions_info[func_name]['debt_time'])
        
        time_gone+=functions_info[func_name]['debt_time']
        functions_info[func_name]['debt_time']=0
    else:
        
        
       
        min_run_time = 0.02  # 2 ms

        if runtime <= 0:
            # print("Insufficient time to run the function; running for minimum time.")
            log_function_info(func_name, 'started.', min_run_time, periodicity)
            time.sleep(min_run_time)
            # time_gone += min_run_time
        else:
            # print("Function can run.")
            functions_info[func_name]['debt_time']=duration-runtime
            log_function_info(func_name, 'started.', runtime, periodicity)
            time.sleep(runtime)
            # time_gone += runtime

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
execution_queue = PriorityQueue()
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
    
            log_entries.append({'ID':identification ,'Time Lapsed':time_gone ,'Duration': duration,'Function': func_name[-1],'Periodicity':periodicity,'Next_time':functions_info[func_name]['next_time']})
            identification+=1
    # print(f"{timestamp} - {func_name} {action} Duration: {duration} seconds")

def run_function(func_name):
    """Run the specified function."""
    with lock:
        functions_info[func_name]['last_run'] = time_gone
        # Run the function based on the map
        function_map[func_name]() # Execute the function

def scheduler():
    global time_gone
    """Scheduler that adds functions to the execution queue based on their intervals."""
    
    while True:
        now = time_gone
        with lock:
            for func_name, info in functions_info.items():
                if now >= info['next_time']:
                    print(f"Scheduling: {func_name}")
                    # Update the next execution time
                    info['next_time'] += info['interval']
                    # Add to priority queue
                    execution_queue.put((info['next_time'], func_name))
                    execution_event.set()
                    
        # Wait for the execution event to be set
        if time_gone < lcm:
            time.sleep(0.01)  # Check every 10ms
            time_gone += 0.01
        else:
            break

def worker():
    """Worker that processes functions from the execution queue."""
    
    while True:
        # Wait for the execution event to be set
        execution_event.wait()
        
        while not execution_queue.empty():
            # Get the function from the queue
            next_time, func_name = execution_queue.get()
            print(f"Executing: {func_name} at time {time_gone} when next time was {functions_info[func_name]['next_time']-functions_info[func_name]['interval']}")
            
            # Execute the function
            run_function(func_name)

        # Clear the event after all functions have been executed
        execution_event.clear()
