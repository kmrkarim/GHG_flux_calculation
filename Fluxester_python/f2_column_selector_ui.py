import customtkinter as ctk
import os


class CustomMessageBox:
    def __init__(self, title, message):
        self.root = ctk.CTkToplevel()
        self.root.title(title)
        self.root.geometry("300x150")
        self.root.grab_set()

        label = ctk.CTkLabel(self.root, text=message, wraplength=250)
        label.pack(pady=20)

        button = ctk.CTkButton(self.root, text="OK", command=self.root.destroy)
        button.pack(pady=10)


# Constant to store the path of the file where previous column selections are saved.
SELECTIONS_FILE = 'column_selections.txt'

def save_column_selections(date_col, time_col, y_axis_col, co2_col, ch4_col, h2o_col, n2o_col, dead_band):
    """
    Saves the selected column names and dead band value to a file.
    """
    with open(SELECTIONS_FILE, 'w') as file:
        file.write(f"{date_col}\n{time_col}\n{y_axis_col}\n{co2_col}\n{ch4_col}\n{h2o_col}\n{n2o_col}\n{dead_band}")

def load_previous_selections():
    """
    Loads previously saved column selections and dead band value from a file.
    """
    if os.path.exists(SELECTIONS_FILE):
        with open(SELECTIONS_FILE, 'r') as file:
            selections = file.read().splitlines()
            return selections + [None] * (8 - len(selections))
    return [None] * 8

def create_column_selection_ui(df, callback):
    """
    Creates a user interface for selecting columns and a dead band value using customtkinter.
    """
    def on_submit():
        selections = [var.get() for var in vars]
        for col in selections[:-1]:
            if col not in df.columns and col != 'None':
                CustomMessageBox(title="Error", message=f"Column '{col}' does not exist in the dataset.")
                return

        dead_band = selections[-1]
        if not dead_band.isdigit() or not (0 <= int(dead_band) <= 60):
            CustomMessageBox(title="Error", message="Dead band must be an integer between 0 and 60.")
            return

        save_column_selections(*selections)
        root.destroy()
        callback(df, *selections)

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Select Columns & Dead Band")
    root.geometry('400x450')

    prev_selections = load_previous_selections()
    labels = ["Date column (YYYY-MM-DD)", "Time column (24HR:MM:SS)", "Y-variable column", "CO2 column", "CH4 column", "H2O-vapor column", "N2O column", "Dead Band (0-60)"]
    vars = [ctk.StringVar(value=val or 'None') for val in prev_selections]

    for label, var in zip(labels, vars):
        frame = ctk.CTkFrame(root)
        frame.pack(fill='x', padx=10, pady=5)

        ctk.CTkLabel(frame, text=label, width=200, anchor='w').pack(side='left', padx=5)
        
        if label == "Dead Band (0-60)":
            ctk.CTkEntry(frame, textvariable=var, width=150).pack(side='right', padx=5)
        else:
            ctk.CTkOptionMenu(frame, variable=var, values=['None'] + list(df.columns)).pack(side='right', padx=5, expand=True)

    submit_button = ctk.CTkButton(root, text="Submit", command=on_submit)
    submit_button.pack(pady=20)

    root.mainloop()