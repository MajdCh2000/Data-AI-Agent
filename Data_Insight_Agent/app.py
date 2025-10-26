import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data_insight_agent import DataInsightAgent

st.set_page_config(page_title="Data Insight Agent", page_icon="📊", layout="centered")

st.title("📊 Data Insight Agent")
st.write("Upload a CSV file and let the agent automatically analyze it for key insights and trends.")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    with st.spinner("Analyzing your dataset..."):
        # Save uploaded file temporarily
        csv_path = "uploaded_data.csv"
        with open(csv_path, "wb") as f:
            f.write(uploaded_file.read())

        # Run the agent
        agent = DataInsightAgent(csv_path)
        result = agent.run()
        st.success("✅ Analysis complete!")

        # Load a sample dataframe for fallback calculations
        df = pd.read_csv(csv_path, nrows=1000)

        # -------------------------------
        # Basic Statistics
        # -------------------------------
        st.subheader("📋 Basic Statistics")
        stats = result.get("stats", {})

        # Rows and columns
        st.write(f"- **Rows:** {stats.get('rows', len(df))}")
        st.write(f"- **Columns:** {', '.join(stats.get('columns', df.columns.tolist()))}")

        # Date range
        if "date_range" in stats and stats["date_range"]:
            start_date = pd.to_datetime(stats['date_range'][0]).date()
            end_date = pd.to_datetime(stats['date_range'][1]).date()
            st.write(f"- **Date range:** {start_date} → {end_date}")
        else:
            datetime_cols = df.select_dtypes(include=["datetime", "object"]).columns.tolist()
            date_range_found = False
            for col in datetime_cols:
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                    if df[col].notnull().any():
                        start_date = df[col].min().date()
                        end_date = df[col].max().date()
                        st.write(f"- **Date range:** {start_date} → {end_date}")
                        date_range_found = True
                        break
                except Exception:
                    continue
            if not date_range_found:
                st.write("- **Date range:** Not available")

        # Total revenue
        if "total_revenue" in stats:
            st.write(f"- **Total revenue:** ${stats['total_revenue']:,.2f}")
        else:
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if numeric_cols:
                col = numeric_cols[0]
                st.write(f"- **Total revenue (approx):** ${df[col].sum():,.2f} (from column '{col}')")
            else:
                st.write("- **Total revenue:** Not available")

        # Top selling day
        if "top_selling_day" in stats:
            st.write(f"- **Top selling day:** {stats['top_selling_day']}")
        else:
            if datetime_cols and numeric_cols:
                df_grouped = df.groupby(df[datetime_cols[0]].dt.date)[numeric_cols[0]].sum()
                top_day = df_grouped.idxmax()
                st.write(f"- **Top selling day (approx):** {top_day}")
            else:
                st.write("- **Top selling day:** Not available")

        # -------------------------------
        # Visualizations
        # -------------------------------
        st.subheader("📈 Visualizations")
        for plot_path in result.get("plots", []):
            st.image(str(plot_path))

        # -------------------------------
        # Key Insights
        # -------------------------------
        st.subheader("💡 Key Insights")
        for ins in result.get("insights", []):
            answer = ins.get('answer', 'N/A')
            # Clean datetime formatting in answers
            if "→" in answer:
                parts = answer.split("→")
                try:
                    start = pd.to_datetime(parts[0].strip()).date()
                    end = pd.to_datetime(parts[1].strip()).date()
                    answer = f"{start} → {end}"
                except Exception:
                    pass
            st.markdown(f"**Q:** {ins.get('question', 'N/A')}  \n**A:** {answer}")

        # -------------------------------
        # Download Report
        # -------------------------------
        st.subheader("📂 Download Report")
        report_file = result.get("report_json")
        if report_file:
            with open(report_file, "rb") as f:
                st.download_button(
                    label="Download JSON Report",
                    data=f,
                    file_name="data_insight_report.json",
                    mime="application/json",
                )
        else:
            st.write("Report not available.")

        st.caption("Built by Majd Chantiri — Student Project on Agentic AI 🧠")

else:
    st.info("⬆️ Upload a CSV to begin analysis.")