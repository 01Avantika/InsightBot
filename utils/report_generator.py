def generate_report(summary, missing, stats):
    report = []

    report.append("EDA REPORT\n")
    report.append("\n--- DATA SUMMARY ---\n")
    report.append(summary.to_string())

    report.append("\n\n--- MISSING VALUES ---\n")
    report.append(missing.to_string())

    report.append("\n\n--- STATISTICAL INSIGHTS ---\n")
    for col, val in stats.items():
        report.append(f"{col}: Mean={val['mean']}, Std={val['std']}")

    return "\n".join(report)
