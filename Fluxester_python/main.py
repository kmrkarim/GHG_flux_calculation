import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
from f1_file_selector import select_file
from f2_column_selector_ui import create_column_selection_ui
from f3_data_plotting import process_columns

def read_file(file_path):
    """Reads a file and returns a pandas DataFrame based on its type."""
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path, encoding='utf-8')  # Try UTF-8 first
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        elif file_path.endswith('.txt'):
            return pd.read_csv(file_path, delimiter='\t', encoding='utf-8')
        else:
            messagebox.showerror("Error", "Unsupported file type. Please select a TXT, CSV, or Excel file.")
            return None
    except UnicodeDecodeError:
        # Retry with Latin-1 if UTF-8 fails
        try:
            if file_path.endswith('.csv'):
                return pd.read_csv(file_path, encoding='latin1')
            elif file_path.endswith('.txt'):
                return pd.read_csv(file_path, delimiter='\t', encoding='latin1')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read the file with fallback encoding: {e}")
            return None
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process the file: {e}")
        return None


# Function to process the selected file
def process_file(file_path):
    """Processes the selected file and passes data to the column selection UI."""
    try:
        # Read the selected file
        data = read_file(file_path)

        if data is None:
            return  # Exit if file type is unsupported

        # Check if DataFrame has any data (excluding column names)
        if data.empty or data.dropna(how='all').empty:
            messagebox.showerror("Error", "The selected file contains only headers without data.")
            return  # Exit the function if the DataFrame is effectively empty

        # Call the next step in the pipeline
        create_column_selection_ui(data, process_columns)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process the file: {e}")

# Function to handle file opening
def open_file():
    """Opens a file dialog for selecting a file."""
    file_path = filedialog.askopenfilename(
        title="Open File",
        initialdir="./",  # Set a default initial directory
        filetypes=(("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("Text files", "*.txt"))
    )
    if file_path:
        app.destroy()  # Close the start window
        process_file(file_path)

# Function to confirm before exiting the app
def on_closing():
    """Prompts the user for confirmation before closing the app."""
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        app.destroy()

# Set appearance and theme **before creating the window**
ctk.set_appearance_mode("Light")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

# Create the main application window
app = ctk.CTk()
app.title("Plant and Soil GHG Flux Data Processing Software")
app.geometry("500x375")
app.resizable(True, True)
ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

# Handle window close confirmation
app.protocol("WM_DELETE_WINDOW", on_closing)

# Add a spacer
spacer = ctk.CTkLabel(app, text="")
spacer.pack(pady=15)  # Adjust the value to add spacing above the title

# Add a title
title_label = ctk.CTkLabel(app, text="FLUXESTER", font=("Arial", 23, "bold"), text_color="#FF5733")
title_label.pack(pady=20)

# Add the button to open files
open_file_button = ctk.CTkButton(app, text="Open File to Process", command=open_file, font=("Arial", 14))
open_file_button.pack(pady=40)

# Add a tooltip to the "Open File to Process" button
def add_tooltip(widget, text):
    tooltip = ctk.CTkLabel(app, text=text, fg_color="yellow", text_color="black", font=("Arial", 10))
    widget.bind("<Enter>", lambda e: tooltip.place(x=widget.winfo_x() + 50, y=widget.winfo_y() - 25))
    widget.bind("<Leave>", lambda e: tooltip.place_forget())

add_tooltip(open_file_button, "Select a TXT, CSV, or Excel file for processing")

# Add a frame as a background for the text
background_frame = ctk.CTkFrame(
    app, 
    corner_radius=10,  # Rounded corners
    fg_color="#e0f7fa"  # Light background color (adjust as desired)
)
background_frame.pack(pady=20, padx=20, fill="both")  # Adjust padding and expand to fit content

description_label = ctk.CTkLabel(
    background_frame,
    text=(
        "Author: Md Abdul Halim [2025]\n"
        "Licensed under: CC BY-NC 4.0\n"
        "Supported file types: TXT, CSV, and Excel\n"
        "Method details: https://doi.org/10.1016/j.scitotenv.2024.172666"
    ),
    font=("Arial", 12),
    justify="center",  # Center text alignment within the box
    anchor="center"   # Center text position
)
description_label.pack(pady=10, padx=10)  # Add internal padding for the label

# Run the application
if __name__ == "__main__":
    app.mainloop()

