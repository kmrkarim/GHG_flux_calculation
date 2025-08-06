import numpy as np
from scipy.stats import pearsonr
import tkinter as tk
from tkinter import simpledialog, messagebox


def get_user_window_size(default_size):
    """
    Prompts the user to input a revised window size or opt out.

    Args:
        default_size (int): The default window size to suggest.

    Returns:
        int or None: The user's chosen window size, or None if they opt out.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Ask the user for a revised window size
    user_input = simpledialog.askinteger("Window Size Adjustment", 
                                         "Data size is smaller than the moving window size.\n"
                                         "Please enter a revised window size:",
                                         initialvalue=default_size,
                                         minvalue=1,
                                         maxvalue=default_size)

    root.destroy()
    return user_input



def find_best_moving_window(data, window_size, time_col, y_axis_col):
    """
    Finds the best moving window in the dataset based on the highest correlation coefficient.

    Args:
        data (DataFrame): The data to search for the best window.
        window_size (int): The size of the moving window.
        time_col (str): The name of the time column.
        y_axis_col (str): The name of the Y-axis column.

    Returns:
        DataFrame: The subset of data corresponding to the best window.
    """
    
    if len(data) < window_size:
        # Prompt the user for a revised window size
        new_window_size = get_user_window_size(len(data))

        if new_window_size is None:
            messagebox.showinfo("Process Terminated", "Moving window process terminated by user.")
            return None
        else:
            window_size = new_window_size
    
    best_window_start = 0
    best_correlation = float('-inf')

    # Convert datetime to numeric for correlation calculation
    numeric_dates = (data[time_col] - data[time_col].iloc[0]).dt.total_seconds()

    for start in range(len(data) - window_size + 1):
        window = data.iloc[start:start + window_size]
        numeric_dates_window = numeric_dates[start:start + window_size]

        # Calculate the Pearson correlation coefficient
        correlation, _ = pearsonr(numeric_dates_window, window[y_axis_col])

        if correlation > best_correlation:
            best_correlation = correlation
            best_window_start = start

    return data.iloc[best_window_start:best_window_start + window_size]
