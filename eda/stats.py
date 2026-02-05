def numeric_stats(df):
    """
    Calculates mean, standard deviation, and skewness
    for numeric columns
    """
    stats = {}

    numeric_cols = df.select_dtypes(include="number").columns

    for col in numeric_cols:
        stats[col] = {
            "mean": df[col].mean(),
            "std": df[col].std(),
            "skew": df[col].skew()
        }

    return stats
