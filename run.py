from config import PROCESSED_DATA_PATH, RAW_DATA_PATH, logger
from src.etl_pipeline import ETLPipeline


def main() -> int:
    logger.info("Input file: %s", RAW_DATA_PATH)
    logger.info("Output file: %s", PROCESSED_DATA_PATH)

    if not RAW_DATA_PATH.exists():
        logger.error("Cannot run pipeline because raw-data.csv was not found")
        logger.error("Place your raw CSV here: %s", RAW_DATA_PATH)
        return 1

    try:
        clean_df = ETLPipeline().run()
    except Exception as exc:
        logger.exception("Pipeline failed: %s", exc)
        return 1

    logger.info("Run finished successfully with %s processed rows", len(clean_df))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
