import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
import random
import logic  # Ensure this module is correctly set up
from threading import Thread
import time
import pandas as pd

# Global variables
functions_info = {}
function_map = {}
scheduler_started = False

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
            tk.Entry(frame_duration).grid(row=i, column=1, padx=10, pady=5)

            tk.Label(frame_periodicity, text=f"Periodicity for Partition {i+1}:").grid(row=i, column=0, padx=10, pady=5)
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

def create_schedule():
    global scheduler_started
    try:
        num_partitions = int(entry_num_partitions.get())
        major_frame = float(entry_major_frame.get())

        # Extract durations and periodicities
        durations = [float(entry.get()) for entry in frame_duration.winfo_children() if isinstance(entry, tk.Entry)]
        periodicities = [int(entry.get()) for entry in frame_periodicity.winfo_children() if isinstance(entry, tk.Entry)]

        # Ensure they match the number of partitions
        if len(durations) != num_partitions or len(periodicities) != num_partitions:
            raise ValueError("Mismatch in number of partitions.")

        # Check for valid periodicities
        if any(periodicity <= 0 for periodicity in periodicities):
            raise ValueError("All periodicities must be positive integers.")

        # Compute the LCM of periodicities
        periodicities_np = np.array(periodicities)
        lcm_periodicity = np.lcm.reduce(periodicities_np)

        if major_frame < lcm_periodicity:
            major_frame = lcm_periodicity

        # Create functions information
        for i in range(num_partitions):
            func_name = f'func{i + 1}'
            functions_info[func_name] = {
                'last_run': 0,
                'interval': periodicities[i],
                'duration': durations[i],
                'count': 0
            }
        
        for i in range(num_partitions):
            func_name = f'func{i + 1}'
            function_map[func_name] = lambda f=func_name: logic.execute_function(f)

        logic.functions_info = functions_info
        logic.function_map = function_map

        # Start the scheduler
        if not scheduler_started:
            scheduler_thread = Thread(target=logic.scheduler, daemon=True)
            worker_thread = Thread(target=logic.worker, daemon=True)
            scheduler_thread.start()
            worker_thread.start()
            scheduler_started = True

        # Run the main loop for the specified duration
        duration = max(major_frame, lcm_periodicity)
        start_time = time.time()
        while True:
            if logic.time_gone >= duration:
                break
        time.sleep(1)

        # Save logs to Excel
        df = pd.DataFrame(logic.log_entries)
        df.to_excel('function_logs.xlsx', index=False)
        print("Log data has been written to function_logs.xlsx")

        # Create the activity plot
        unique_functions = df["Function"].unique()
        colors = plt.cm.viridis(np.linspace(0, 1, len(unique_functions)))

        for i, function in enumerate(unique_functions):
            func_data = df[df['Function'] == function]
            end_times = func_data['Time Lapsed'] + func_data['Duration']

            # Use index to create a constant y-value for each function
            constant_y_value = i + 1

            # Ensure we use numpy arrays for end_times and Time Lapsed
            plt.hlines(constant_y_value, func_data['Time Lapsed'].values, end_times.values,
                       label=f'Function {function}', color=colors[i], linewidth=20)

        plt.xlabel('Time Lapsed')
        plt.ylabel('Function Activity')
        plt.title('Function Activity Over Time')
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

# Update scrollregion when widgets are added/removed
def on_frame_configure(event):
    canvas_main.configure(scrollregion=canvas_main.bbox("all"))

frame_content.bind("<Configure>", on_frame_configure)

# Run the tkinter main loop
root.mainloop()
