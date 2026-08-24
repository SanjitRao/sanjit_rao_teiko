import sqlite3
import pandas as pd
import os
import sys

def load_data():
    csv_file = "cell-count.csv"
    db_name = "immune_trial.db"

    if not os.path.exists(csv_file):
        print(f"Error: '{csv_file}' not found in the current directory.")
        sys.exit(1)

    df = pd.read_csv(csv_file)

    ## renamed for convenience
    rename_map = {'sample_id': 'sample', 'indication': 'condition','gender': 'sex'}
    df.rename(columns=rename_map, inplace=True)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    ## define relational schema
    cursor.executescript('''
        DROP TABLE IF EXISTS cell_counts;
        DROP TABLE IF EXISTS samples;
        DROP TABLE IF EXISTS subjects;

        -- Table 1: Static patient metadata
        CREATE TABLE subjects (
            subject TEXT PRIMARY KEY,
            project TEXT,
            condition TEXT,
            age REAL,
            sex TEXT,
            treatment TEXT,
            response TEXT
        );

        -- Table 2: Longitudinal sample collection metadata
        CREATE TABLE samples (
            sample TEXT PRIMARY KEY,
            subject TEXT,
            sample_type TEXT,
            time_from_treatment_start REAL,
            FOREIGN KEY (subject) REFERENCES subjects (subject)
        );

        -- Table 3: Unpivoted cell population counts
        CREATE TABLE cell_counts (
            sample TEXT,
            population TEXT,
            count REAL,
            PRIMARY KEY (sample, population),
            FOREIGN KEY (sample) REFERENCES samples (sample)
        );
    ''')

    subject_cols = ['subject', 'project', 'condition', 'age', 'sex', 'treatment', 'response']
    avail_subject_cols = [c for c in subject_cols if c in df.columns]
    subjects_df = df[avail_subject_cols].drop_duplicates(subset=['subject'])
    subjects_df.to_sql('subjects', conn, if_exists='append', index=False)

    sample_cols = ['sample', 'subject', 'sample_type', 'time_from_treatment_start']
    avail_sample_cols = [c for c in sample_cols if c in df.columns]
    samples_df = df[avail_sample_cols].drop_duplicates(subset=['sample'])
    samples_df.to_sql('samples', conn, if_exists='append', index=False)

    populations = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
    avail_pops = [c for c in populations if c in df.columns]
    
    cell_counts_df = df.melt(id_vars=['sample'], value_vars=avail_pops, var_name='population', value_name='count')
    
    ## drop rows where a count might be missing, then load
    cell_counts_df = cell_counts_df.dropna(subset=['count'])
    cell_counts_df.to_sql('cell_counts', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()
    
    print(f"Data loaded into {db_name}")

if __name__ == "__main__":
    load_data()