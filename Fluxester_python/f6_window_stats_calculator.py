def calculate_window_statistics(window, gas_columns, time_col, other_cols):
    """
    Calculates statistics (slope, mean, etc.) for the specified window of data.

    Args:
        window (DataFrame): The data window to calculate statistics for.
        gas_columns (list): List of gas column names to calculate slopes.
        time_col (str): The name of the time column.
        other_cols (list): List of other columns to calculate means.

    Returns:
        dict: A dictionary containing calculated statistics.
    """
    summary = {}
    start_datetime = window[time_col].iloc[0]
    numeric_dates = (window[time_col] - start_datetime).dt.total_seconds()

    # Calculate slopes for gas columns
    for gas_col in gas_columns:
        if gas_col in window.columns:
            y_values = window[gas_col].to_numpy()
            summary[f"{gas_col}_slope"] = calculate_slope(y_values, numeric_dates)

    # Calculate mean or representative value for other columns
    for col in other_cols:
        if col in window.columns:
            if pd.api.types.is_numeric_dtype(window[col]):
                summary[col] = window[col].mean(skipna=True)
            elif pd.api.types.is_categorical_dtype(window[col]) or pd.api.types.is_object_dtype(window[col]):
                summary[col] = window[col].iloc[0]

    return summary
