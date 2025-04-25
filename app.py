import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import json
import matplotlib.pyplot as plt

st.set_page_config(page_title="Universal ETL Tool", layout="wide")
st.title("📊 Universal ETL Tool with Dashboard")

uploaded_file = st.file_uploader("📁 Upload your file", type=["csv", "xlsx", "json", "txt", "pdf"])

def read_file(file):
    try:
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        elif file.name.endswith(".xlsx"):
            return pd.read_excel(file)
        elif file.name.endswith(".json"):
            data = json.load(file)
            return pd.json_normalize(data)
        elif file.name.endswith(".txt"):
            content = file.read().decode("utf-8")
            return pd.DataFrame({"Text": content.splitlines()})
        elif file.name.endswith(".pdf"):
            doc = fitz.open(stream=file.read(), filetype="pdf")
            text = "\n".join([page.get_text() for page in doc])
            return pd.DataFrame({"PDF Text": text.split("\n")})
    except Exception as e:
        st.error(f"Error reading file: {e}")
    return None

if uploaded_file is not None:
    df = read_file(uploaded_file)

    if df is not None:
        st.success("✅ File uploaded and processed successfully!")
        st.subheader("📄 Preview of Data")
        st.dataframe(df.head())

        # Download button
        st.download_button("⬇️ Download as CSV", df.to_csv(index=False), file_name="extracted_data.csv")

        # Dashboard section
        st.subheader("📈 Dashboard & Insights")

        # Show basic stats
        with st.expander("🔍 Data Summary"):
            st.write(df.describe(include='all').transpose())

        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns

        if not numeric_cols.empty:
            st.markdown("### 📊 Line Chart for Numeric Columns")
            selected_num = st.selectbox("Select numeric column:", numeric_cols)
            st.line_chart(df[selected_num])

        if not categorical_cols.empty:
            st.markdown("### 🧱 Bar Chart for Categorical Columns")
            selected_cat = st.selectbox("Select categorical column:", categorical_cols)
            st.bar_chart(df[selected_cat].value_counts())

        # Optional: Add pie chart
        if not categorical_cols.empty:
            st.markdown("### 🥧 Pie Chart (Top 5 Categories)")
            top_5 = df[selected_cat].value_counts().head(5)
            fig, ax = plt.subplots()
            ax.pie(top_5, labels=top_5.index, autopct='%1.1f%%')
            ax.axis('equal')
            st.pyplot(fig)
