import pathlib
import sys

import pandas as pd


ROOT_DIR = pathlib.Path(__file__).resolve().parent
while not (ROOT_DIR / "config.py").exists() and ROOT_DIR != ROOT_DIR.parent:
    ROOT_DIR = ROOT_DIR.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import MAX_DUPLICATE_PERCENT, MAX_NULL_PERCENT, RAW_DATA_PATH, logger


class DataValidator:
    def __init__(
        self,
        max_null_percent: float = MAX_NULL_PERCENT,
        max_duplicate_percent: float = MAX_DUPLICATE_PERCENT,
    ):
        self.max_null_percent = max_null_percent
        self.max_duplicate_percent = max_duplicate_percent

    def validate(self, df: pd.DataFrame) -> dict:
        results = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "nulls": self.check_nulls(df),
            "duplicates": self.check_duplicates(df),
            "invalid_ranges": self.check_invalid_ranges(df),
            "wrong_types": self.check_wrong_types(df),
        }

        logger.info("Validation finished with %s issue groups", self.count_issue_groups(results))
        return results

    def check_nulls(self, df: pd.DataFrame) -> dict:
        null_counts = df.isna().sum()
        issues = {}

        for column, count in null_counts.items():
            if count == 0:
                continue

            percent = round((count / len(df)) * 100, 2) if len(df) else 0.0
            issues[column] = {
                "count": int(count),
                "percent": percent,
                "critical": percent > self.max_null_percent,
            }

        return issues

    def check_duplicates(self, df: pd.DataFrame) -> dict:
        duplicate_count = int(df.duplicated().sum())
        duplicate_percent = round((duplicate_count / len(df)) * 100, 2) if len(df) else 0.0

        return {
            "count": duplicate_count,
            "percent": duplicate_percent,
            "critical": duplicate_percent > self.max_duplicate_percent,
        }

    def check_invalid_ranges(self, df: pd.DataFrame) -> dict:
        issues = {}

        age_columns = ["age", "patient_age", "age_from_dob"]
        for column in age_columns:
            if column in df.columns:
                ages = pd.to_numeric(df[column], errors="coerce")
                invalid = df[ages.notna() & ((ages < 0) | (ages > 120))]
                self.add_range_issue(issues, column, invalid, "Age must be between 0 and 120")

        money_columns = [
            "bill_amount",
            "billing_amount",
            "amount_billed",
            "amount_paid",
            "payment_amount",
        ]
        for column in money_columns:
            if column in df.columns:
                values = pd.to_numeric(df[column], errors="coerce")
                invalid = df[values.notna() & (values < 0)]
                self.add_range_issue(issues, column, invalid, "Money values cannot be negative")

        rate_columns = ["bill_collection_rate", "collection_rate"]
        for column in rate_columns:
            if column in df.columns:
                rates = pd.to_numeric(df[column], errors="coerce")
                invalid = df[rates.notna() & ((rates < 0) | (rates > 1))]
                self.add_range_issue(issues, column, invalid, "Rate must be between 0 and 1")

        return issues

    def check_wrong_types(self, df: pd.DataFrame) -> dict:
        issues = {}

        numeric_columns = [
            "patient_id",
            "appointment_id",
            "billing_id",
            "age",
            "patient_age",
            "bill_amount",
            "billing_amount",
            "amount_billed",
            "amount_paid",
            "payment_amount",
        ]
        for column in numeric_columns:
            if column in df.columns:
                invalid_count = self.count_unparseable_values(df[column], "number")
                if invalid_count:
                    issues[column] = {
                        "expected": "number",
                        "invalid_count": invalid_count,
                    }

        date_columns = [
            "date_of_birth",
            "dob",
            "appointment_date",
            "billing_date",
            "registered_at",
        ]
        for column in date_columns:
            if column in df.columns:
                invalid_count = self.count_unparseable_values(df[column], "date")
                if invalid_count:
                    issues[column] = {
                        "expected": "date",
                        "invalid_count": invalid_count,
                    }

        return issues

    def count_unparseable_values(self, series: pd.Series, expected_type: str) -> int:
        non_empty = series.dropna()

        if expected_type == "number":
            parsed = pd.to_numeric(non_empty, errors="coerce")
        elif expected_type == "date":
            parsed = pd.to_datetime(non_empty, errors="coerce")
        else:
            return 0

        return int(parsed.isna().sum())

    def add_range_issue(self, issues: dict, column: str, invalid_rows: pd.DataFrame, message: str) -> None:
        if invalid_rows.empty:
            return

        issues[column] = {
            "message": message,
            "invalid_count": len(invalid_rows),
            "sample_indexes": invalid_rows.index[:5].tolist(),
        }

    def count_issue_groups(self, results: dict) -> int:
        issue_count = 0

        for key in ["nulls", "invalid_ranges", "wrong_types"]:
            if results.get(key):
                issue_count += 1

        if results.get("duplicates", {}).get("count", 0) > 0:
            issue_count += 1

        return issue_count


if __name__ == "__main__":
    if not RAW_DATA_PATH.exists():
        logger.error("Raw data file not found: %s", RAW_DATA_PATH)
        raise SystemExit(1)

    raw_df = pd.read_csv(RAW_DATA_PATH)
    report = DataValidator().validate(raw_df)
    print(report)
