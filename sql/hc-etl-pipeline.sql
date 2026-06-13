CREATE SCHEMA IF NOT EXISTS learner_03;

DROP TABLE IF EXISTS learner_03.healthcare_processed;
DROP TABLE IF EXISTS learner_03.healthcare_raw;

CREATE TABLE learner_03.healthcare_raw (
    patient_id TEXT,
    first_name TEXT,
    last_name TEXT,
    date_of_birth TEXT,
    gender TEXT,
    blood_type TEXT,
    email TEXT,
    phone TEXT,
    city TEXT,
    insurance_type TEXT,
    registered_at TEXT,
    appointment_id TEXT,
    appointment_date TEXT,
    billing_id TEXT,
    bill_amount TEXT,
    billing_amount TEXT,
    amount_billed TEXT,
    amount_paid TEXT,
    payment_amount TEXT
);

CREATE TABLE learner_03.healthcare_processed (
    patient_id INTEGER,
    first_name TEXT,
    last_name TEXT,
    date_of_birth DATE,
    gender TEXT,
    blood_type TEXT,
    email TEXT,
    phone TEXT,
    city TEXT,
    insurance_type TEXT,
    registered_at DATE,
    appointment_id INTEGER,
    appointment_date DATE,
    billing_id INTEGER,
    bill_amount NUMERIC(12, 2),
    billing_amount NUMERIC(12, 2),
    amount_billed NUMERIC(12, 2),
    amount_paid NUMERIC(12, 2),
    payment_amount NUMERIC(12, 2),
    age_from_dob INTEGER,
    bill_collection_rate NUMERIC(8, 4)
);

-- Load CSV files after running the Python ETL.
-- Update the file paths if your project lives somewhere else.
-- In psql, use \copy. In pgAdmin, use the import/export tool.

-- \copy learner_03.healthcare_raw FROM 'C:/Healthcare_ETL_Pipeline/data/raw/raw-data.csv' WITH (FORMAT csv, HEADER true);
-- \copy learner_03.healthcare_processed FROM 'C:/Healthcare_ETL_Pipeline/data/processed/processed-data.csv' WITH (FORMAT csv, HEADER true);

SELECT
    COUNT(*) AS raw_row_count
FROM learner_03.healthcare_raw;

SELECT
    COUNT(*) AS processed_row_count
FROM learner_03.healthcare_processed;

SELECT
    COUNT(*) AS duplicate_processed_rows
FROM (
    SELECT
        patient_id,
        date_of_birth,
        appointment_id,
        billing_id,
        COUNT(*) AS row_count
    FROM learner_03.healthcare_processed
    GROUP BY
        patient_id,
        date_of_birth,
        appointment_id,
        billing_id
    HAVING COUNT(*) > 1
) duplicates;

SELECT
    SUM(CASE WHEN patient_id IS NULL THEN 1 ELSE 0 END) AS missing_patient_id,
    SUM(CASE WHEN first_name IS NULL THEN 1 ELSE 0 END) AS missing_first_name,
    SUM(CASE WHEN date_of_birth IS NULL THEN 1 ELSE 0 END) AS missing_date_of_birth,
    SUM(CASE WHEN age_from_dob IS NULL THEN 1 ELSE 0 END) AS missing_age_from_dob,
    SUM(CASE WHEN bill_collection_rate IS NULL THEN 1 ELSE 0 END) AS missing_bill_collection_rate
FROM learner_03.healthcare_processed;

SELECT
    patient_id,
    first_name,
    last_name,
    date_of_birth,
    age_from_dob
FROM learner_03.healthcare_processed
WHERE age_from_dob < 0
   OR age_from_dob > 120;

SELECT
    patient_id,
    bill_amount,
    billing_amount,
    amount_billed,
    amount_paid,
    payment_amount
FROM learner_03.healthcare_processed
WHERE COALESCE(bill_amount, 0) < 0
   OR COALESCE(billing_amount, 0) < 0
   OR COALESCE(amount_billed, 0) < 0
   OR COALESCE(amount_paid, 0) < 0
   OR COALESCE(payment_amount, 0) < 0;

SELECT
    patient_id,
    amount_billed,
    amount_paid,
    bill_collection_rate
FROM learner_03.healthcare_processed
WHERE bill_collection_rate < 0
   OR bill_collection_rate > 1;

SELECT
    insurance_type,
    COUNT(*) AS patient_count,
    ROUND(AVG(age_from_dob), 1) AS avg_age,
    ROUND(AVG(bill_collection_rate), 4) AS avg_collection_rate
FROM learner_03.healthcare_processed
GROUP BY insurance_type
ORDER BY patient_count DESC;

SELECT
    city,
    COUNT(*) AS patient_count
FROM learner_03.healthcare_processed
GROUP BY city
ORDER BY patient_count DESC; 