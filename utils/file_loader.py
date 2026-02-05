import pandas as pd

def load_file(uploaded_file):
    """
    Detects file type and loads data accordingly
    """
    file_name = uploaded_file.name

    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        return df, "csv"

    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
        return df, "excel"

    else:
        return None, None
