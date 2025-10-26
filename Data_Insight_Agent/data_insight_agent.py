import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
import numpy as np

class DataInsightAgent:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)

    def run(self):
        df = pd.read_csv(self.csv_path)
        df = df.dropna(how="all")

        # Basic info
        stats = {
            "rows": len(df),
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
        }

        # Detect column types
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        date_cols = [col for col in df.columns if "date" in col.lower()]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors="coerce")

        # --- Visualizations ---
        plots = []

        # Histogram for numeric columns
        for col in numeric_cols[:3]:
            plt.figure(figsize=(6, 4))
            sns.histplot(df[col].dropna(), kde=True, color="skyblue")
            plt.title(f"Distribution of {col}")
            path = self.output_dir / f"hist_{col}.png"
            plt.tight_layout()
            plt.savefig(path)
            plt.close()
            plots.append(path)


        # Correlation heatmap
        if len(numeric_cols) > 1:
            plt.figure(figsize=(6, 4))
            corr = df[numeric_cols].corr()
            sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
            plt.title("Correlation Heatmap")
            path = self.output_dir / "correlation_heatmap.png"
            plt.tight_layout()
            plt.savefig(path)
            plt.close()
            plots.append(path)

        # --- Generate Insights ---
        insights = []
        if numeric_cols:
            for col in numeric_cols:
                mean_val = df[col].mean()
                median_val = df[col].median()
                max_val = df[col].max()
                min_val = df[col].min()
                insights.append({
                    "question": f"What are the key stats for {col}?",
                    "answer": f"Mean = {mean_val:.2f}, Median = {median_val:.2f}, Min = {min_val:.2f}, Max = {max_val:.2f}"
                })

        if categorical_cols:
            #top_cat = df[categorical_cols[0]].value_counts().idxmax()
            #insights.append({
            #    "question": f"What’s the most frequent value in {categorical_cols[0]}?",
            #    "answer": f"{top_cat}"
            top_cat = df[categorical_cols[0]].value_counts().idxmax()
            # Convert datetime to date if necessary
            if pd.api.types.is_datetime64_any_dtype(df[categorical_cols[0]]):
                top_cat = pd.to_datetime(top_cat).date()
            insights.append({
                "question": f"What is the most frequent value in {categorical_cols[0]}?",
                "answer": f"{top_cat}"
            })
            

        if date_cols:
            insights.append({
                "question": "What’s the date range in your dataset?",
                "answer": f"{df[date_cols[0]].min()} → {df[date_cols[0]].max()}"
            })

        # Save report
        report_json = self.output_dir / "report.json"
        with open(report_json, "w") as f:
            json.dump({"stats": stats, "insights": insights}, f, indent=2)

        return {"stats": stats, "plots": plots, "insights": insights, "report_json": report_json}