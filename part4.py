import sqlite3
import pandas as pd

def run_subset_analysis(db_path="immune_trial.db"):
    """
    Queries specific data subsets to evaluate baseline treatment effects and 
    specific patient demographics.
    """
    conn = sqlite3.connect(db_path)
    

    ## query A: baseline melanoma PBMC treated w/ miraclib
    query_a = """
        SELECT 
            s.sample,
            sub.subject,
            sub.project,
            sub.response,
            sub.sex
        FROM samples s
        JOIN subjects sub ON s.subject = sub.subject
        WHERE sub.condition = 'melanoma' 
          AND sub.treatment = 'miraclib'
          AND s.sample_type = 'PBMC'
          AND s.time_from_treatment_start = 0
    """
    df_a = pd.read_sql_query(query_a, conn)
    
    print("Part 4: Data Subset Analysis")
    print("Query A: Baseline Melanoma PBMC (Treatment: miraclib)")
    
    project_counts = df_a['project'].value_counts()
    print("\nSamples per project:")
    print(project_counts.to_string())

    ## drop duplicates and compute response/sex counts
    unique_subjects = df_a.drop_duplicates(subset=['subject'])
    response_counts = unique_subjects['response'].value_counts()
    print("\nSubjects by response status:")
    print(response_counts.to_string())

    sex_counts = unique_subjects['sex'].value_counts()
    print("\nSubjects by sex:")
    print(sex_counts.to_string())

    ## query b: melanoma males w/ B-cells for responders at time=0
    query_b = """
        SELECT c.count as b_cell_count
        FROM samples s
        JOIN subjects sub ON s.subject = sub.subject
        JOIN cell_counts c ON s.sample = c.sample
        WHERE sub.condition = 'melanoma'
          AND sub.sex = 'M'
          AND sub.response = 'yes'
          AND s.time_from_treatment_start = 0
          AND c.population = 'b_cell'
    """
    df_b = pd.read_sql_query(query_b, conn)
    avg_b_cells = df_b['b_cell_count'].mean()
    
    print("Query B: Targeted Metric")
    print(f"Average number of B cells (Melanoma Males, Responders, Baseline): {avg_b_cells:.2f}")

    conn.close()

if __name__ == "__main__":
    run_subset_analysis()