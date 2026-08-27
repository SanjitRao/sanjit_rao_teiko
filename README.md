### How to Run Codebase
* python -m venv test_venv
* make setup
* make pipeline
* make dashboard


### Database Schema
The data is modeled using a normalized, relational SQLite database (`immune_trial.db`) consisting of three distinct tables:
1. **`subjects`**: Stores static, patient-level metadata (`subject`, `project`, `condition`, `age`, `sex`, `treatment`, `response`).
2. **`samples`**: Stores longitudinal sample collection metadata (`sample`, `subject`, `sample_type`, `time_from_treatment_start`).
3. **`cell_counts`**: Stores the unpivoted immune cell populations and their corresponding counts (`sample`, `population`, `count`).

### Design Rationale & Scalability
* **Normalization (3NF):** By decoupling the patient metadata from the sample metadata, we eliminate massive data duplication. A patient's age, sex, and indication are stored exactly once, rather than being redundantly repeated for every longitudinal timepoint and sample type collected from that subject.
* **Vertical Scaling:** The `cell_counts` table transforms the biological data from a "wide" format (columns) to a "long" format (rows). If Loblaw Bio later expands the trial to measure 50+ new cell subsets using high-parameter flow cytometry, the database schema requires *zero* structural changes. The database simply accepts new rows with a different `population` tag, effectively preventing column bloat.
* **Analytical Efficiency:** This decoupled, long-format structure optimizes aggregation queries. Calculating total cell counts or filtering by specific immune subsets requires highly efficient SQL `GROUP BY` and `JOIN` operations rather than tedious, hard-coded column arithmetic.

### Code Structure & Rationale
* Kept the code strcuture as simple and interpretable as possible, giving each part of this coding challenge its own script, numbered by part (part2.py, part3.py, etc)

### Link to Dashboard:
https://sanjitraoteiko-vo3hwauf6hulawvhmsuhyw.streamlit.app/