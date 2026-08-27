import streamlit as st
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Loblaw Bio Trial Dashboard", layout="wide")

def load_data(query):
    conn = sqlite3.connect("immune_trial.db")
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("Loblaw Bio: Immune Cell Population Dashboard")
st.markdown("Interactive analysis of clinical trial cell counts and treatment responses.")

## --- Part 2: Data Overview ---
st.header("1. Initial Analysis: Cell Frequency Overview")
frequency_query = """
    SELECT sample, population, count 
    FROM cell_counts
"""
df_freq = load_data(frequency_query)
df_freq['total_count'] = df_freq.groupby('sample')['count'].transform('sum')
df_freq['percentage'] = (df_freq['count'] / df_freq['total_count']) * 100
summary_df = df_freq[['sample', 'total_count', 'population', 'count', 'percentage']].sort_values(by=['sample', 'population'])

st.dataframe(summary_df, use_container_width=True)

## --- Part 3: Statistical Analysis ---
st.header("2. Treatment Response: Miraclib (Melanoma PBMC)")
stats_query = """
    SELECT s.sample, sub.response, c.population, c.count
    FROM samples s
    JOIN subjects sub ON s.subject = sub.subject
    JOIN cell_counts c ON s.sample = c.sample
    WHERE sub.condition = 'melanoma' AND sub.treatment = 'miraclib' AND s.sample_type = 'PBMC' AND sub.response IN ('yes', 'no')
"""
df_stats = load_data(stats_query)
df_stats['total_count'] = df_stats.groupby('sample')['count'].transform('sum')
df_stats['percentage'] = (df_stats['count'] / df_stats['total_count']) * 100

fig, ax = plt.subplots(figsize=(10, 5))
sns.boxplot(data=df_stats, x='population', y='percentage', hue='response', palette={'yes': '#2ca02c', 'no': '#d62728'}, ax=ax)
ax.set_title("Immune Cell Relative Frequencies: Responders vs. Non-Responders")
ax.set_ylabel("Relative Frequency (%)")
st.pyplot(fig)

## --- Part 4: Data Subset Analysis ---
st.header("3. Baseline Subset Analysis (Time = 0)")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Baseline Melanoma PBMC (Miraclib)")
    baseline_query = """
        SELECT s.sample, sub.subject, sub.project, sub.response, sub.sex
        FROM samples s
        JOIN subjects sub ON s.subject = sub.subject
        WHERE sub.condition = 'melanoma' AND sub.treatment = 'miraclib' AND s.sample_type = 'PBMC' AND s.time_from_treatment_start = 0
    """
    df_base = load_data(baseline_query)
    st.write("**Samples per Project:**", df_base['project'].value_counts().to_dict())
    
    unique_subs = df_base.drop_duplicates(subset=['subject'])
    st.write("**Subjects by Response:**", unique_subs['response'].value_counts().to_dict())
    st.write("**Subjects by Sex:**", unique_subs['sex'].value_counts().to_dict())

with col2:
    st.subheader("Targeted Biomarker")
    bcell_query = """
        SELECT c.count FROM samples s
        JOIN subjects sub ON s.subject = sub.subject
        JOIN cell_counts c ON s.sample = c.sample
        WHERE sub.condition = 'melanoma' AND sub.sex = 'M' AND sub.response = 'yes' AND s.time_from_treatment_start = 0 AND c.population = 'b_cell'
    """
    df_bcell = load_data(bcell_query)
    avg_b = df_bcell['count'].mean()
    st.metric(label="Avg B-Cells (Melanoma Males, Responders, t=0)", value=f"{avg_b:.2f}")