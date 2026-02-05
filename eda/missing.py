def missing_values(df):
    """
    Returns count of missing values per column
    """
    return df.isnull().sum()
