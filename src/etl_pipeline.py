import pathlib
import sys

import pandas as pd


ROOT_DIR = pathlib.Path(__file__).resolve().parent
while not (ROOT_DIR / "config.py").exists() and ROOT_DIR != ROOT_DIR.parent:
    ROOT_DIR = ROOT_DIR.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import PROCESSED_DATA_PATH, RAW_DATA_PATH, logger
from src.data_transformer import DataTransformer
from src.data_validator import DataValidator


class ETLPipeline:
    def __init__(
        self,
        raw_path: pathlib.Path = RAW_DATA_PATH,
        processed_path: pathlib.Path = PROCESSED_DATA_PATH,
    ):
        self.raw_path = pathlib.Path(raw_path)
        self.processed_path = pathlib.Path(processed_path)
        self.validator = DataValidator()
        self.transformer = DataTransformer()

    def run(self) -> pd.DataFrame:
        logger.info("Starting healthcare ETL pipeline")

        raw_df = self.extract()
        raw_report = self.validate(raw_df, stage="raw")

        clean_df = self.transform(raw_df)
        clean_report = self.validate(clean_df, stage="processed")

        self.load(clean_df)

        logger.info("Pipeline completed successfully")
        self.log_report_summary("Raw validation", raw_report)
        self.log_report_summary("Processed validation", clean_report)

        return clean_df

    def extract(self) -> pd.DataFrame:
        if not self.raw_path.exists():
            raise FileNotFoundError(f"Raw data file not found: {self.raw_path}")

        logger.info("Extracting data from %s", self.raw_path)
        df = pd.read_csv(self.raw_path)
        logger.info("Extracted %s rows and %s columns", len(df), len(df.columns))
        return df

    def validate(self, df: pd.DataFrame, stage: str) -> dict:
        logger.info("Validating %s data", stage)
        return self.validator.validate(df)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Transforming raw data")
        return self.transformer.transform(df)

    def load(self, df: pd.DataFrame) -> None:
        self.processed_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Loading clean data to %s", self.processed_path)
        df.to_csv(self.processed_path, index=False)
        logger.info("Saved %s rows to processed data file", len(df))

    def log_report_summary(self, label: str, report: dict) -> None:
        null_columns = len(report.get("nulls", {}))
        duplicate_count = report.get("duplicates", {}).get("count", 0)
        range_issues = len(report.get("invalid_ranges", {}))
        type_issues = len(report.get("wrong_types", {}))

        logger.info(
            "%s: %s null columns, %s duplicate rows, %s range issues, %s type issues",
            label,
            null_columns,
            duplicate_count,
            range_issues,
            type_issues,
        )


if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.run()
