import sqlite3
import pandas as pd

def get_frequency_summary(db_path="immune_trial.db"):
    """
    Connects to the SQLite database, calculates the relative frequency of each 
    cell population per sample, and returns a formatted summary DataFrame.
    """
    conn = sqlite3.connect(db_path)
    query = "SELECT sample, population, count FROM cell_counts"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    ## calculate the percentage of count per sample
    df['total_count'] = df.groupby('sample')['count'].transform('sum')
    df['percentage'] = (df['count'] / df['total_count']) * 100
    
    ## summarize everything
    summary_df = df[['sample', 'total_count', 'population', 'count', 'percentage']]
    summary_df = summary_df.sort_values(by=['sample', 'population']).reset_index(drop=True)
    
    return summary_df

if __name__ == "__main__":
    summary_table = get_frequency_summary()
    
    print("Part 2: Initial Analysis - Data Overview")
    print(summary_table.head(15).to_string(index=False))