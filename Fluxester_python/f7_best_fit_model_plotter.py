import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

# Define the nonlinear model function
def nonlinear_model(x,  C0, Cmax, k, t0):
    return Cmax + (C0 - Cmax) * np.exp(-k * (x - t0))

def plot_gas_with_best_window(selected_data, best_window_data, gas_col, slope, intercept, method, popt, ax):
    # Convert 'datetime' columns safely to pandas datetime format
    best_window_data = best_window_data.copy()
    best_window_data.loc[:, 'datetime'] = pd.to_datetime(best_window_data['datetime'])
    selected_data = selected_data.copy()
    selected_data.loc[:, 'datetime'] = pd.to_datetime(selected_data['datetime'])

    # Plot selected and best window data points
    ax.scatter(selected_data['datetime'], selected_data[gas_col], label='Data Points', color='grey')
    ax.scatter(best_window_data['datetime'], best_window_data[gas_col], label='Best Window', color='orange')

    # Plot fitted line based on method
    elapsed_time = (best_window_data['datetime'] - best_window_data['datetime'].min()).dt.total_seconds()
    # print("Elapsed time from plotter:", elapsed_time)
    
    try:
        if method == 'Nonlinear' and popt is not None:
            # print("popt plotter:", popt)
            # Nonlinear plot
            nonlinear_fitted_line = nonlinear_model(elapsed_time, *popt)
            ax.plot(best_window_data['datetime'], nonlinear_fitted_line, label='Best Fit (Nonlinear)', color='green')
        else:
            # Linear plot
            linear_fitted_line = slope * elapsed_time + intercept
            ax.plot(best_window_data['datetime'], linear_fitted_line, label='Best Fit (Linear)', color='blue')
    except Exception as e:
        print("An error occured:", e)
    
    # Apply formatting
    ax.set_title(f"{gas_col} Concentration")
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%y-%b-%d %H:%M:%S'))
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
