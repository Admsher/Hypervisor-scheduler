import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        fig, ax = plt.subplots()
        
        # Plot Duration with Time on X-Axis
        ax.bar(range(num_partitions), durations, color='b', label='Duration')
        
        # Optionally, you can plot Periodicity on a secondary Y-axis if needed
        ax.set_xlabel('Time (Partitions)')
        ax.set_ylabel('Duration')
        ax.set_title('Schedule Bar Graph')
        ax.legend()
        
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
