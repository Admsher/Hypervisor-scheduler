import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random
import logic
from threading import Thread, Lock, Event
import time
import pandas as pd
import matplotlib.patches as mpatches

functions_info={}
function_map={}
stop_event = Event()

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
            
        # Adjust layout
        root.update_idletasks()
        root.geometry(f"500x{200 + 50*num_partitions}")

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid positive integer for the number of partitions.")

def submit():
    try:
        num_partitions = int(entry_num_partitions.get())
        durations = [float(entry.get()) for entry in frame_duration.winfo_children() if isinstance(entry, tk.Entry)]
        periodicities = [float(entry.get()) for entry in frame_periodicity.winfo_children() if isinstance(entry, tk.Entry)]

        if len(durations) != num_partitions or len(periodicities) != num_partitions:
            raise ValueError("Mismatch in number of partitions.")

        # Process input values
        messagebox.showinfo("Input Values", f"Number of partitions: {num_partitions}\n"
                                            f"Durations: {', '.join(map(str, durations))}\n"
                                            f"Periodicities: {', '.join(map(str, periodicities))}")
    except ValueError as e:
        messagebox.showerror("Invalid Input", f"Error: {e}")

def create_schedule():
    try:
        num_partitions = int(entry_num_partitions.get())
        durations = [float(entry.get()) for entry in frame_duration.winfo_children() if isinstance(entry, tk.Entry)]
        periodicities = [float(entry.get()) for entry in frame_periodicity.winfo_children() if isinstance(entry, tk.Entry)]

        if len(durations) != num_partitions or len(periodicities) != num_partitions:
            raise ValueError("Mismatch in number of partitions.")
        
        # Create a new window for the plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        temp_val=0
        for i in range(num_partitions):
            func_name = f'func{i + 1}'  # Create function names like 'func1', 'func2', etc.
            functions_info[func_name] = {
                'last_run': 0,  # Assuming last_run is initialized to 0
                'interval': periodicities[i],  # Periodicity from UI
                'duration': durations[i]       # Duration from UI
            }
        for i in range(num_partitions):
            func_name = f'func{i + 1}'  # Create function names like 'func1', 'func2', etc.
            function_map[func_name] = lambda f=func_name: logic.execute_function(f)  
        
        logic.functions_info=functions_info
        logic.function_map= function_map
        
        # Start the scheduler
        global scheduler_started
        scheduler_thread = Thread(target=logic.scheduler, daemon=True)
        worker_thread = Thread(target=logic.worker, daemon=True)
        if not scheduler_started:
            scheduler_thread.start()
            worker_thread.start()
        # Start the scheduler and worker threads only once
            
            scheduler_started = True

      
    # Run the main loop for 2 minutes
        start_time = time.time()
        duration = 10  # 2 minutes
        

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= duration:
                break
        time.sleep(1)
        

    # Save logs to Excel
        df = pd.DataFrame(logic.log_entries)
        df.to_excel('function_logs.xlsx', index=False)
        

        print("Log data has been written to function_logs.xlsx")
      
        
        
        duration_final=[]
        durations=[]
        for i in df["Duration"]:
            duration_final.append(temp_val)
            durations.append(i)
            temp_val=temp_val+i

            
            # print(duration_final[i])
        # Create the 3D Bar graph
        xpos = np.array(duration_final)            # X-axis representing durations                   # X-axis representing durations
        ypos = np.ones(len(duration_final))      # Y-axis values set to 1
        zpos = np.zeros(len(duration_final))     # Z starting positions
        unique_functions = df["Function"].unique()
        function_color_map = {function: (random.random(), random.random(), random.random()) for function in unique_functions}
        colors = [function_color_map[function] for function in df["Function"]]
        # colors = [(random.random(), random.random(), random.random()) for _ in range(len(duration_final))]
        dx = np.array(durations)         # Bar width
        dy = np.ones(len(duration_final))        # Bar depth
        dz = np.ones(len(duration_final))        # Bar heights fixed at 1 for simplicity

        # Plot the 3D bars
        ax.bar3d(xpos, ypos, zpos, dx, dy, dz, zsort='average',color=colors)

        ax.set_xlabel('Time (X-axis)')
        ax.set_ylabel('Y (Fixed at 1)')
        ax.set_zlabel('Z (Fixed at 1)')
        ax.set_title('3D Schedule Bar Graph')
        legend_patches = [mpatches.Patch(color=function_color_map[function], label=function) for function in unique_functions]

        # Add the legend to the plot
        ax.legend(handles=legend_patches, loc='upper right', title="Functions")

        # Embed the plot in a Tkinter window
        plot_window = tk.Toplevel(root)
        plot_window.title("Schedule Graph")
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    except ValueError as e:
        messagebox.showerror("Invalid Input", f"Error: {e}")

# Create main window
root = tk.Tk()
root.title("Dynamic Partition Parameters")

# Number of partitions label and entry
label_num_partitions = tk.Label(root, text="Number of Partitions:")
label_num_partitions.grid(row=0, column=0, padx=10, pady=10)
entry_num_partitions = tk.Entry(root)
entry_num_partitions.grid(row=0, column=1, padx=10, pady=10)

# Canvas to draw boxes
canvas_boxes = tk.Canvas(root, width=300, height=50, bg="white")
canvas_boxes.grid(row=0, column=2, rowspan=5, padx=10, pady=10)

# Update button
button_update = tk.Button(root, text="Update Fields", command=update_fields)
button_update.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Duration fields frame
frame_duration = tk.Frame(root)
frame_duration.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
tk.Label(frame_duration, text="Duration for each Partition:").grid(row=0, column=0, padx=10, pady=5)

# Periodicity fields frame
frame_periodicity = tk.Frame(root)
frame_periodicity.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
tk.Label(frame_periodicity, text="Periodicity:").grid(row=0, column=0, padx=10, pady=5)

# Submit button
button_submit = tk.Button(root, text="Submit", command=submit)
button_submit.grid(row=4, columnspan=2, padx=10, pady=20)

# Create Schedule button
button_create_schedule = tk.Button(root, text="Create Schedule", command=create_schedule)
button_create_schedule.grid(row=5, columnspan=2, padx=10, pady=10)

# Run the tkinter main loop
root.mainloop()
