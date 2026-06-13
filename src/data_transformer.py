import pathlib
import sys

import pandas as pd


ROOT_DIR = pathlib.Path(__file__).resolve().parent
while not (ROOT_DIR / "config.py").exists() and ROOT_DIR != ROOT_DIR.parent:
    ROOT_DIR = ROOT_DIR.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import PROCESSED_DATA_PATH, RAW_DATA_PATH, logger


class DataTransformer:
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        clean_df = df.copy()

        clean_df = self.clean_column_names(clean_df)
        clean_df = self.clean_text_columns(clean_df)
        clean_df = self.remove_duplicates(clean_df)
        clean_df = self.fix_data_types(clean_df)
        clean_df = self.fix_invalid_ranges(clean_df)
        clean_df = self.fill_missing_values(clean_df)
        clean_df = self.add_derived_columns(clean_df)

        logger.info("Transformation finished: %s rows, %s columns", len(clean_df), len(clean_df.columns))
        return clean_df

    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_", regex=False)
            .str.replace("-", "_", regex=False)
        )
        return df

    def clean_text_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        text_columns = df.select_dtypes(include=["object"]).columns

        for column in text_columns:
            df[column] = df[column].astype("string").str.strip()
            df[column] = df[column].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

        return df

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        before_count = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        removed_count = before_count - len(df)

        if removed_count:
            logger.info("Removed %s duplicate rows", removed_count)

        return df

    def fix_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        for column in self.existing_columns(df, self.numeric_columns()):
            df[column] = pd.to_numeric(df[column], errors="coerce")

        for column in self.existing_columns(df, self.date_columns()):
            df[column] = pd.to_datetime(df[column], errors="coerce")

        return df

    def fix_invalid_ranges(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        for column in self.existing_columns(df, ["age", "patient_age", "age_from_dob"]):
            df.loc[(df[column] < 0) | (df[column] > 120), column] = pd.NA

        for column in self.existing_columns(df, self.money_columns()):
            df.loc[df[column] < 0, column] = pd.NA

        for column in self.existing_columns(df, ["bill_collection_rate", "collection_rate"]):
            df.loc[(df[column] < 0) | (df[column] > 1), column] = pd.NA

        return df

    def fill_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        for column in df.columns:
            if df[column].isna().sum() == 0:
                continue

            if pd.api.types.is_numeric_dtype(df[column]):
                fill_value = df[column].median()
                if pd.isna(fill_value):
                    fill_value = 0
                elif pd.api.types.is_integer_dtype(df[column]):
                    fill_value = round(fill_value)

                df[column] = df[column].fillna(fill_value)
            elif pd.api.types.is_datetime64_any_dtype(df[column]):
                df[column] = df[column].fillna(df[column].mode().iloc[0]) if not df[column].mode().empty else df[column]
            else:
                mode_values = df[column].mode(dropna=True)
                fill_value = mode_values.iloc[0] if not mode_values.empty else "Unknown"
                df[column] = df[column].fillna(fill_value)

        return df

    def add_derived_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        dob_column = self.first_existing_column(df, ["date_of_birth", "dob"])
        if dob_column and "age_from_dob" not in df.columns:
            today = pd.Timestamp.today().normalize()
            df["age_from_dob"] = ((today - df[dob_column]).dt.days // 365).astype("Int64")

        billed_column = self.first_existing_column(df, ["amount_billed", "bill_amount", "billing_amount"])
        paid_column = self.first_existing_column(df, ["amount_paid", "payment_amount"])
        if billed_column and paid_column and "bill_collection_rate" not in df.columns:
            df["bill_collection_rate"] = df[paid_column] / df[billed_column]
            df.loc[df[billed_column] <= 0, "bill_collection_rate"] = 0
            df["bill_collection_rate"] = df["bill_collection_rate"].clip(lower=0, upper=1)

        return df

    def numeric_columns(self) -> list[str]:
        return [
            "patient_id",
            "appointment_id",
            "billing_id",
            "age",
            "patient_age",
            *self.money_columns(),
        ]

    def money_columns(self) -> list[str]:
        return [
            "bill_amount",
            "billing_amount",
            "amount_billed",
            "amount_paid",
            "payment_amount",
        ]

    def date_columns(self) -> list[str]:
        return [
            "date_of_birth",
            "dob",
            "appointment_date",
            "billing_date",
            "registered_at",
        ]

    def existing_columns(self, df: pd.DataFrame, columns: list[str]) -> list[str]:
        return [column for column in columns if column in df.columns]

    def first_existing_column(self, df: pd.DataFrame, columns: list[str]) -> str | None:
        for column in columns:
            if column in df.columns:
                return column
        return None


if __name__ == "__main__":
    if not RAW_DATA_PATH.exists():
        logger.error("Raw data file not found: %s", RAW_DATA_PATH)
        raise SystemExit(1)

    raw_df = pd.read_csv(RAW_DATA_PATH)
    transformed_df = DataTransformer().transform(raw_df)
    transformed_df.to_csv(PROCESSED_DATA_PATH, index=False)
    logger.info("Saved transformed data to %s", PROCESSED_DATA_PATH)
