def explain_stats(stats):
    explanations = []

    for col, values in stats.items():
        explanations.append(
            f"• The average value of '{col}' is {round(values['mean'], 2)}, "
            f"with variability (std deviation) of {round(values['std'], 2)}."
        )

        if values["skew"] > 1:
            explanations.append(
                f"• '{col}' is right-skewed, meaning higher values are less frequent."
            )
        elif values["skew"] < -1:
            explanations.append(
                f"• '{col}' is left-skewed, meaning lower values are less frequent."
            )
        else:
            explanations.append(
                f"• '{col}' is approximately normally distributed."
            )

    return explanations
