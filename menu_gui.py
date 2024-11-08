# Import necessary libraries
import tkinter as tk 
from tkinter import filedialog, messagebox, ttk, Menu, simpledialog ,font
import pygame 
import os 
import threading
import time
import io
import zipfile
import json
from tkinter import ttk
import shutil
import copy
import platform
import sys
from PIL import Image, ImageTk 


# Global variables
ingredient_data = None  # Data for the ingredients table
instruction_data = None  # Data for the instructions table
data = None
selected_ingredient_row = None  # Store selected row in ingredients
selected_instruction_row = None  # Store selected row in instructions

highlight_color = "yellow"  # Color for highlighting the selected row
default_color = "white"  # Default background color


copied_ingredient_row = None  # Store copied ingredient row
copied_instruction_row = None  # Store copied instruction row
ERROR_COLOR = "red"
NORMAL_COLOR = "white"

# Initialize pygame mixer for audio playback
pygame.mixer.init()


def get_base_path():
    # When running as exe, sys.executable gives the exe path
    # When running as script, __file__ gives the script path
    if getattr(sys, 'frozen', False):
        # Running as exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
    return base_path

# Set up directory paths
BASE_DIR = get_base_path()
AUDIO_FOLDER_PATH = os.path.join(BASE_DIR, "mp3")
SELECT_FOLDER_PATHS = os.path.join(BASE_DIR, "Recipee's", "Aloo Samosa")
Image_folder_path = os.path.join(BASE_DIR,"jpg")


global error_cells
error_cells = []

# Function to change the color of a specific cell
def change_cell_color(row, col, frame, color):
    for widget in frame.grid_slaves(row=row, column=col):
        if isinstance(widget, tk.Frame):
            for label in widget.winfo_children():
                if isinstance(label, tk.Label):
                    if color:
                        label.config(bg=color)
                    else:
                        # Reset to default color and style
                        label.config(bg=default_color, font=('Arial', 10, 'underline'))

# Function to play audio file
def play_audio(file_name, row, col, frame):
    audio_file = os.path.join(AUDIO_FOLDER_PATH, file_name)

    if os.path.exists(audio_file):
        # Change cell color to light green
        change_cell_color(row, col, frame, "light green")

        def play_and_reset():
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            # Reset cell color after audio finishes
            root.after(0, lambda: change_cell_color(row, col, frame, None))

        # Start audio playback in a separate thread
        threading.Thread(target=play_and_reset, daemon=True).start()

# Function to handle left-click on the audioP column (column index 5)
def on_audio_click(row, col):
    audio_value = ingredient_data[row][col]
    if audio_value:
        audio_file_name = f"{audio_value}.mp3"
        play_audio(audio_file_name, row, col, ingredients_frame)

# Function to handle left-click on instruction audio columns
def on_instruction_audio_click(row, col):
    audio_value = instruction_data[row][col]
    if audio_value:
        audio_file_name = f"{audio_value}.mp3"
        play_audio(audio_file_name, row, col, instructions_frame)

# Function to check if an audio file exists
def audio_file_exists(file_name):
    audio_path = os.path.join(AUDIO_FOLDER_PATH, f"{file_name}.mp3")
    return os.path.exists(audio_path)

# Function to handle missing audio files
def handle_missing_audio(file_name):
    audio_path = os.path.join(AUDIO_FOLDER_PATH, f"{file_name}.mp3")
    if not os.path.exists(audio_path):
        response = messagebox.askquestion("Audio File Not Found", 
                                          f"The audio file '{file_name}.mp3' was not found. Would you like to add it?")
        if response == 'yes':
            file_path = filedialog.askopenfilename(
                title="Select Audio File",
                filetypes=[("MP3 files", "*.mp3")]
            )
            if file_path:
                try:
                    # Ensure the AUDIO_FOLDER_PATH exists
                    os.makedirs(AUDIO_FOLDER_PATH, exist_ok=True)
                    # Copy the selected file to the AUDIO_FOLDER_PATH
                    shutil.copy2(file_path, audio_path)
                    messagebox.showinfo("Success", f"Audio file '{file_name}.mp3' has been added successfully.")
                    return True
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred while copying the file: {str(e)}")
    return False
def handle_image_upload(file_name):
    # Create the path with a .png extension for saving in the folder
    image_path = os.path.join(Image_folder_path, f"{file_name}.png")

    # Check if the image with this file name already exists as a .png
    if os.path.exists(image_path):
        return True  # Image already exists, no need to upload

    # Prompt the user to select an image file
    file_path = filedialog.askopenfilename(
        title="Select Image File",
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.tiff;*.tif;*.webp;*.svg;*.heic;*.heif;*.raw;*.cr2;*.nef;*.orf;*.sr2;*.psd;*.ai;*.eps;*.ico;*.jfif")]
    )

    if file_path:
        try:
            # Ensure the Image_folder_path exists
            os.makedirs(Image_folder_path, exist_ok=True)

            # Open the selected file and convert to PNG format
            with Image.open(file_path) as img:
                # Convert image to RGB mode if it's in a different mode (like CMYK or RGBA)
                img = img.convert("RGB")
                # Save as .png in the target folder
                img.save(image_path, "PNG")

            messagebox.showinfo("Success", f"Image file '{file_name}.png' has been added successfully.")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the file: {str(e)}")
    return False  # Return False if no file was selected or an error occurred
def show_image_popup(event, value, root):
    if not value:  # If cell is empty
        return

    # Check for .jpg and .png file extensions
    image_path_jpg = os.path.join(Image_folder_path, f"{value}.jpg")
    image_path_png = os.path.join(Image_folder_path, f"{value}.png")

    # Determine the correct file path
    if os.path.exists(image_path_jpg):
        image_path = image_path_jpg
    elif os.path.exists(image_path_png):
        image_path = image_path_png
    else:
        return  # No image found, exit the function

    try:
        # Create popup window
        popup = tk.Toplevel(root)
        popup.overrideredirect(True)  # Remove window decorations

        # Position popup to the left of the cursor
        x = root.winfo_pointerx() - 210  # Adjusted to appear to the left
        y = root.winfo_pointery() + 10
        popup.geometry(f"+{x}+{y}")

        # Load and resize image to 200x200
        image = Image.open(image_path)
        image = image.resize((300, 300), Image.Resampling.LANCZOS)

        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image)

        # Create label with image
        label = tk.Label(popup, image=photo)
        label.image = photo  # Keep a reference to avoid garbage collection
        label.pack()

        # Function to destroy popup
        def destroy_popup(event=None):
            popup.destroy()

        # Bind the popup destruction to the mouse leave events
        popup.bind('<Leave>', destroy_popup)
        event.widget.bind('<Leave>', destroy_popup)

        # Optional: Bind popup to the widget to keep it accessible
        event.widget._popup = popup

    except Exception as e:
        print(f"Error showing image: {e}")
        if 'popup' in locals():
            popup.destroy()

def display_ingredients_table(data):
    highlight_color = "yellow"  # Define highlight color
    default_color = "white"     # Define default color
    
    for i, row in enumerate(data):
        for j, value in enumerate(row):
            cell = tk.Frame(ingredients_frame, relief="solid", borderwidth=1)
            cell.grid(row=i, column=j, sticky="nsew", padx=1, pady=1)
            
            # Set background color based on selection and conditions
            bg_color = highlight_color if i == selected_ingredient_row else default_color
            if i == 0:  # If it's header row
                bg_color = "light grey"
            if i > 0 and j in [4, 5, 6, 7] and value and not audio_file_exists(value):
                bg_color = "red"
            
            underline = (j in [4, 5, 6, 7] and i > 0)
            
            label = tk.Label(cell, text=str(value), font=('Arial', 10, 'underline' if underline else ''),
                             bg=bg_color, anchor='center')
            label.pack(side='left', fill='both', expand=True)

            if i > 0:  # Skip header row
                label.bind("<Double-1>", lambda event, r=i, c=j: edit_cell(r, c, ingredient_data, ingredients_frame))
                label.bind("<Button-3>", lambda event, r=i, f=ingredients_frame: show_context_menu(event, r, f))

            if j in [4, 5, 6, 7]:  # Audio columns
                label.bind("<Button-1>", lambda event, r=i, c=j: on_audio_click(r, c))
                
            # Add image hover for image column (column 8)
            if j == 8 and i > 0:  # Image column
                label.bind("<Enter>", lambda event, v=value: show_image_popup(event, v, ingredients_frame.winfo_toplevel()))

    for j in range(len(data[0])):
        ingredients_frame.grid_columnconfigure(j, weight=1)
  
def is_valid_stirrer_value(value):
    if value == "" or value.strip() == "":  # Allow blank or empty string values
        return True
    try:
        int_value = int(value)
        return 0 <= int_value <= 4
    except ValueError:
        return False
def check_stirrer_errors():
    errors = []
    for i, row in enumerate(instruction_data[1:], start=1):  # Skip header
        stirrer_value = row[10]  # Assuming stirrer is at index 10
        if not is_valid_stirrer_value(stirrer_value):
            errors.append(f"Invalid stirrer value '{stirrer_value}' in step {i}")
    
def is_valid_magnetron_value(value):
    if value == "" or value.strip() == "":  # Allow blank or empty string values
        return True
    try:
        int_value = int(value)
        return int_value in [0, 20, 40, 60, 80, 100]  # Magnetron valid values
    except ValueError:
        return False    

def check_for_errors(data_table, frame):
    error_cells = []
    for i, row in enumerate(data_table):
        if i == 0:  # Skip header row
            continue
        for j, value in enumerate(row):
            is_error = False
            if frame == instructions_frame:
                if j == 10:  # Stirrer column
                    if str(value).strip() not in ["0", "1", "2", "3", "4", ""]:
                        is_error = True
                elif j == 20:  # Skip column
                    if str(value).strip().lower() not in ["true", "false", ""]:
                        is_error = True
                elif j == 7:  # Lid status column
                    if str(value).strip().lower() not in ["open", "close", ""]:
                        is_error = True
                elif j == 3:  # Induction power column
                    if str(value).strip() not in ["0", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100", ""]:
                        is_error = True
                elif j == 12:  # Magnetron power column
                    if str(value).strip() not in ["0", "20", "40", "60", "80", "100", ""]:
                        is_error = True

            if is_error:
                error_cells.append((i, j))
    return error_cells
    

# Function to load JSON file and display both tables
def load_json():
    global ingredient_data, instruction_data  # Declare ingredient_data and instruction_data as global
    
    # Open file dialog to select JSON file
    file_path = filedialog.askopenfilename(filetypes=[("All Supported Files", "*.json;*.txt;*.zip")])
    
    if not file_path:
        return
    
    try:
        if file_path.lower().endswith('.zip'):
            # Handle ZIP file
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                json_files = [f for f in zip_ref.namelist() if f.lower().endswith('.txt')]
                if not json_files:
                    raise ValueError("No JSON file found in the ZIP archive")
                
                # Use the first JSON file found
                json_file = json_files[0]
                with zip_ref.open(json_file) as file:
                    data = json.load(io.TextIOWrapper(file))
        else:
            # Handle regular JSON file
            with open(file_path, 'r') as file:
                data = json.load(file)


        # Set recipe name at the heading
        recipe_name = data.get("name", ["Unknown Recipe"])[0]
        title_label.config(text=f"Recipe: {recipe_name}")
        
        # Extract ingredient and instruction data for the tables
        ingredient_data = format_ingredients(data)
        instruction_data = format_instructions(data)
        
        # Clear the existing table frames before adding new data
        clear_table(ingredients_frame)
        clear_table(instructions_frame)
        
        # Display the data in both tables
        display_ingredients_table(ingredient_data)
        display_instructions_table(instruction_data)
        # check_audio_files()
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to format the ingredients data into a table-like format
def format_ingredients(data):
    rows = []
    ingredients = data.get("Ingredients", [])
    
    # Column names: Name, Weight, and Action
    column_names = ['Name', 'Weight', 'Action','audio','audioI','audioP','audioQ','audioU','Image','Text']
    
    # Loop through the ingredients and extract the relevant fields
    for ingredient in ingredients:
        name = ingredient.get("title", "")
        weight = ingredient.get("weight", "")
        action = ingredient.get("app_audio", "")
        audio = ingredient.get("audio", "")
        audioI = ingredient.get("audioI", "")
        audioP = ingredient.get("audioP", "")
        audioQ = ingredient.get("audioQ", "")
        audioU = ingredient.get("audioU", "")
        Image = ingredient.get("image","")
        Text = ingredient.get("text","")
        rows.append([name, weight, action,audio,audioI,audioP,audioQ,audioU,Image,Text])
    
    # Include headers in the first row
    return [column_names] + rows

# Function to format the instructions data into a table-like format
def format_instructions(data):
    rows = []
    instructions = data.get("Instruction", [])
    
    # Column names for the instruction table
    column_names = ['Step', 'Procedure', 'Induction On Time', 'Induction Power', 
                    'Text', 'Weight', 'Duration (s)', 'Lid Status', 
                    'Wait Time (s)', 'Warm Time (s)', 'Stirrer', 
                    'Mag On Time', 'Mag Power', 'Action', 'Mag Serv', 'Pump','AudioI','AudioP','AudioQ','AudioU','skip','Ind_lid_con', 'threshold', 'Purge on', 'Image']
    
    # Loop through the instructions and format the data
    for i, instruction in enumerate(instructions):
        step = f"Step {i + 1}"
        procedure = instruction.get("Audio", "")  # Fetch 'audio' as 'procedure'
        ind_lid_con = instruction.get("Indtime_lid_con","")
        ind_on_time = instruction.get("Induction_on_time", 0)
        ind_power = instruction.get("Induction_power", 0)
        mag_on_time = instruction.get("Magnetron_on_time", 0)
        mag_power = instruction.get("Magnetron_power", 0)
        text = instruction.get("Text", "")
        weight = instruction.get("Weight", "")
        duration = instruction.get("durationInSec", 0)
        lid_status = instruction.get("lid", "N/A")
        wait_time = instruction.get("wait_time", 0)
        warm_time = instruction.get("warm_time", 0)
        stirrer = instruction.get("stirrer_on", 0)
        action = instruction.get("app_audio", 0)
        mag_serv = instruction.get("mag_severity")
        pump = instruction.get("pump_on", 0)
        AudioI = instruction.get("audioI",0)
        AudioP = instruction.get("audioP",0)
        AudioQ = instruction.get("audioQ",0)
        AudioU = instruction.get("audioU",0)
        skip = instruction.get("skip",0)
        ind_lid_con = instruction.get("Indtime_lid_con","")   
        threshold = instruction.get("threshold","")   
        purge_on = instruction.get("purge_on","") 
        image = instruction.get("image","")
        # Append row data
        rows.append([step, procedure,ind_on_time, ind_power, text, weight, 
                     duration, lid_status, wait_time, warm_time, stirrer, 
                     mag_on_time, mag_power, action, mag_serv, pump,AudioI,AudioP,AudioQ,AudioU,skip,ind_lid_con,threshold,purge_on,image])
    
    # Include headers in the first row
    return [column_names] + rows


# Function to clear a specific table frame
def clear_table(frame):
    for widget in frame.winfo_children():
        widget.destroy()
def add_ingredient():
    ingredient_data.append(["New Ingredient", "0", "","","","","0","","",""])  # Add a new ingredient row
    clear_table(ingredients_frame)  # Clear the current table
    display_ingredients_table(ingredient_data)  # Refresh the ingredients table

# Function to add a new instruction step
def add_instruction():
    # Determine the next step number
    next_step_number = len(instruction_data)  # Current length gives the next step number
    instruction_data.append([f"Step {next_step_number}", "","0", "0", "", "0", "0", "N/A", "0","0","","","","","","","","","","","","","","",""])    # Add a new instruction row
    clear_table(instructions_frame)  # Clear the current table
    display_instructions_table(instruction_data)  # Refresh the instructions table
def paste_row(paste_above=False):
    global copied_ingredient_row, copied_instruction_row, selected_ingredient_row, selected_instruction_row
    
    if selected_ingredient_row is not None and copied_ingredient_row is not None:
        # Paste ingredient row
        if selected_ingredient_row == 0:
            insert_position = 1
        else:
            insert_position = selected_ingredient_row if paste_above else selected_ingredient_row + 1
            
        ingredient_data.insert(insert_position, copy.deepcopy(copied_ingredient_row))
        # Deselect row after pasting
        selected_ingredient_row = None
        clear_table(ingredients_frame)
        display_ingredients_table(ingredient_data)
        
    elif selected_instruction_row is not None and copied_instruction_row is not None:
        # Paste instruction row
        if selected_instruction_row == 0:
            insert_position = 1
        else:
            insert_position = selected_instruction_row if paste_above else selected_instruction_row + 1
            
        instruction_data.insert(insert_position, copy.deepcopy(copied_instruction_row))
        update_step_numbers()  # Update step numbers after paste
        # Deselect row after pasting
        selected_instruction_row = None
        clear_table(instructions_frame)
        display_instructions_table(instruction_data)
        
    else:
        if copied_ingredient_row is None and copied_instruction_row is None:
            messagebox.showwarning("Warning", "No row has been copied yet")
        else:
            messagebox.showwarning("Warning", "Please select a row in the correct table to paste")

def update_step_numbers():
    # Skip header row (index 0)
    for i in range(1, len(instruction_data)):
        instruction_data[i][0] = f"Step {i}"  # Update step number in first column

def copy_selected_row():
    global copied_ingredient_row, copied_instruction_row, selected_ingredient_row, selected_instruction_row
    
    if selected_ingredient_row is not None and selected_ingredient_row > 0:
        # Copy ingredient row
        copied_ingredient_row = copy.deepcopy(ingredient_data[selected_ingredient_row])
        copied_instruction_row = None  # Clear other clipboard
        # Deselect row after copying
        selected_ingredient_row = None
        clear_table(ingredients_frame)
        display_ingredients_table(ingredient_data)
        
    elif selected_instruction_row is not None and selected_instruction_row > 0:
        # Copy instruction row
        copied_instruction_row = copy.deepcopy(instruction_data[selected_instruction_row])
        copied_ingredient_row = None  # Clear other clipboard
        # Deselect row after copying
        selected_instruction_row = None
        clear_table(instructions_frame)
        display_instructions_table(instruction_data)
        
    else:
        messagebox.showwarning("Warning", "Please select a valid row to copy")

def delete_selected_row():
    global selected_ingredient_row, selected_instruction_row
    
    # Handle ingredient deletion
    if selected_ingredient_row is not None:
        if selected_ingredient_row == 0:  # Don't delete header row
            messagebox.showwarning("Warning", "Cannot delete header row")
            return
            
        response = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this ingredient?")
        if response:
            ingredient_data.pop(selected_ingredient_row)
            selected_ingredient_row = None
            clear_table(ingredients_frame)
            display_ingredients_table(ingredient_data)
    
    # Handle instruction deletion
    elif selected_instruction_row is not None:
        if selected_instruction_row == 0:  # Don't delete header row
            messagebox.showwarning("Warning", "Cannot delete header row")
            return
            
        response = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this instruction?")
        if response:
            instruction_data.pop(selected_instruction_row)
            update_step_numbers()
            selected_instruction_row = None
            clear_table(instructions_frame)
            display_instructions_table(instruction_data)
    
    else:
        messagebox.showwarning("Warning", "Please select a row to delete")


def show_context_menu(event, row, frame):
    global selected_ingredient_row, selected_instruction_row

    # Handle deselection when clicking already selected row
    if frame == ingredients_frame:
        if selected_ingredient_row == row:  # If clicking already selected row
            update_row_highlight(selected_ingredient_row, "white", frame)
            selected_ingredient_row = None
            return  # Don't show context menu when deselecting
        else:
            # Find and update previous highlighted row (if any)
            if selected_ingredient_row is not None:
                update_row_highlight(selected_ingredient_row, "white", frame)
            selected_ingredient_row = row
            selected_instruction_row = None
            # Highlight new selected row
            update_row_highlight(row, "yellow", frame)
    else:  # instructions_frame
        if selected_instruction_row == row:  # If clicking already selected row
            update_row_highlight(selected_instruction_row, "white", frame)
            selected_instruction_row = None
            return  # Don't show context menu when deselecting
        else:
            # Find and update previous highlighted row (if any)
            if selected_instruction_row is not None:
                update_row_highlight(selected_instruction_row, "white", frame)
            selected_instruction_row = row
            selected_ingredient_row = None
            # Highlight new selected row
            update_row_highlight(row, "yellow", frame)
    
    # Create context menu
    
    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Copy", command=lambda: copy_selected_row())
    
    # Add Paste option if there's copied content
    if (frame == ingredients_frame and copied_ingredient_row) or \
       (frame == instructions_frame and copied_instruction_row):
        paste_menu = tk.Menu(context_menu, tearoff=0)
        paste_menu.add_command(label="Paste Above", command=lambda: paste_row(True))
        paste_menu.add_command(label="Paste Below", command=lambda: paste_row(False))
        context_menu.add_cascade(label="Paste", menu=paste_menu)
    else:
        context_menu.add_command(label="Paste", state="disabled")

    context_menu.add_separator()
    context_menu.add_command(label="Delete", command=lambda: delete_selected_row())

    # Show context menu at the right-click location
    try:
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        context_menu.grab_release()

def update_row_highlight(row, color, frame):
    """Update the background color of a specific row without refreshing the entire table"""
    if row is None or row == 0:  # Don't highlight header row
        return
        
    for widget in frame.grid_slaves(row=row):
        for label in widget.winfo_children():
            if isinstance(label, tk.Label):
                # Preserve red background for missing audio files
                if (frame == ingredients_frame and widget.grid_info()['column'] in [4, 5, 6, 7]) or \
                   (frame == instructions_frame and widget.grid_info()['column'] in [16, 17, 18, 19]):
                    if label.cget('text') and not audio_file_exists(label.cget('text')):
                        continue  # Skip updating color for missing audio files
                label.configure(bg=color)

def display_ingredients_table(data):
    highlight_color = "yellow"  # Define highlight color
    default_color = "white"     # Define default color
    
    for i, row in enumerate(data):
        for j, value in enumerate(row):
            cell = tk.Frame(ingredients_frame, relief="solid", borderwidth=1)
            cell.grid(row=i, column=j, sticky="nsew", padx=1, pady=1)
            
            # Set background color based on selection and conditions
            bg_color = highlight_color if i == selected_ingredient_row else default_color
            if i == 0:  # If it's header row
                bg_color = "light grey"
            if i > 0 and j in [4, 5, 6, 7] and value and not audio_file_exists(value):
                bg_color = "red"
            
            underline = (j in [4, 5, 6, 7] and i > 0)
            
            label = tk.Label(cell, text=str(value), font=('Arial', 10, 'underline' if underline else ''),
                             bg=bg_color, anchor='center')
            label.pack(side='left', fill='both', expand=True)

            if i > 0:  # Skip header row
                label.bind("<Double-1>", lambda event, r=i, c=j: edit_cell(r, c, ingredient_data, ingredients_frame))
                label.bind("<Button-3>", lambda event, r=i, f=ingredients_frame: show_context_menu(event, r, f))

            if j in [4, 5, 6, 7]:  # Audio columns
                label.bind("<Button-1>", lambda event, r=i, c=j: on_audio_click(r, c))
            if j == 8 and i > 0:  # Image column
                label.bind("<Enter>", lambda event, v=value: show_image_popup(event, v, ingredients_frame.winfo_toplevel()))

    for j in range(len(data[0])):
        ingredients_frame.grid_columnconfigure(j, weight=1)

def display_instructions_table(data):
    highlight_color = "yellow"  # Define highlight color
    default_color = "white"     # Define default color
    
    for i, row in enumerate(data):
        for j, value in enumerate(row):
            cell = tk.Frame(instructions_frame, relief="solid", borderwidth=1)
            cell.grid(row=i, column=j, sticky="nsew", padx=1, pady=1)
            
            # Set background color based on selection and conditions
            bg_color = highlight_color if i == selected_instruction_row else default_color
            if i == 0:  # If it's header row
                bg_color = "light grey"
            if i > 0 and j in [16, 17, 18, 19] and value and not audio_file_exists(value):
                bg_color = "red"
            
            underline = (j in [16, 17, 18, 19] and i > 0)
            
            label = tk.Label(cell, text=str(value), font=('Arial', 10, 'underline' if underline else ''),
                             bg=bg_color, anchor='center')
            label.pack(side='left', fill='both', expand=True)

            if i > 0:  # Skip header row
                label.bind("<Double-1>", lambda event, r=i, c=j: edit_cell(r, c, instruction_data, instructions_frame))
                label.bind("<Button-3>", lambda event, r=i, f=instructions_frame: show_context_menu(event, r, f))

            if j in [16, 17, 18, 19]:  # Audio columns
                label.bind("<Button-1>", lambda event, r=i, c=j: on_instruction_audio_click(r, c))
            if j == 24 and i > 0:  # Image column
                label.bind("<Enter>", lambda event, v=value: show_image_popup(event, v, instructions_frame.winfo_toplevel()))

    for j in range(len(data[0])):
        instructions_frame.grid_columnconfigure(j, weight=1)

def move_row_up(data_table, frame):
    global selected_instruction_row
    if frame != instructions_frame:  # Only allow moving rows in instructions table
        return
        
    if selected_instruction_row is None or selected_instruction_row <= 1:  # Don't move header row or first row
        messagebox.showwarning("Warning", "Cannot move this row up")
        return
    
    # Swap the selected row with the one above it
    data_table[selected_instruction_row], data_table[selected_instruction_row - 1] = \
        data_table[selected_instruction_row - 1], data_table[selected_instruction_row]
    
    # Update the selected row index to reflect the new position
    selected_instruction_row -= 1
    
    # Update step numbers
    update_step_numbers()
    
    # Clear and refresh the table to reflect the changes
    clear_table(frame)
    display_instructions_table(data_table)

def move_row_down(data_table, frame):
    global selected_instruction_row
    if frame != instructions_frame:  # Only allow moving rows in instructions table
        return
        
    if selected_instruction_row is None or selected_instruction_row >= len(data_table) - 1:  # Don't move last row
        messagebox.showwarning("Warning", "Cannot move this row down")
        return
    
    # Swap the selected row with the one below it
    data_table[selected_instruction_row], data_table[selected_instruction_row + 1] = \
        data_table[selected_instruction_row + 1], data_table[selected_instruction_row]
    
    # Update the selected row index to reflect the new position
    selected_instruction_row += 1
    
    # Update step numbers
    update_step_numbers()
    
    # Clear and refresh the table to reflect the changes
    clear_table(frame)
    display_instructions_table(data_table)

def clear_table(frame):
    for widget in frame.winfo_children():
        widget.destroy()



# Modify the display functions to detect row selection

def edit_cell(row, col, data_table, frame):
    # Check if this is the image column (column 24) in the ingredients table
    if frame == ingredients_frame and col == 8:  # Image column
        current_value = data_table[row][col]
        file_name = simpledialog.askstring("Image Name", "Enter image name (without extension):")
        if file_name:
            if handle_image_upload(file_name):
                data_table[row][col] = file_name
                # Clear and refresh both tables
                clear_table(ingredients_frame)
                clear_table(instructions_frame)
                display_ingredients_table(ingredient_data)
                display_instructions_table(instruction_data)
        return
    if frame == instructions_frame and col == 24:  # Image column
        current_value = data_table[row][col]
        file_name = simpledialog.askstring("Image Name", "Enter image name (without extension):")
        if file_name:
            if handle_image_upload(file_name):
                data_table[row][col] = file_name
                # Clear and refresh both tables
                clear_table(ingredients_frame)
                clear_table(instructions_frame)
                display_ingredients_table(ingredient_data)
                display_instructions_table(instruction_data)
        return
    # original edit_cell function remains the same
    current_value = data_table[row][col]
    if (frame == ingredients_frame and col == 2) or (frame == instructions_frame and col == 13):
        return  # Exit the function without creating an entry widget
        
    if frame == ingredients_frame:
        audio_columns = [4, 5, 6, 7]  # Audio columns for ingredients
    elif frame == instructions_frame:
        audio_columns = [16, 17, 18, 19]  # Audio columns for instructions
    else:
        audio_columns = []  # No audio columns if it's neither

    if col in audio_columns:
        if not audio_file_exists(current_value):
            if handle_missing_audio(current_value):
                # If the file was successfully added, update the cell color
                cell = frame.grid_slaves(row=row, column=col)[0]
                cell.config(bg='white')  # or any other color to indicate success
            else:
                # If the file is still missing, keep the cell red
                cell = frame.grid_slaves(row=row, column=col)[0]
                cell.config(bg='red')

    # Create an entry widget for inline editing
    entry = tk.Entry(frame, font=('Arial', 10))
    entry.insert(0, current_value)
    entry.grid(row=row, column=col, sticky="nsew")
    
    def save_value():
        new_value = entry.get()
        old_value = data_table[row][col]
        
        if frame == instructions_frame and (col == 6 or col == 2):  # Duration or Induction On Time column
            try:
                seconds = int(new_value)
                
                if seconds < 0 or seconds > 6000:
                    field_name = "Duration" if col == 6 else "Induction On Time"
                    messagebox.showerror("Error", f"{field_name} must be between 0 and 6000 seconds.")
                    return
                    
                # Update both Duration and Induction On Time
                data_table[row][2] = str(seconds)  # Induction On Time
                data_table[row][6] = str(seconds)  # Duration
                
                # Format time for audioU
                if seconds >= 60:
                    minutes = seconds // 60
                    remaining_seconds = seconds % 60
                    if remaining_seconds == 0:
                        audioU_text = f"{minutes}Minute"
                    else:
                        audioU_text = f"{minutes}Minute {remaining_seconds}Seconds"
                else:
                    audioU_text = f"{seconds}Seconds"
                
                # Update audioU column (index 19)
                data_table[row][19] = audioU_text
                
            except ValueError:
                field_name = "Duration" if col == 6 else "Induction On Time"
                messagebox.showerror("Error", f"Please enter a valid number for {field_name}")
                return
        if frame == ingredients_frame:
            if col == 0:  # Name
                update_name(old_value, new_value, ingredients_frame)
            elif col == 1:  # Weight
                update_weight(data_table[row][0], new_value, ingredients_frame)
            elif col in [2, 3, 5]:  # Action, audio, audioP
                update_action_audio(row, col, new_value, ingredients_frame)
        
        elif frame == instructions_frame:
            if col == 4:  # Text
                update_name(old_value, new_value, instructions_frame)
            elif col == 5:  # Weight
                update_weight(data_table[row][4], new_value, instructions_frame)
            elif col in [1, 13, 17]:  # Procedure, Action, audioP
                update_action_audio(row, col, new_value, instructions_frame)
            
            # Apply validation for instruction table
            if not validate_instruction_input(col, new_value):
                entry.delete(0, tk.END)
                entry.insert(0, old_value)
                return

        data_table[row][col] = new_value
        
        # Clear and refresh both tables
        clear_table(ingredients_frame)
        clear_table(instructions_frame)
        display_ingredients_table(ingredient_data)
        display_instructions_table(instruction_data)

        # Remove the entry widget
        entry.destroy()

    # Bind the return key to save the new value
    entry.bind("<Return>", lambda event: save_value())
    entry.bind("<FocusOut>", lambda event: save_value())
    entry.focus_set()

def validate_instruction_input(col, value):
    value_str = str(value).strip()
    if col == 20 and not validate_skip(value_str):
        messagebox.showerror("Invalid Value", "The 'Skip' column can only accept 'true', 'false', or be blank.")
        return False
    if col == 10 and not validate_Stirrer(value_str):
        messagebox.showerror("Invalid Value", "The 'Stirrer' column can only accept values from '0 to 4' or be blank.")
        return False
    if col == 7 and not validate_Lid(value_str):
        messagebox.showerror("Invalid Value", "The 'Lid_status' column can only accept 'open', 'close' or be blank.")
        return False
    if col == 3 and not validate_induction(value_str):
        messagebox.showerror("Invalid Value", "The 'Induction' column can only accept value in terms 10x or be blank.")
        return False
    if col == 12 and not validate_magnetron(value_str):
        messagebox.showerror("Invalid Value", "The 'Magnetron' column can only accept value in terms of 20x or be blank.")
        return False
    return True

def validate_skip(value):
    return value.lower() in ["true", "false", ""]

def validate_Stirrer(value):
    return value in ["0", "1", "2", "3", "4", ""]

def validate_Lid(value):
    return value.lower() in ["open", "close", ""]

def validate_induction(value):
    return value in ["0", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100", ""]

def validate_magnetron(value):
    return value in ["0", "20", "40", "60", "80", "100", ""]

def update_action_audio(row, col, new_value, frame):
    if frame == ingredients_frame:
        if col == 2:  # Action
            words = new_value.split()
            if len(words) >= 3:
                ingredient_data[row][3] = words[0]  # audio
                ingredient_data[row][0] = words[1]  # Name
                ingredient_data[row][5] = words[0]  # audioP
                update_name(ingredient_data[row][0], words[1], ingredients_frame)
        elif col == 3:  # audio
            ingredient_data[row][3] = new_value  # audio
            ingredient_data[row][5] = new_value  # audioP
            # Update Action (column 2) with new audio while preserving name and weight
            ingredient_data[row][2] = f"{new_value} {ingredient_data[row][0]} {ingredient_data[row][1]}"
        elif col == 0:  # Name
            ingredient_data[row][0] = new_value  # Name
            ingredient_data[row][4] = new_value  # AudioI
            # Update Action (column 2) with new name while preserving audio and weight
            ingredient_data[row][2] = f"{ingredient_data[row][3]} {new_value} {ingredient_data[row][1]}"
        elif col == 1:  # Weight
            ingredient_data[row][1] = new_value  # Weight
            # Update Action (column 2) with new weight while preserving audio and name
            ingredient_data[row][2] = f"{ingredient_data[row][3]} {ingredient_data[row][0]} {new_value}"
    
    elif frame == instructions_frame:
        # For instruction frame updates
        if col == 13:  # Action
            words = new_value.split()
            if words:
                instruction_data[row][1] = words[0]  # Procedure
                instruction_data[row][17] = words[0]  # audioP
                if len(words) > 1:
                    instruction_data[row][4] = words[-1]  # Text
                    instruction_data[row][16] = words[-1]  # AudioI
                    update_name(instruction_data[row][4], words[-1], instructions_frame)
        elif col == 1:  # Procedure update
            instruction_data[row][1] = new_value  # Procedure
            instruction_data[row][17] = new_value  # audioP
            instruction_data[row][13] = f"{new_value} {instruction_data[row][4]} {instruction_data[row][5]}"
        elif col == 4:  # Text update
            instruction_data[row][4] = new_value  # Text
            instruction_data[row][16] = new_value  # AudioI
            instruction_data[row][13] = f"{instruction_data[row][1]} {new_value} {instruction_data[row][5]}"
        elif col == 5:  # Weight update
            instruction_data[row][5] = new_value  # Weight
            instruction_data[row][13] = f"{instruction_data[row][1]} {instruction_data[row][4]} {new_value}"

def update_name(old_name, new_name, frame):
    if frame == ingredients_frame:
        for ingredient in ingredient_data[1:]:
            if ingredient[0] == old_name:
                ingredient[0] = new_name  # Name
                # Update Action with new name while preserving audio and weight
                ingredient[2] = f"{ingredient[3]} {new_name} {ingredient[1]}"
                ingredient[4] = new_name  # AudioI
        
        for instruction in instruction_data[1:]:
            if instruction[4] == old_name:
                instruction[4] = new_name  # Text
                instruction[13] = f"{instruction[1]} {new_name} {instruction[5]}"
                instruction[16] = new_name  # AudioI
    
    elif frame == instructions_frame:
        for instruction in instruction_data[1:]:
            if instruction[4] == old_name:
                instruction[4] = new_name  # Text
                instruction[13] = f"{instruction[1]} {new_name} {instruction[5]}"
                instruction[16] = new_name  # AudioI
        
        for ingredient in ingredient_data[1:]:
            if ingredient[0] == old_name:
                ingredient[0] = new_name  # Name
                ingredient[2] = f"{ingredient[3]} {new_name} {ingredient[1]}"
                ingredient[4] = new_name  # AudioI

def update_weight(item_name, new_weight, frame):
    weight_parts = new_weight.split()
    numeric_weight = weight_parts[0] if weight_parts else "0"
    unit = weight_parts[1] if len(weight_parts) > 1 else ""

    if frame == ingredients_frame:
        for ingredient in ingredient_data[1:]:
            if ingredient[0] == item_name:
                ingredient[1] = new_weight  # Weight
                # Update Action with new weight while preserving audio and name
                ingredient[2] = f"{ingredient[3]} {ingredient[0]} {new_weight}"
                ingredient[6] = numeric_weight  # AudioQ
                ingredient[7] = unit  # AudioU
        
        for instruction in instruction_data[1:]:
            if instruction[4] == item_name:
                instruction[5] = new_weight  # Weight
                instruction[13] = f"{instruction[1]} {instruction[4]} {new_weight}"
                instruction[18] = numeric_weight  # AudioQ
    
    elif frame == instructions_frame:
        for instruction in instruction_data[1:]:
            if instruction[4] == item_name:
                instruction[5] = new_weight  # Weight
                instruction[13] = f"{instruction[1]} {instruction[4]} {new_weight}"
                instruction[18] = numeric_weight  # AudioQ
        
        for ingredient in ingredient_data[1:]:
            if ingredient[0] == item_name:
                ingredient[1] = new_weight  # Weight
                ingredient[2] = f"{ingredient[3]} {ingredient[0]} {new_weight}"
                ingredient[6] = numeric_weight  # AudioQ
                ingredient[7] = unit  # AudioU

# Function to save the updated data back to the JSON file
def save_json():
    global data, ingredient_data, instruction_data
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    
    if not file_path:
        return
    
    try:
        # Initialize the updated data structure
        updated_data = {
            "name": ["Unknown Recipe"],
            "audio1": [""],
            "audio2": [""],
            "category": "0",
            "description": "",
            "difficulty": "Easy",
            "id": 0,
            "imageUrl": "",
            "isSelected": False,
            "subCategories": "",
            "tags": "",
            "Ingredients": [],
            "Instruction": []
        }

        # Update recipe metadata if 'data' exists
        if isinstance(data, dict):
            updated_data["audio1"] = data.get("audio1", [""])
            updated_data["audio2"] = data.get("audio2", [""])
            updated_data["category"] = str(data.get("category", "0"))
            updated_data["description"] = str(data.get("description", ""))
            updated_data["difficulty"] = str(data.get("difficulty", "Easy"))
            updated_data["id"] = int(data.get("id", 0))
            updated_data["imageUrl"] = str(data.get("imageUrl", ""))
            updated_data["isSelected"] = bool(data.get("isSelected", False))
            updated_data["subCategories"] = str(data.get("subCategories", ""))
            updated_data["tags"] = str(data.get("tags", ""))

        # Prompt for recipe name if it's "Unknown Recipe"
        if updated_data["name"] == ["Unknown Recipe"]:
            new_name = simpledialog.askstring("Recipe Name", "Please enter a name for the recipe:")
            if new_name:
                updated_data["name"] = [new_name]
            else:
                messagebox.showerror("Error", "Recipe name is required!")
                return

        # Process Ingredients
        current_id = 1  # Keep track of actual ID for valid ingredients
        if isinstance(ingredient_data, list) and len(ingredient_data) > 1:
            for i in range(1, len(ingredient_data)):  # Skip header row
                row = ingredient_data[i]
                
                # Skip if the row is invalid or name is empty or "New Ingredient"
                if not isinstance(row, list) or len(row) == 0:
                    continue
                    
                ingredient_name = str(row[0]).strip()
                if not ingredient_name or ingredient_name == "New Ingredient":
                    continue
                
                ingredient = {
                    "app_audio": "",
                    "audio": "",
                    "audioI": "",
                    "audioP": "",
                    "audioQ": "",
                    "audioU": "",
                    "id": current_id,  # Use current_id instead of i
                    "image": "",
                    "text": "",
                    "title": "",
                    "weight": ""
                }
                
                ingredient["title"] = ingredient_name
                ingredient["weight"] = str(row[1]) if len(row) > 1 else ""
                ingredient["app_audio"] = str(row[2]) if len(row) > 2 else ""
                ingredient["audio"] = str(row[3]) if len(row) > 3 else ""
                ingredient["audioI"] = str(row[4]) if len(row) > 4 else ""
                ingredient["audioP"] = str(row[5]) if len(row) > 5 else ""
                
                # Safely split weight
                weight_parts = ingredient["weight"].split()
                ingredient["audioQ"] = weight_parts[0] if len(weight_parts) > 0 else ""
                ingredient["audioU"] = weight_parts[1] if len(weight_parts) > 1 else ""
                
                # Format the image path as required
                image_name = str(row[8]) if len(row) > 8 else ""
                if image_name:
                    ingredient["image"] = f"content://com.invent.ontocook.cropper.fileprovider/my_images/Pictures/{image_name}.png"
                ingredient["text"] = str(row[9]) if len(row) > 9 else ""
                
                updated_data["Ingredients"].append(ingredient)
                current_id += 1

        # Process Instructions
        current_id = 1  # Reset current_id for instructions
        if isinstance(instruction_data, list) and len(instruction_data) > 1:
            for i in range(1, len(instruction_data)):  # Skip header row
                row = instruction_data[i]
                
                # Skip if row doesn't exist or Text column is empty
                if not isinstance(row, list) or len(row) <= 4 or not row[4].strip():
                    continue
                
                instruction = {
                    "Audio": "",
                    "Indtime_lid_con": "",
                    "Induction_on_time": "0",
                    "Induction_power": "0",
                    "Magnetron_on_time": "0",
                    "Magnetron_power": "0",
                    "Text": "",
                    "Weight": "",
                    "app_audio": "",
                    "audioI": "",
                    "audioP": "",
                    "audioQ": "",
                    "audioU": "",
                    "durationInSec": 0,
                    "id": current_id,
                    "image": "",
                    "lid": "",
                    "mag_severity": "",
                    "pump_on": "0",
                    "skip": "false",
                    "stirrer_on": "0",
                    "wait_time": "0",
                    "warm_time": "0",
                    "threshold": "0",
                    "purge_on": "0"
                }
                
                field_mapping = {
                    1: "Audio", 2: "Induction_on_time", 3: "Induction_power", 4: "Text", 5: "Weight",
                    6: "durationInSec", 7: "lid", 8: "wait_time", 9: "warm_time", 10: "stirrer_on",
                    11: "Magnetron_on_time", 12: "Magnetron_power", 13: "app_audio", 14: "mag_severity",
                    15: "pump_on", 16: "audioI", 17: "audioP", 18: "audioQ", 19: "audioU", 20: "skip",
                    21: "Indtime_lid_con", 22: "threshold", 23: "purge_on", 24: "image"
                }
                
                for idx, field in field_mapping.items():
                    if idx < len(row):
                        if field == "durationInSec":
                            instruction[field] = int(row[idx]) if str(row[idx]).isdigit() else 0
                        else:
                            instruction[field] = str(row[idx])
                
                # Format the image path as required
                image_name = str(row[24]) if len(row) > 24 else ""
                if image_name:
                    instruction["image"] = f"content://com.invent.ontocook.cropper.fileprovider/my_images/Pictures/{image_name}.png"
                
                updated_data["Instruction"].append(instruction)
                current_id += 1
 
        # Write the updated data to the JSON file
        with open(file_path, 'w') as file:
            json.dump(updated_data, file, indent=2)

        messagebox.showinfo("Success", "Data saved successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving: {str(e)}")
        # Print the full error traceback for debugging
        import traceback
        traceback.print_exc()

def prt_action(part_name):
    print(f"{part_name} button clicked")
def new_recipe():
    global ingredient_data, instruction_data, data, selected_row, error_cells

    # Reset selection and errors
    selected_row = None
    error_cells = []

    # Initialize default recipe metadata
    data = {
        "name": ["New Recipe"],
        "Ingredients": [
            {
                "title": "Water",
                "weight": "500 ml",
                "app_audio": "add water 500 ml",
                "audio": "add",
                "audioI": "Water",
                "audioP": "add",
                "audioQ": "500",
                "audioU": "ml",
                "image": "",
                "text": "Add water"
            },
            {
                "title": "Oil",
                "weight": "30 ml",
                "app_audio": "add oil 30 ml",
                "audio": "add",
                "audioI": "Oil",
                "audioP": "add",
                "audioQ": "30",
                "audioU": "ml",
                "image": "",
                "text": "Add oil"
            },
            {
                "title": "Salt",
                "weight": "10 g",
                "app_audio": "add salt 10 g",
                "audio": "add",
                "audioI": "Salt",
                "audioP": "add",
                "audioQ": "10",
                "audioU": "g",
                "image": "",
                "text": "Add salt"
            }
        ],
        "Instruction": [
            {
                "Audio": "heat",
                "Induction_on_time": "120",
                "Induction_power": "80",
                "Text": "Water",
                "Weight": "500 ml",
                "durationInSec": "120",
                "lid": "close",
                "wait_time": "0",
                "warm_time": "0",
                "stirrer_on": "1",
                "Magnetron_on_time": "0",
                "Magnetron_power": "0",
                "app_audio": "heat water 500 ml",
                "mag_severity": "",
                "pump_on": "0",
                "audioI": "Water",
                "audioP": "heat",
                "audioQ": "500",
                "audioU": "2Minutes",
                "skip": "false",
                "Indtime_lid_con": "120",
                "threshold": "0",
                "purge_on": "0",
                "image": ""
            },
            {
                "Audio": "add",
                "Induction_on_time": "0",
                "Induction_power": "0",
                "Text": "Oil",
                "Weight": "30 ml",
                "durationInSec": "30",
                "lid": "open",
                "wait_time": "30",
                "warm_time": "0",
                "stirrer_on": "0",
                "Magnetron_on_time": "0",
                "Magnetron_power": "0",
                "app_audio": "add oil 30 ml",
                "mag_severity": "",
                "pump_on": "0",
                "audioI": "Oil",
                "audioP": "add",
                "audioQ": "30",
                "audioU": "30Seconds",
                "skip": "false",
                "Indtime_lid_con": "",
                "threshold": "0",
                "purge_on": "0",
                "image": ""
            },
            {
                "Audio": "stir",
                "Induction_on_time": "60",
                "Induction_power": "40",
                "Text": "Salt",
                "Weight": "",
                "durationInSec": "60",
                "lid": "close",
                "wait_time": "0",
                "warm_time": "0", # Changed from "30" to "0"
                "stirrer_on": "1",
                "Magnetron_on_time": "30",
                "Magnetron_power": "30",
                "app_audio": "stir mixture",
                "mag_severity": "medium",
                "pump_on": "1",
                "audioI": "Mixture",
                "audioP": "stir",
                "audioQ": "",
                "audioU": "1Minute",
                "skip": "false",
                "Indtime_lid_con": "60",
                "threshold": "0",
                "purge_on": "0",
                "image": ""
            }
        ]
    }

    # Format the ingredients data into a table-like format
    ingredient_data = format_ingredients(data)

    # Format the instructions data into a table-like format
    instruction_data = format_instructions(data)

    # Update the recipe name in the title
    title_label.config(text="Recipe: New Recipe")

    # Clear existing tables
    for widget in ingredients_frame.winfo_children():
        widget.destroy()
    for widget in instructions_frame.winfo_children():
        widget.destroy()

    # Create new tables with default data
    display_ingredients_table(ingredient_data)
    display_instructions_table(instruction_data)
    for i in range(1, len(ingredient_data)):
        for j in range(len(ingredient_data[i])):
            cell = ingredients_frame.grid_slaves(row=i, column=j)
            if cell:
                cell[0].bind('<Double-Button-1>', 
                    lambda e, row=i, col=j: edit_cell(row, col, ingredient_data, ingredients_frame))

    # Add cell editing functionality to instructions table
    for i in range(1, len(instruction_data)):
        for j in range(len(instruction_data[i])):
            cell = instructions_frame.grid_slaves(row=i, column=j)
            if cell:
                cell[0].bind('<Double-Button-1>', 
                    lambda e, row=i, col=j: edit_cell(row, col, instruction_data, instructions_frame))
    # Enable all buttons
    save_button.config(state='normal')
    add_ingredient_button.config(state='normal')
    add_step_button.config(state='normal')
    move_up_button.config(state='normal')
    move_down_button.config(state='normal')
    
def load_text_files():
    # List all text files in the specified directory
    return [f for f in os.listdir(SELECT_FOLDER_PATHS) if f.endswith('.txt')]

def select_recipe(event=None):  # Accept an optional event argument
    # Logic for selecting a recipe
    title_label.config(text="Recipe: Selected Recipe")
    print("Select Recipe button clicked")
    
    # Load and display text files in the combo box
    text_files = load_text_files()
    if text_files:
        recipe_combobox['values'] = text_files  # Populate the combo box with text files
        recipe_combobox.pack(pady=10)  # Show the combo box
    else:
        print("No text files available.")

def load_file(event=None):
    global ingredient_data, instruction_data  # Declare ingredient_data and instruction_data as global
    
    selected_file = recipe_combobox.get()  # Get the selected file from the combo box
    if selected_file:
        file_path = os.path.join(SELECT_FOLDER_PATHS, selected_file)
        
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                
                # Set recipe name at the heading
                recipe_name = data.get("name", ["Unknown Recipe"])[0]
                title_label.config(text=f"Recipe: {recipe_name}")
                
                # Extract ingredient and instruction data for the tables
                ingredient_data = format_ingredients(data)
                instruction_data = format_instructions(data)
                
                # Clear the existing table frames before adding new data
                clear_table(ingredients_frame)
                clear_table(instructions_frame)
                
                # Display the data in both tables
                display_ingredients_table(ingredient_data)
                display_instructions_table(instruction_data)
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    hide_combobox()  # Hide the combo box after loading

def hide_combobox():
    recipe_combobox.pack_forget()  # Hide the combo box
def refresh_tables():
    global error_cells
    error_cells = []  # Clear any existing error cells
    
    # Synchronize values in ingredients table
    for i, row in enumerate(ingredient_data[1:], 1):
        # Update Action using existing functions
        update_action_audio(i, 3, row[3], ingredients_frame)  # Sync audio
        update_name(row[0], row[0], ingredients_frame)       # Sync name
        update_weight(row[0], row[1], ingredients_frame)     # Sync weight
    
    # Synchronize values in instructions table
    for i, row in enumerate(instruction_data[1:], 1):
        # Update Action using existing functions
        update_action_audio(i, 1, row[1], instructions_frame)  # Sync procedure
        update_action_audio(i, 4, row[4], instructions_frame)  # Sync text
        update_action_audio(i, 5, row[5], instructions_frame)  # Sync weight
    
    # Clear and redraw both tables
    clear_table(ingredients_frame)
    clear_table(instructions_frame)
    display_ingredients_table(ingredient_data)
    display_instructions_table(instruction_data)
    
    # Recheck for errors
    error_cells = check_for_errors(instruction_data, instructions_frame)
    
root = tk.Tk()
root.title("Recipe Editor")

# Create a frame to hold the canvas and scrollbars
container = tk.Frame(root)
container.pack(fill='both', expand=True)

# Create a canvas that will hold all the content with scrollbars
main_canvas = tk.Canvas(container)
main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add vertical and horizontal scrollbars for the entire window
y_scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=main_canvas.yview)
y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

x_scrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=main_canvas.xview)
x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

main_canvas.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

# Create a frame inside the canvas to hold all the content
content_frame = tk.Frame(main_canvas)

# Add the content_frame to the canvas window
main_canvas.create_window((0, 0), window=content_frame, anchor='nw')

def on_mousewheel(event):
    # Cross-platform mouse wheel scrolling
    if platform.system() == 'Windows':
        delta = -1 * (event.delta // 120)
    elif platform.system() == 'Darwin':  # macOS
        delta = -1 * event.delta
    else:  # Linux
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            return
    
    if event.state == 0:  # No modifier keys
        main_canvas.yview_scroll(delta, "units")
    elif event.state & 0x1:  # Shift is pressed
        main_canvas.xview_scroll(delta, "units")

def on_frame_configure(event):
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))

# Bind mouse wheel events for all platforms
if platform.system() == 'Windows':
    # Windows bindings
    main_canvas.bind("<MouseWheel>", on_mousewheel)
    content_frame.bind("<MouseWheel>", on_mousewheel)
elif platform.system() == 'Darwin':  # macOS
    # macOS bindings
    main_canvas.bind("<MouseWheel>", on_mousewheel)
    content_frame.bind("<MouseWheel>", on_mousewheel)
else:
    # Linux bindings
    main_canvas.bind("<Button-4>", on_mousewheel)
    main_canvas.bind("<Button-5>", on_mousewheel)
    content_frame.bind("<Button-4>", on_mousewheel)
    content_frame.bind("<Button-5>", on_mousewheel)

# Bind the scrolling to the main window as well to ensure it works everywhere
root.bind_all("<MouseWheel>", on_mousewheel)  # Windows/macOS
root.bind_all("<Button-4>", on_mousewheel)    # Linux
root.bind_all("<Button-5>", on_mousewheel)    # Linux

# Bind frame configuration
content_frame.bind("<Configure>", on_frame_configure)
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X)
# Create a frame for the buttons at the top left
button_frame = tk.Frame(top_frame)
button_frame.pack(pady=10)

# New Recipe button
new_recipe_button = tk.Button(button_frame, text="New Recipe", command=new_recipe)
new_recipe_button.pack(side='left', padx=5)

# Select Recipe button
select_button = tk.Button(button_frame, text="Select the Recipe", command=select_recipe)
select_button.pack(side='left', padx=5)

# Create a combo box for displaying text files (initially hidden)
recipe_combobox = ttk.Combobox(root)
recipe_combobox.pack_forget()  # Hide the combo box initially

# Bind the combo box selection to load the file directly
recipe_combobox.bind("<<ComboboxSelected>>", load_file)

# Create a button to load the selected text file (initially hidden)
load_button = tk.Button(root, text="Load File", command=load_file)
load_button.pack_forget()  # Hide the load button initially

# Create a button to load the selected text file (initially hidden)
load_button = tk.Button(root, text="Load File", command=load_file)
load_button.pack_forget()  # Hide the load button initially

# Set up the title frame for "on2cook"
title_frame = tk.Frame(content_frame)
title_frame.pack(pady=10)

# Title labels
on_label = tk.Label(title_frame, text="on", font=('Arial', 24), fg='red')
on_label.pack(side=tk.LEFT)

two_cook_label = tk.Label(title_frame, text="2cook", font=('Arial', 24), fg='black')
two_cook_label.pack(side=tk.LEFT)

# Label for displaying the recipe name
recipe_name = "Your Recipe Name"  # Placeholder for the recipe name
title_label = tk.Label(content_frame, text=f"Recipe: {recipe_name}", font=('Arial', 16), anchor='center')
title_label.pack(pady=10, anchor='center')  # Center the recipe name

# Ingredients section
ingredients_label = tk.Label(content_frame, text="Ingredients", font=('Arial', 14, 'bold'), anchor='center')
ingredients_label.pack(pady=5, anchor='center')  # Center the ingredients label

ingredients_frame = tk.Frame(content_frame)
ingredients_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

# Instructions section
instructions_label = tk.Label(content_frame, text="Instructions", font=('Arial', 14, 'bold'), anchor='center')
instructions_label.pack(pady=5, anchor='center')  # Center the instructions label

instructions_frame = tk.Frame(content_frame)
instructions_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)



# Create a separate frame for buttons at the bottom of the main window
bottom_frame = tk.Frame(root)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Button frame inside the bottom frame
button_frame = tk.Frame(bottom_frame)
button_frame.pack(pady=10)

# Load button
load_button = tk.Button(button_frame, text="Load Recipe", command=load_json)
load_button.pack(side='left', padx=5)

# Save button
save_button = tk.Button(button_frame, text="Save Recipe", command=save_json)
save_button.pack(side='left', padx=5)

# Add ingredient button
add_ingredient_button = tk.Button(button_frame, text="Add Ingredient", command=add_ingredient)
add_ingredient_button.pack(side='left', padx=5)

# Add step button
add_step_button = tk.Button(button_frame, text="Add Step", command=add_instruction)
add_step_button.pack(side='left', padx=5)

# Move up button
move_up_button = tk.Button(button_frame, text="Move Up", command=lambda: move_row_up(instruction_data, instructions_frame))
move_up_button.pack(side='left', padx=5)

# Move down button
move_down_button = tk.Button(button_frame, text="Move Down", command=lambda: move_row_down(instruction_data, instructions_frame))
move_down_button.pack(side='left', padx=5)

# PRT buttons
prt1_button = tk.Button(button_frame, text="prt1", command=lambda: prt_action("prt1"))
prt1_button.pack(side='left', padx=5)

prt2_button = tk.Button(button_frame, text="prt2", command=lambda: prt_action("prt2"))
prt2_button.pack(side='left', padx=5)

prt3_button = tk.Button(button_frame, text="prt3", command=lambda: prt_action("prt3"))
prt3_button.pack(side='left', padx=5)

prt4_button = tk.Button(button_frame, text="prt4", command=lambda: prt_action("prt 4"))
prt4_button.pack(side='left', padx=5)

refresh_button = tk.Button(button_frame, text="Refresh", command=refresh_tables)
refresh_button.pack(side=tk.LEFT, padx=5)


root.mainloop()