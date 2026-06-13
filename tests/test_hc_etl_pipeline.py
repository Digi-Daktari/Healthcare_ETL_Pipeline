from pathlib import Path

import pandas as pd

from src.data_transformer import DataTransformer
from src.data_validator import DataValidator
from src.etl_pipeline import ETLPipeline


def sample_dirty_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Patient ID": ["1", "2", "2", "bad"],
            "First Name": [" Ana ", None, None, "Maya"],
            "Date of Birth": ["2000-01-01", "not-a-date", "not-a-date", "1985-05-20"],
            "Age": ["24", "200", "200", "-4"],
            "Amount Billed": ["1000", "-50", "-50", "0"],
            "Amount Paid": ["750", "25", "25", "0"],
        }
    )


def test_validator_finds_null_values():
    report = DataValidator().validate(sample_dirty_data())

    assert "First Name" in report["nulls"]
    assert report["nulls"]["First Name"]["count"] == 2


def test_validator_finds_duplicate_rows():
    report = DataValidator().validate(sample_dirty_data())

    assert report["duplicates"]["count"] == 1
    assert report["duplicates"]["percent"] > 0


def test_validator_finds_invalid_age_ranges():
    df = pd.DataFrame({"age": [34, -2, 140]})

    report = DataValidator().validate(df)

    assert report["invalid_ranges"]["age"]["invalid_count"] == 2


def test_validator_finds_negative_money_values():
    df = pd.DataFrame({"amount_billed": [100.0, -1.0, 250.0]})

    report = DataValidator().validate(df)

    assert report["invalid_ranges"]["amount_billed"]["invalid_count"] == 1


def test_validator_finds_wrong_numeric_types():
    df = pd.DataFrame({"patient_id": ["1", "not-a-number", "3"]})

    report = DataValidator().validate(df)

    assert report["wrong_types"]["patient_id"]["invalid_count"] == 1


def test_validator_finds_wrong_date_types():
    df = pd.DataFrame({"date_of_birth": ["2000-01-01", "wrong-date"]})

    report = DataValidator().validate(df)

    assert report["wrong_types"]["date_of_birth"]["invalid_count"] == 1


def test_transformer_cleans_column_names_and_text():
    clean_df = DataTransformer().transform(sample_dirty_data())

    assert "patient_id" in clean_df.columns
    assert clean_df.loc[0, "first_name"] == "Ana"


def test_transformer_removes_duplicate_rows():
    clean_df = DataTransformer().transform(sample_dirty_data())

    assert len(clean_df) == 3


def test_transformer_converts_numeric_and_date_columns():
    clean_df = DataTransformer().transform(sample_dirty_data())

    assert pd.api.types.is_numeric_dtype(clean_df["patient_id"])
    assert pd.api.types.is_datetime64_any_dtype(clean_df["date_of_birth"])


def test_transformer_fills_missing_values():
    clean_df = DataTransformer().transform(sample_dirty_data())

    assert clean_df.isna().sum().sum() == 0


def test_transformer_adds_age_from_dob():
    clean_df = DataTransformer().transform(sample_dirty_data())

    assert "age_from_dob" in clean_df.columns
    assert clean_df["age_from_dob"].between(0, 120).all()


def test_transformer_adds_bill_collection_rate():
    clean_df = DataTransformer().transform(sample_dirty_data())

    assert "bill_collection_rate" in clean_df.columns
    assert clean_df["bill_collection_rate"].between(0, 1).all()


def test_pipeline_runs_and_saves_processed_file():
    raw_path = Path("data/raw/test-pipeline-raw-data.csv")
    processed_path = Path("data/processed/test-pipeline-processed-data.csv")
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    processed_path.parent.mkdir(parents=True, exist_ok=True)

    sample_dirty_data().to_csv(raw_path, index=False)

    try:
        clean_df = ETLPipeline(raw_path=raw_path, processed_path=processed_path).run()

        assert processed_path.exists()
        assert len(clean_df) == 3
        assert "age_from_dob" in clean_df.columns
        assert "bill_collection_rate" in clean_df.columns
    finally:
        for path in [raw_path, processed_path]:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
