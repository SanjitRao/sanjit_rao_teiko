import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

def run_statistical_analysis(db_path="immune_trial.db"):
    """
    Filters for PBMC samples from melanoma patients on miraclib, compares 
    responders vs non-responders, generates a boxplot, and reports statistics.
    """
    conn = sqlite3.connect(db_path)

    ## build query
    query = """
        SELECT 
            s.sample,
            sub.response,
            c.population,
            c.count
        FROM samples s
        JOIN subjects sub ON s.subject = sub.subject
        JOIN cell_counts c ON s.sample = c.sample
        WHERE sub.condition = 'melanoma' 
          AND sub.treatment = 'miraclib'
          AND s.sample_type = 'PBMC'
          AND sub.response IN ('yes', 'no')
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    ## calculate relative frequencies
    df['total_count'] = df.groupby('sample')['count'].transform('sum')
    df['percentage'] = (df['count'] / df['total_count']) * 100


    ## begin the statistical testing
    populations = df['population'].unique()
    stats_results = []
    
    for pop in populations:
        pop_data = df[df['population'] == pop]
        
        ## find percent of responders vs non-responders
        responders = pop_data[pop_data['response'] == 'yes']['percentage']
        non_responders = pop_data[pop_data['response'] == 'no']['percentage']
        
        ## calculate stats
        stat, p_val = mannwhitneyu(responders, non_responders, alternative='two-sided')
        is_significant = "Yes" if p_val < 0.05 else "No"
        
        stats_results.append({'Population': pop,'P-Value': p_val,'Significant (p < 0.05)': is_significant})

    ## build stats dataframe and plot
    stats_df = pd.DataFrame(stats_results)

    plt.figure(figsize=(12, 7))
    sns.boxplot(data=df, x='population', y='percentage', hue='response', palette={'yes': '#2ca02c', 'no': '#d62728'})
    
    plt.title('Immune Cell Relative Frequencies: Responders vs. Non-Responders\n(Melanoma | Miraclib | PBMC)', fontsize=14)
    plt.xlabel('Cell Population', fontsize=12)
    plt.ylabel('Relative Frequency (%)', fontsize=12)
    plt.legend(title='Response')
    plt.tight_layout()

    plot_filename = "part3_boxplot.png"
    plt.savefig(plot_filename)
    
    return stats_df, plot_filename

if __name__ == "__main__":
    print("Part 3: Statistical Analysis")

    results_df, plot_path = run_statistical_analysis()
    print("Statistical Findings (Mann-Whitney U Test):")
    print(results_df.to_string(index=False))
    

    significant_pops = results_df[results_df['Significant (p < 0.05)'] == 'Yes']['Population'].tolist()

    ## verbose explanation of Part 3 results
    if significant_pops:
        print(f"There is a statistically significant difference in relative frequencies between responders and non-responders for the following populations: {', '.join(significant_pops)}")
    else:
        print("No statistically significant differences ($p < 0.05$) were found between responders and non-responders across any cell population.")
        
    print(f"\nBoxplot visualization saved to '{plot_path}'.")