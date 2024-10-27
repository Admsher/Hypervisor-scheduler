import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random
import logic
from threading import Thread, Event
import time
import pandas as pd
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
import math
import itertools
from tkinter import StringVar
import log_exporter

functions_info = {}
function_map = {}
stop_event = Event()
scheduler_started = False
# Initialize zoom scale
zoom_scale = 1.0
global checkflag
checkflag=False
global offset_array
offset_array=[]


def find_offsets(A, N):
    min_A = min(A)
    offsets = []
    offset_vars = [chr(120 + i) for i in range(len(A))]  # create offset variables dynamically
    offset_ranges = [np.arange(-min_A, min_A, 1) for _ in offset_vars]  # use numpy arange for float ranges

    for offset_values in itertools.product(*offset_ranges):
        print(offset_values)
        sequences = []
        for a_i, offset in zip(A, offset_values):
            sequence = [a_i * j + offset for j in range(1, N+1)]
            sequences.append(sequence)
        union = set()
        for s in sequences:
            union |= set(s)
        if len(union) == sum(len(s) for s in sequences):
            offsets.append(offset_values)
    return offsets



def create_priority_dialog(partitions):
    # Create a new Tkinter window
    window = tk.Tk()
    window.title("Set Partition Priorities")

    # Create a label and a listbox to display the partitions
    label = tk.Label(window, text="Set priorities for the following partitions:")
    label.pack()
    listbox = tk.Listbox(window)
    for partition in partitions:
        listbox.insert(tk.END, partition)
    listbox.pack()

    # Create a frame to hold the priority entry fields
    frame = tk.Frame(window)
    frame.pack()

    # Create a priority entry field for each partition
    priority_entries = []
    for i, partition in enumerate(partitions):
        label = tk.Label(frame, text=f"{partition}:")
        label.grid(row=i, column=0)
        entry = tk.Entry(frame)
        entry.grid(row=i, column=1)
        priority_entries.append(entry)

    # Create a button to submit the priorities
    def submit_priorities():
        priorities = []
        for entry in priority_entries:
            priority = int(entry.get())
            priorities.append(priority)
        logic.priorities=priorities
        window.destroy()
        create_schedule()

    button = tk.Button(window, text="Submit", command=lambda: submit_priorities())
    button.pack()

    # Start the Tkinter event loop
    priorities = window.mainloop()
    create_schedule()


def update_fields():
    try:
        num_partitions = int(entry_num_partitions.get())
        if num_partitions <= 0:
            raise ValueError("Number of partitions must be positive.")

        # Clear existing fields
        for widget in frame_duration.winfo_children():
            widget.destroy()
        for widget in frame_periodicity.winfo_children():
            widget.destroy()

        # Clear and redraw the boxes on canvas
        canvas_boxes.delete("all")
        canvas_width = 300
        canvas_height = 50
        box_width = canvas_width / num_partitions
        for i in range(num_partitions):
            x0 = i * box_width
            x1 = x0 + box_width
            y0 = 10
            y1 = canvas_height - 10
            canvas_boxes.create_rectangle(x0, y0, x1, y1, outline="black", fill="lightblue")

        # Create new fields
        for i in range(num_partitions):
            tk.Label(frame_duration, text=f"Duration for Partition {i+1}:").grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(frame_duration, width=10, insertwidth=10)
            entry.insert(0, "1")
            entry.grid(row=i, column=1, padx=10, pady=5)
            # tk.Entry(frame_duration,default="1").grid(row=i, column=1, padx=10, pady=5)

            tk.Label(frame_periodicity, text=f"Periodicity for Partition {i+1} (in ms):").grid(row=i, column=0, padx=10, pady=5)
            tk.Entry(frame_periodicity).grid(row=i, column=1, padx=10, pady=5)

        # Add Major Frame entry after updating fields
        if not major_frame_label.winfo_ismapped():
            major_frame_label.grid(row=num_partitions + 3, column=0, padx=10, pady=10)
            entry_major_frame.grid(row=num_partitions + 3, column=1, padx=10, pady=10)

        # Adjust layout
        root.update_idletasks()
        canvas_main.configure(scrollregion=canvas_main.bbox("all"))

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid positive integer for the number of partitions.")
        
        
def checkclash(peridicity_array,major_frame)->bool:
    i =0
    j= len(peridicity_array)-1
    while i<j:
        lcm=math.lcm(int(peridicity_array[i]),int(peridicity_array[j]))
        if lcm<major_frame:
            return True
        i+=1
        j-=1
    return False
        
        

def create_schedule():
    global zoom_scale, bars,priorities,checkflag
    try:
        num_partitions = int(entry_num_partitions.get())
        major_frame = float(entry_major_frame.get())
       
        durations = [float(entry.get()) for entry in frame_duration.winfo_children() if isinstance(entry, tk.Entry)]
      
        periodicities = [float(entry.get()) for entry in frame_periodicity.winfo_children() if isinstance(entry, tk.Entry)]

        if len(durations) != num_partitions or len(periodicities) != num_partitions:
            raise ValueError("Mismatch in number of partitions.")

        # Compute the LCM of periodicities, ensuring they are non-zero
        periodicities_int = [int(p) for p in periodicities if p > 0]
        if not periodicities_int:
            raise ValueError("All periodicities must be greater than zero.")
        
        lcm_periodicity = np.lcm.reduce(np.array(periodicities_int))
        if checkclash(periodicities,lcm_periodicity) and not checkflag :
            max_iter=int(lcm_periodicity/min(periodicities))
            offset_array= find_offsets(periodicities,max_iter)
            if offset_array is not None:
                print("Offset feasible")
            else:
                checkflag=True
                messagebox.showwarning("Clash Detetcted", "Some partitions are clashing, give priority to each partition manually.")
                partitions = []
                print(num_partitions)
                for i in range(num_partitions):
                        partitions.append(f"Parition {i+1}")
                        print(partitions)
                create_priority_dialog(partitions)

        if major_frame <= lcm_periodicity:
            if lcm_periodicity==max(periodicities_int):
                major_frame = lcm_periodicity + max(durations)
            else:
                major_frame=major_frame

        # print(major_frame)

        logic.lcm = major_frame

        # Create a new window for the plot
        temp_val = 0
        try:
            for i in range(num_partitions):
                func_name = f'func{i + 1}'
                functions_info[func_name] = {
                    'last_run': 0,
                    'interval': periodicities[i],
                    'duration': durations[i],
                    'count': 0,
                    'debt_time':0,
                    'next_time':periodicities[i]+offset_array[-2][i]
                }
        except UnboundLocalError:
            for i in range(num_partitions):
                func_name = f'func{i + 1}'
                functions_info[func_name] = {
                    'last_run': 0,
                    'interval': periodicities[i],
                    'duration': durations[i],
                    'count': 0,
                    'debt_time':0,
                    'next_time':periodicities[i]
                }
        
        
        for i in range(num_partitions):
                func_name = f'func{i + 1}'
                function_map[func_name] = lambda f=func_name: logic.execute_function(f)
        
        logic.functions_info = dict(sorted(functions_info.items(), key=lambda item: item[1]['interval']))
        logic.function_map = function_map
        

        # Start the scheduler
        global scheduler_started
        scheduler_thread = Thread(target=logic.scheduler, daemon=True)
        worker_thread = Thread(target=logic.worker, daemon=True)
        if not scheduler_started:
            scheduler_thread.start()
            worker_thread.start()
            scheduler_started = True

        # Run the main loop for the calculated duration
        duration = max(lcm_periodicity, major_frame)
        # start_time = time.time()
        while True:

            if logic.time_gone >= duration:
                break
        time.sleep(1)

        # Save logs to Excel
        df = pd.DataFrame(logic.log_entries)
        df.to_excel('function_logs.xlsx', index=False)
        print("Log data has been written to function_logs.xlsx")
        min_durations = df.groupby('Function')['Duration'].min()
        min_durations.to_csv('output.txt', sep='\t', header=True)

        # Create the 3D Bar graph
        unique_functions = df["Function"].unique()
        colors = plt.cm.viridis(np.linspace(0, 1, len(unique_functions)))

        for i, function in enumerate(unique_functions):
            func_data = df[df['Function'] == function]
            end_times = func_data['Time Lapsed'] + func_data['Duration']
            constant_y_value = 0
            y_values = np.full_like(func_data['Time Lapsed'].values, constant_y_value)
             # Constant y value for display
            plt.hlines(y_values, func_data['Time Lapsed'].values, end_times.values,
                       label=f'Partition {function}', color=colors[i], linewidth=20)

        plt.xlabel('Time Lapsed')
        plt.ylabel('Function Activity')
        plt.title('Partition Activity Over Time')
        plt.legend()
        plt.show()

    except ValueError as e:
        messagebox.showerror("Invalid Input", f"Error: {e}")


# Create main window
root = tk.Tk()
root.title("Dynamic Partition Parameters")
root.geometry("800x500")

# Create a frame for the canvas and scrollbar
frame_main = tk.Frame(root)
frame_main.pack(fill=tk.BOTH, expand=True)

# Create a canvas widget
canvas_main = tk.Canvas(frame_main)
canvas_main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a vertical scrollbar linked to the canvas
scrollbar_y = tk.Scrollbar(frame_main, orient=tk.VERTICAL, command=canvas_main.yview)
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

# Create a frame inside the canvas to hold the widgets
frame_content = tk.Frame(canvas_main)
canvas_main.create_window((0, 0), window=frame_content, anchor="nw")

# Configure the scrollbar
canvas_main.configure(yscrollcommand=scrollbar_y.set)

# Number of partitions label and entry
label_num_partitions = tk.Label(frame_content, text="Number of Partitions:")
label_num_partitions.grid(row=0, column=0, padx=10, pady=10)
entry_num_partitions = tk.Entry(frame_content)
entry_num_partitions.grid(row=0, column=1, padx=10, pady=10)

# Major Frame label and entry
major_frame_label = tk.Label(frame_content, text="Major Frame:")
entry_major_frame = tk.Entry(frame_content)

# Canvas to draw boxes
canvas_boxes = tk.Canvas(frame_content, width=300, height=50, bg="white")
canvas_boxes.grid(row=0, column=2, rowspan=5, padx=10, pady=10)

# Update button
button_update = tk.Button(frame_content, text="Update Fields", command=update_fields)
button_update.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Duration fields frame
frame_duration = tk.Frame(frame_content)
frame_duration.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
tk.Label(frame_duration, text="Duration for each Partition:").grid(row=0, column=0, padx=10, pady=5)

# Periodicity fields frame
frame_periodicity = tk.Frame(frame_content)
frame_periodicity.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
tk.Label(frame_periodicity, text="Periodicity:").grid(row=0, column=0, padx=10, pady=5)

# Create Schedule button
button_create_schedule = tk.Button(frame_content, text="Create Schedule", command=create_schedule)
button_create_schedule.grid(row=10, columnspan=2, padx=10, pady=10)

label_format = tk.Label(frame_content, text="Select Format for Conversion:")
label_format.grid(row=11, column=0, padx=10, pady=10)

format_var = StringVar(value="Select Format")
format_options = ["VxWorks", "PikeOS"]
dropdown_format = tk.OptionMenu(frame_content, format_var, *format_options)
dropdown_format.grid(row=11, column=1, padx=10, pady=10)

# Convert to CSV
button_convert_csv = tk.Button(frame_content, text="Output XML", command=lambda: log_exporter.convert_to_csv(format_var))
button_convert_csv.grid(row=12, columnspan=2, padx=10, pady=5)

# Convert to XML
# button_convert_xml = tk.Button(frame_content, text="Convert to XML", command=log_exporter.convert_to_xml)
# button_convert_xml.grid(row=13, columnspan=2, padx=10, pady=5)

# # Convert to VxWorks XML
# button_convert_vxworks_xml = tk.Button(frame_content, text="Convert to VxWorks XML", command=log_exporter.convert_to_vxworks_xml)
# button_convert_vxworks_xml.grid(row=14, columnspan=2, padx=10, pady=5)

# Update scrollregion when widgets are added/removed
def on_frame_configure(event):
    canvas_main.configure(scrollregion=canvas_main.bbox("all"))

frame_content.bind("<Configure>", on_frame_configure)

# Run the tkinter main loop
root.mainloop()
