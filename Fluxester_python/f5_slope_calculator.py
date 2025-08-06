import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import linregress
import statsmodels.api as sm
from statsmodels.tools.sm_exceptions import PerfectSeparationError

def get_gas_threshold(gas_type, k_thresholds):
    """
    Get the threshold for a gas type with flexible matching.

    Parameters:
    gas_type (str): Input gas type, potentially with variations.
    k_thresholds (dict): Dictionary of thresholds for gas types.

    Returns:
    float: Threshold value for the matched gas type.
    """
    # Create a normalized mapping for flexible matching
    normalized_mapping = {
        'CO2': 'CO2', 'CO2_PPM': 'CO2', 'CO2_PPB': 'CO2', 'CO2_DRY': 'CO2', 
        'CO2_PPM_DRY': 'CO2', 'CO2_PPB_DRY': 'CO2',
        'CH4': 'CH4', 'CH4_PPM': 'CH4', 'CH4_PPB': 'CH4', 'CH4_DRY': 'CH4', 
        'CH4_PPM_DRY': 'CH4', 'CH4_PPB_DRY': 'CH4', 
        'H2O': 'H2O', 'H2O_PPM': 'H2O', 'H2O_PPB': 'H2O', 
        'N2O': 'N2O', 'N2O_PPM': 'N2O', 'N2O_PPB': 'N2O', 
        'N2O_PPB_DRY': 'N2O', 'N2O_PPM_DRY': 'N2O'
    }

    # Normalize the input gas type
    gas_type_normalized = gas_type.strip().upper()

    # Match the gas type to the normalized mapping
    standardized_gas_type = normalized_mapping.get(gas_type_normalized)

    if standardized_gas_type and standardized_gas_type in k_thresholds:
        return k_thresholds[standardized_gas_type]
    else:
        raise ValueError(
            f"Unrecognized gas type: {gas_type}. Valid types: {list(normalized_mapping.keys())}"
        )

def estimate_gas_slope(gas_concentration, datetime_data, gas_type):
    """
    Estimate the slope of gas concentration changes over time with calculated initial estimates.

    Parameters:
    gas_concentration (array-like): Array of gas concentration values.
    datetime_data (array-like): Array of datetime values corresponding to the concentration measurements.
    gas_type (str): Type of gas (e.g., 'CO2', 'CH4', 'H2O', 'N2O').

    Returns:
    tuple: Contains the slope, intercept (for linear models), p-value of the slope, method used ('Linear' or 'Nonlinear'), and model parameters.
    """
    # Convert datetime data to pandas datetime format and calculate elapsed time in seconds.
    datetime_data = pd.to_datetime(datetime_data)
    elapsed_time = (datetime_data - datetime_data.min()).dt.total_seconds()

    # Calculate C0 (initial concentration) from the intercept of the first 10 data points
    X_first_10 = sm.add_constant(elapsed_time[:10])
    Y_first_10 = gas_concentration[:10]
    linear_model_first_10 = sm.OLS(Y_first_10, X_first_10).fit()
    C0_initial_guess = linear_model_first_10.params.iloc[0]

    # Define the nonlinear model function
    def nonlinear_model(x, C0, Cmax, k, t0):
        """
        Nonlinear model for gas concentration changes over time.
        """
        exp_term = np.exp(-k * (x - t0))
        return Cmax + (C0 - Cmax) * exp_term

    # Prepare data for model fitting
    X = sm.add_constant(elapsed_time)
    Y = gas_concentration

    try:
        # Attempt polynomial fit
        X_poly = sm.add_constant(np.column_stack((elapsed_time, elapsed_time**2)))
        poly_results = sm.OLS(Y, X_poly).fit()
        p_value_poly_term = poly_results.pvalues[2]

        if p_value_poly_term < 0.05:
            # Non-linear model
            print("Im nonlinear")
            try:
                # Improved initial guesses
                Cmax_initial_guess = np.nanmax(Y)
                k_initial_guess = max(1e-6, 1 / (elapsed_time.max() - elapsed_time.min()))
                t0_initial_guess = elapsed_time.min()

                # Use curve_fit with bounds for stability
                popt, _ = curve_fit(
                    nonlinear_model,
                    elapsed_time,
                    Y,
                    p0=[C0_initial_guess, Cmax_initial_guess, k_initial_guess, t0_initial_guess],
                    bounds=(
                        [0, 0, 0, elapsed_time.min()],  # Lower bounds
                        [np.inf, np.inf, np.inf, elapsed_time.max()],  # Upper bounds
                    ),
                    maxfev=100000,  # Increase iterations for convergence
                    ftol=1e-6,  # Tighter tolerance
                    xtol=1e-6
                )

                # Extract parameters
                C0, Cmax, k_value, t0 = popt

                # Validate the fitted k_value against thresholds
                k_thresholds = {'CO2': 0.0082, 'CH4': 0.05, 'H2O': 0.5, 'N2O': 0.01}
                try:
                    # Get the threshold using the get_gas_threshold function
                    k_threshold = get_gas_threshold(gas_type, k_thresholds)
                except ValueError as e:
                    print(e)
                    return None, None, None, 'Error', None

                print(f"Gas Type: {gas_type}, Threshold: {k_threshold}")

                if k_value > k_threshold:
                    slope, intercept, r_value, p_value, std_err = linregress(elapsed_time, Y)
                    #print("Im here")
                    return slope, intercept, p_value, 'Linear', None
                else:
                    slope = k_value * (Cmax - C0)  # k * (Cmax - C0)
                    return slope, None, None, 'Nonlinear', popt

            except RuntimeError as e:
                print(f"Nonlinear model fitting failed: {e}")
                slope, intercept, r_value, p_value, std_err = linregress(elapsed_time, Y)
                return slope, intercept, p_value, 'Linear', None

        else:
            # If polynomial fit does not meet criteria, fallback to linear regression
            slope, intercept, r_value, p_value, std_err = linregress(elapsed_time, Y)
            return slope, intercept, p_value, 'Linear', None

    except (PerfectSeparationError, np.linalg.LinAlgError, RuntimeError) as e:
        print(f"Error during slope estimation: {e}")
        # Fallback to linear regression in case of exceptions
        try:
            slope, intercept, r_value, p_value, std_err = linregress(elapsed_time, Y)
            return slope, intercept, p_value, 'Linear', None
        except Exception as e:
            print(f"Linear regression failed: {e}")
            # In case linear regression also fails, return a placeholder
            return None, None, None, 'Error', None

    # Fallback return in case none of the above conditions are met
    return None, None, None, 'Unknown', None