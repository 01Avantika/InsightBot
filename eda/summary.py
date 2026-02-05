def generate_summary(df):
    """
    Generates descriptive statistics for the dataset
    """
    return df.describe(include="all")
