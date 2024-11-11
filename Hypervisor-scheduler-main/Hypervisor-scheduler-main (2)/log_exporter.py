import pandas as pd
import xml.etree.ElementTree as ET
from tkinter import messagebox
import logic
import numpy as np
def convert_to_csv(format_var):
    selected_format = format_var.get()
    if selected_format == "VxWorks":
        filename = 'function_logs_vxworks.csv'
    elif selected_format == "PikeOS":
        filename = 'function_logs_pikeos.csv'
    else:
        messagebox.showwarning("Select Format", "Please select a format to convert.")
        return

    df = pd.DataFrame(logic.log_entries)
    
    if not df.empty:
        if selected_format == "VxWorks":
            convert_to_vxworks_xml()
        elif selected_format == "PikeOS":
            convert_to_xml()
        messagebox.showinfo("Success", f"Log data has been written to {filename}")
    else:
        messagebox.showwarning("No Data", "No log data available to convert.")

def convert_to_xml():
    df = pd.DataFrame(logic.log_entries)
    if df.empty:
        messagebox.showwarning("No Data", "No log data available to convert.")
        return

    # Create the root element
    schedule_scheme = ET.Element("ScheduleScheme", Name="SCHED_BOOT")
    window_table = ET.SubElement(schedule_scheme, "WindowTable")

    for index, row in df.iterrows():
        window = ET.SubElement(window_table, "Window")
        window.set("Identifier", str(index + 1))  
        window.set("Start", str(int(row['Time Lapsed']*1000000))) 
        window.set("Duration", str(row['Duration']*1000000))  
        window.set("TimePartitionID", str(row['Function']))  
        window.set("Flags", "VM_SCF_PERIOD")  

    filename = 'function_logs_pikeos.xml'
    with open(filename, 'wb') as f:
        f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')  
        f.write(ET.tostring(schedule_scheme, encoding='utf-8', xml_declaration=False))

    with open(filename, 'r+', encoding='utf-8') as f:
        content = f.read()
        content = content.replace('><', '>\n<')
        f.seek(0)
        f.write(content)
        f.truncate()
        
    messagebox.showinfo("Success", f"Log data has been written to {filename}")

def convert_to_vxworks_xml():
    df = pd.DataFrame(logic.log_entries)
    if df.empty:
        messagebox.showwarning("No Data", "No log data available to convert.")
        return

    schedule = ET.Element("Schedule", Name="init")

    for index, row in df.iterrows():
        window = ET.SubElement(schedule, "Window")
        window.set("PartitionNameRef", str(row['Function']))
        window.set("Duration", str(np.ceil(row['Duration'] * 1000000)))
        window.set("Offset", str(np.ceil(int(row['Time Lapsed'] * 1000000) / 10000) * 10000))  # Round the Offset value
        window.set("PeriodicProcessingStart", "true")

    filename = 'function_logs_vxworks.xml'
    with open(filename, 'wb') as f:
        f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
        f.write(ET.tostring(schedule, encoding='utf-8', xml_declaration=False))

    with open(filename, 'r+', encoding='utf-8') as f:
        content = f.read()
        content = content.replace('><', '>\n<')
        f.seek(0)
        f.write(content)
        f.truncate()

    messagebox.showinfo("Success", f"Log data has been written to {filename}")
