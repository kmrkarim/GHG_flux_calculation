
import matplotlib
matplotlib.use('TkAgg')
import os
#matplotlib.use('gtk3agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from matplotlib.widgets import RectangleSelector, Button
from matplotlib.dates import num2date, DateFormatter, AutoDateLocator
import pandas as pd
import numpy as np
from tkinter import messagebox
import pytz
from f4_moving_window_selector import find_best_moving_window, get_user_window_size
from f5_slope_calculator import estimate_gas_slope
from f6_window_stats_calculator import calculate_window_statistics
from f7_best_fit_model_plotter import plot_gas_with_best_window


# Initialize a set to store indices of selected data points and a variable for the Axes object
selected_indices = set()
ax = None

def apply_date_formatting():
    """
    Apply date formatting to the x-axis of the plot.
    This function sets the date format and tick parameters for the x-axis.
    """
    ax.xaxis.set_major_formatter(DateFormatter('%y-%b-%d %H:%M:%S')) # Set date-time format
    ax.xaxis.set_major_locator(AutoDateLocator()) # Automatic tick locator
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")  # # Rotate x-axis labels for better readability and ensure labels are rotated
    ax.tick_params(axis='x', labelsize=9) # Set font size for x-axis labels

# Declare global variables for the DataFrame and the RectangleSelector
global df, rect_selector

# Other global variables to store the names of gas columns and dead band value
global co2_col_name, ch4_col_name, h2o_col_name, n2o_col_name, dead_band_value

def process_columns(df_param, date_col, time_col, y_axis_col, co2_col, ch4_col, h2o_col, n2o_col, dead_band):
    """
    Process the DataFrame columns and set up the initial plot.

    Args:
    df_param (DataFrame): The DataFrame containing the data to plot.
    date_col (str): The name of the column containing date information.
    time_col (str): The name of the column containing time information.
    y_axis_col (str): The name of the column to plot on the y-axis.
    co2_col (str): The name of the CO2 column.
    ch4_col (str): The name of the CH4 column.
    h2o_col (str): The name of the H2O column.
    n2o_col (str): The name of the N2O column.
    dead_band (int): The dead band value for slope calculation.
    """
    global ax, selected_indices, y_axis_col_name, df, rect_selector
    global co2_col_name, ch4_col_name, h2o_col_name, n2o_col_name, dead_band_value

    # Update the global variables with the parameters passed to the function
    y_axis_col_name, co2_col_name, ch4_col_name, h2o_col_name, n2o_col_name, dead_band_value = y_axis_col, co2_col, ch4_col, h2o_col, n2o_col, dead_band
    df = df_param

    # Convert date and time columns to a datetime format and create a figure and axes
    df['datetime'] = pd.to_datetime(df[date_col] + ' ' + df[time_col])
    fig, ax = plt.subplots(figsize=(10, 6))

    # Scatter plot with custom style
    ax.scatter(df['datetime'], df[y_axis_col], 
               color='black', edgecolor='white', s=30, linewidth=0.5)

    # Apply date formatting to the x-axis initially
    apply_date_formatting()  

    # Increase bottom padding for better label display
    plt.subplots_adjust(bottom=0.15)

    # Set the x-axis limits based on the datetime range
    min_date, max_date = df['datetime'].min(), df['datetime'].max()
    range_extension = (max_date - min_date) * 0.05
    ax.set_xlim(min_date - range_extension, max_date + range_extension)

    # Initialize the RectangleSelector for selecting data points
    rect_selector = RectangleSelector(ax, onselect, useblit=True, interactive=True)

    # Setup a button for saving selected data
    button_ax = fig.add_axes([0.875, 0.01, 0.11, 0.05])  # Button position and size
    button = Button(button_ax, 'Save Selection', color='lightblue', hovercolor='blue')
    button.on_clicked(submit_selection)

    # Attach the event handler
    button.on_clicked(submit_selection)

    # Connect the on_draw event to reapply date formatting when the plot is redrawn
    fig.canvas.mpl_connect('draw_event', lambda event: apply_date_formatting())

    plt.show()  # Display the plot



def onselect(eclick, erelease):
    """
    Handle the event when a rectangular selection is made on the plot.
    This function updates the set of selected indices based on the selection.
    """
    global df, selected_indices, y_axis_col_name

    # Clear previous selection if this is a new selection (not a double-click)
    if not eclick.dblclick:
        selected_indices.clear()

    # Convert mouse click and release positions to datetime values
    x1, x2 = num2date(eclick.xdata), num2date(erelease.xdata)
    # Adjust for timezone if necessary
    x1 = x1.replace(tzinfo=None)
    x2 = x2.replace(tzinfo=None)

    # Identify and update the indices of the selected data points
    selected = df[(df['datetime'] >= min(x1, x2)) & (df['datetime'] <= max(x1, x2)) &
                  (df[y_axis_col_name] >= eclick.ydata) & (df[y_axis_col_name] <= erelease.ydata)]
    selected_indices.update(selected.index)
    update_plot()  # Update the plot with the new selection



def update_plot():
    """
    Update the plot to reflect changes, such as new data point selections.
    """
    global ax, selected_indices

    # Save the current zoom level and plot position
    x_lim = ax.get_xlim()
    y_lim = ax.get_ylim()

    # Clear the axes and redraw the scatter plot with the updated selection
    ax.clear()
    xdata, ydata = df['datetime'], df[y_axis_col_name]
    colors = ['#006400' if i in selected_indices else 'black' for i in range(len(xdata))]
    ax.scatter(xdata, ydata, color=colors, edgecolor='white', s=30, linewidth=0.5)

    apply_date_formatting()  # Reapply date formatting

    # Restore the zoom level and plot position
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)

    plt.subplots_adjust(bottom=0.15)
    plt.draw()  # Redraw the updated plot



def process_and_visualize_data():
    """
    Process selected data and apply slope calculation, window statistics, and visualization.
    """
    global selected_indices, df, co2_col_name, ch4_col_name, h2o_col_name, n2o_col_name, dead_band_value, y_axis_col_name

    DEFAULT_MOVING_WINDOW_SIZE = 35  # Default moving window size
    response = messagebox.askquestion(
        'Set Moving Window Size',
        f'The default moving window size is {DEFAULT_MOVING_WINDOW_SIZE}. Do you want to proceed with this size?'
    )
    if response != 'yes':
        new_window_size = get_user_window_size(DEFAULT_MOVING_WINDOW_SIZE)
        if new_window_size is None:
            messagebox.showinfo('Process Terminated', 'Process terminated by user.')
            return
        else:
            DEFAULT_MOVING_WINDOW_SIZE = new_window_size  # Update the window size

    if selected_indices:
        selected_indices_list = list(selected_indices)
        selected_data = df.loc[selected_indices_list]

        # Adjust for dead band
        dead_band = int(dead_band_value)
        if len(selected_data) > dead_band + DEFAULT_MOVING_WINDOW_SIZE:
            data_after_dead_band = selected_data.iloc[dead_band:]
            best_window_data = find_best_moving_window(
                data_after_dead_band, DEFAULT_MOVING_WINDOW_SIZE, 'datetime', y_axis_col_name
            )

            # Define the time range for the best window
            start_datetime = best_window_data['datetime'].iloc[0]
            end_datetime = best_window_data['datetime'].iloc[-1]

            # Generate datetime strings for filenames
            start_datetime_str = start_datetime.strftime('%Y%m%d%H%M%S')
            end_datetime_str = end_datetime.strftime('%Y%m%d%H%M%S')

            summary = {}
            fig, axs = plt.subplots(len([co2_col_name, ch4_col_name, h2o_col_name, n2o_col_name]), figsize=(10, 12))

            # Loop through each gas column
            for i, gas_col in enumerate([co2_col_name, ch4_col_name, h2o_col_name, n2o_col_name]):
                if gas_col and gas_col in best_window_data.columns:
                    gas_concentration = best_window_data[gas_col].to_numpy()
                    slope, intercept, p_value, method, popt = estimate_gas_slope(
                        gas_concentration, best_window_data['datetime'], gas_col
                    )

                    # Update the summary dictionary
                    summary[f"{gas_col}_slope"] = slope
                    summary[f"{gas_col}_p_value"] = p_value
                    summary[f"{gas_col}_method"] = method

                    # Plot the data
                    plot_gas_with_best_window(selected_data, best_window_data, gas_col, slope, intercept, method, popt, axs[i])
                    axs[i].set_ylabel(f"{gas_col} Concentration")
                    axs[i].title.set_text(None)

                    # Show x-axis tick labels only on the last graph
                    if i != len([co2_col_name, ch4_col_name, h2o_col_name, n2o_col_name]) - 1:
                        axs[i].set_xticklabels([])

            # Adjust layout and save the figure
            plt.tight_layout(pad=3.0)
            output_folder = "./data"
            os.makedirs(output_folder, exist_ok=True)
            fig.savefig(f"{output_folder}/{start_datetime_str}_to_{end_datetime_str}_gases.png")

            # Handle additional columns
            for col in best_window_data.columns:
                if col not in [co2_col_name, ch4_col_name, h2o_col_name, n2o_col_name, 'datetime']:
                    if pd.api.types.is_numeric_dtype(best_window_data[col]):
                        summary[col] = best_window_data[col].mean(skipna=True)
                    elif pd.api.types.is_categorical_dtype(best_window_data[col]) or pd.api.types.is_object_dtype(best_window_data[col]):
                        summary[col] = best_window_data[col].iloc[0]

            # Save the summary
            summary_df = pd.DataFrame([summary])
            summary_csv_path = f"{output_folder}/{start_datetime_str}_to_{end_datetime_str}_summary.csv"
            summary_df.to_csv(summary_csv_path, index=False)
            messagebox.showinfo("Info", f"Slope, summary stats, and figures saved in {output_folder}")
        else:
            messagebox.showwarning("Warning", "Insufficient data points after applying dead band for the moving window.")
    else:
        messagebox.showwarning("Warning", "No data points selected.")

        
def submit_selection(event):
    """
    Handle the event when the 'Save Selection' button is clicked.
    This function saves the selected data and resets the RectangleSelector.
    """
    global rect_selector
    process_and_visualize_data()  # Save the selected data

    # Reset the RectangleSelector for a new selection
    rect_selector.set_active(False)
    rect_selector = RectangleSelector(ax, onselect, useblit=True, interactive=True)



def on_draw(event):
    """
    Handle the draw event on the plot.
    This function reapplies the date formatting every time the plot is redrawn.
    """
    apply_date_formatting()
