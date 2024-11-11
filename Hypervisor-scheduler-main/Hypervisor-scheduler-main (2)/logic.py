import datetime
from threading import Thread, Lock, Event
from queue import SimpleQueue,PriorityQueue
import time
import pandas as pd
import math
import schedule
import numpy as np
import itertools


first_instance=[]
global instance_true
instance_true=True
global time_gone
functions_info = {}
global functions_in_call
functions_in_call=[]
global priorities
priorities=[]


def execute_function(func_name):
    global time_gone,functions_in_call
    
    """Generic function executor based on the function name."""

    duration = functions_info[func_name]['duration']
    periodicity=functions_info[func_name]['interval']
    min_time=time_gone+duration
    for func,info in  functions_info.items():
        if func == func_name:
            continue
        if (info['next_time']-info['interval'])*10 == np.floor(time_gone*10):
                index1 = int(func_name[-1]) - 1
                index2 = int(func[-1]) - 1
                if priorities[index1]>priorities[index2] and len(priorities)!=0:
                    return 
        if time_gone+duration>info['next_time']:    
                min_time = min(min_time, info['next_time'])
    runtime = duration-(time_gone+duration-min_time)
    
   
  
    if functions_info[func_name]['debt_time'] > 0 and functions_info[func_name]['debt_time'] < runtime:

        log_function_info(func_name, 'started.', functions_info[func_name]['debt_time'],periodicity)
        time.sleep(functions_info[func_name]['debt_time']/100)
        
        time_gone+=functions_info[func_name]['debt_time']
        functions_info[func_name]['debt_time']=0
    else:

        min_run_time = 1 

        if runtime <= 1:
            log_function_info(func_name, 'started.', min_run_time, periodicity)
            time.sleep(min_run_time/100)
       
        else:
            functions_info[func_name]['debt_time']=duration-runtime
            log_function_info(func_name, 'started.', runtime, periodicity)
            time.sleep(runtime/100)

function_map = {
    'func1': lambda: execute_function('func1'),
    'func2': lambda: execute_function('func2'),
    'func3': lambda: execute_function('func3'),
    'func4': lambda: execute_function('func4'),
}

lock = Lock()
execution_event = Event()
execution_event.set() 
global scheduled_functions
execution_queue = PriorityQueue()
scheduled_functions = set()  
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


def run_function(func_name):
    """Run the specified function."""
    with lock:
        functions_info[func_name]['last_run'] = time_gone
        function_map[func_name]() 
def scheduler():
    global time_gone
    """Scheduler that adds functions to the execution queue based on their intervals."""
    
    while True:
        now = time_gone
        with lock:
            for func_name, info in functions_info.items():
                if now >= info['next_time']:
                    info['next_time'] += info['interval']
                    execution_queue.put((info['next_time'], func_name))
                    execution_event.set()
     
        if time_gone < lcm:

            time.sleep(1/100)  
            time_gone += 0.1
        else:
            break

def worker():
    """Worker that processes functions from the execution queue."""
    
    while True:
       
        execution_event.wait()
        
        while not execution_queue.empty() :
       
            next_time, func_name = execution_queue.get()

            run_function(func_name)
            if time_gone<lcm:
                 break
        execution_event.clear()
