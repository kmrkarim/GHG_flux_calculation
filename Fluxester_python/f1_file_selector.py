# Importing necessary libraries
import os
import tkinter as tk  # Tkinter is used for creating GUI elements
from tkinter import filedialog, messagebox  # Importing specific modules for file dialog and message boxes

# Function to retrieve the last directory used by the application
def get_last_directory():
    """
    Attempts to read a file named 'last_directory.txt' to get the last accessed directory.

    This function is helpful for enhancing user experience by opening the file dialog in the 
    previously used directory, making file navigation easier for the user.

    Returns:
        str: The path of the last accessed directory. Returns None if the file doesn't exist or can't be read.
    """
    try:
        # Opening the file in read mode
        with open('last_directory.txt', 'r') as file:
            return file.read().strip()  # Reads and returns the directory path, stripping any leading/trailing whitespace
    except FileNotFoundError:  # Exception handling for cases where 'last_directory.txt' does not exist
        return None

# Function to select a CSV file using a file dialog
def select_file():
    """
    Presents a file dialog to the user for selecting a CSV file. This function is designed to be user-friendly,
    starting the file dialog in the last used directory, and updating that directory upon file selection.

    Tkinter's root window is initialized but kept hidden (withdrawn) to avoid showing an empty window.

    Returns:
        str: The full path of the selected CSV file, or None if no file is selected.
    """
    root = tk.Tk()  # Creating a root window using Tkinter
    root.withdraw()  # Hides the root window, as we only need the file dialog

    # Retrieve the last opened directory or use the current working directory as a fallback
    initial_dir = get_last_directory() or os.getcwd()

    # Opening a file dialog for the user to select a CSV file
    file_path = filedialog.askopenfilename(
        initialdir=initial_dir,  # Sets the starting directory of the file dialog
        title="Select a CSV File",  # Title of the file dialog window
        filetypes=[("CSV files", "*.csv")]  # Restricts the selection to CSV files only
    )

    if file_path:
        # If a file is selected, save the directory of the selected file
        directory = os.path.dirname(file_path)  # Extracts the directory part of the file path
        with open('last_directory.txt', 'w') as file:  # Opens 'last_directory.txt' in write mode
            file.write(directory)  # Writes the directory to the file

        return file_path  # Returns the path of the selected file

    return None  # Returns None if no file is selected
