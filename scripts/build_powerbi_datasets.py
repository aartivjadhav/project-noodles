# This file is the "master runner" for Task 6: connect to the database → create tables → add calculated fields → create views → validate the row count → report OK or FAILED.

import sys
# 👉 Import sys to use sys.exit(code) at the end of the script (0 = success, 1 = error)

import pandas as pd
# 👉 Import pandas to read SQL into a DataFrame and count the row count (validate data)

from sqlalchemy import text
# 👉 Import text() to safely execute raw SQL (SQL string) in SQLAlchemy

from etl.load import get_engine
# 👉 Import the get_engine() function to create a DB (MySQL) connection from .env

from etl.logger import setup_logger
# 👉 Import the setup_logger() function to create a standard logger (print logs to the terminal)

from etl.aggregations import (
    create_currency_summary_table,
    create_daily_social_summary,
    create_social_engagement_summary,
)
# 👉 Import 3 functions to create aggregation tables.

from etl.calculated_columns import (
    add_engagement_categories,
    calculate_social_trend_indicators,
)
# 👉 Import two functions to create calculated/derived columns and an enriched trend table.

logger = setup_logger("powerbi_prep")

# -------------------------------------------------
# Helper: execute SQL file
# -------------------------------------------------
def execute_sql_file(engine, filepath: str):
    # 👉 Define a function to run an SQL file
    # 👉 Input: engine (DB connection), filepath (path to the .sql file)

    logger.info(f"Executing SQL file: {filepath}")
    # 👉 Log which SQL file is currently running
    
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()
    # 👉 Open the SQL file and read the entire content as an SQL string

    statements = [s.strip() for s in sql.split(";") if s.strip()]
    # 👉 Split SQL content into multiple statements using semicolons (;)
    # 👉 Use `strip()` to remove whitespace/empty lines
    # 👉 Use `if s.strip()` to remove "empty statements"

    with engine.begin() as conn:
    # 👉 Open transaction (BEGIN)
    # 👉 If an error occurs → rollback, preventing the database from being in an "unfinished" state.
        for stmt in statements:
            conn.execute(text(stmt))
        # 👉 Repeat each SQL statement and execute it.
        # 👉 Wrap it in text (stmt) so SQLAlchemy understands this is raw SQL.

    logger.info(f"✓ SQL executed: {filepath}")

# -------------------------------------------------
# Main pipeline
# -------------------------------------------------
def main():
# 👉 The main function to gather the entire flow of the dataset build

    logger.info("=" * 60)
    logger.info("Building Power BI datasets")
    logger.info("=" * 60)
    # 👉 Add a header for a nicer log and easier readability when running.

    try:
    # 👉 Start try/catch blocks so that if there are errors, they are logged to the stacktrace.

        engine = get_engine()
        # 👉 Create a DB engine (connect to MySQL) from .env

        logger.info("✓ Database connection established")

        # -----------------------------------------
        # Step 1: Aggregation tables
        # -----------------------------------------
        logger.info("Step 1: Creating aggregation tables")

        create_currency_summary_table(engine)
        # 👉 Create a CurrencySummary table (summarized by currency)

        create_daily_social_summary(engine)
        # 👉 Create a DailySocialSummary table (summarized by day)

        create_social_engagement_summary(engine)
        # 👉 Create a SocialEngagementSummary table (aggregated by platform).

        # -----------------------------------------
        # Step 2: Calculated / derived columns
        # -----------------------------------------
        logger.info("Step 2: Creating calculated columns")

        add_engagement_categories(engine)
        # 👉 Read CurrencySummary and add EngagementCategory, InfluenceLevel
        # 👉 Then overwrite the CurrencySummary table

        calculate_social_trend_indicators(engine)
        # 👉 Query facts + dim then calculate MA7/MA30/momentum/trend
        # 👉 Save to FactSocialEngagementEnriched table

        # -----------------------------------------
        # Step 3: Create Power BI views
        # -----------------------------------------
        logger.info("Step 3: Creating Power BI views")

        execute_sql_file(engine, "sql/04_create_powerbi_views.sql")
        # 👉 Run the SQL file to create vw_ExecutiveDashboard, vw_TimeSeries, and vw_SocialAnalytics

        # -----------------------------------------
        # Step 4: Validate results
        # -----------------------------------------
        logger.info("Step 4: Validating datasets")

        summary = pd.read_sql("""
            SELECT 'CurrencySummary' AS TableName, COUNT(*) AS RowCount FROM CurrencySummary
            UNION ALL
            SELECT 'DailySocialSummary', COUNT(*) AS RowCount FROM DailySocialSummary
            UNION ALL
            SELECT 'SocialEngagementSummary', COUNT(*) AS RowCount FROM SocialEngagementSummary
        """, engine)
        # 👉 Run 3 COUNT statements to get the row count of 3 tables
        # 👉 Combine them into one DataFrame summary

        logger.info("Dataset summary:")
        for _, row in summary.iterrows():
            logger.info(f"  {row['TableName']}: {row['RowCount']} rows")
        # 👉 Iterate through each row in the DataFrame and print the row number for each table

        logger.info("✓ Power BI datasets ready")
        return 0
        # 👉 Returns code 0 = success

    except Exception:
    # 👉 If there are any errors in the try
        logger.exception("❌ FAILED to build Power BI datasets")
        return 1
        # 👉 Returns code 1 = failure

if __name__ == "__main__":
    sys.exit(main())
# 👉 Call main() and exit according to the returned code
# 👉 Success → exit 0, error → exit 1