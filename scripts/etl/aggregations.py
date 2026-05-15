# The aggregations.py file is the heart of Task 6, responsible for converting raw social media data into a ready-to-use aggregation table for Power BI.

from sqlalchemy import text
# 👉 Used to run raw SQL (CREATE TABLE, DROP TABLE...)

from .logger import setup_logger
# 👉 Import logger for shared use with ETL

logger = setup_logger("aggregations")

# -------------------------------------------------
# CurrencySummary
# -------------------------------------------------
def create_currency_summary_table(engine):
    # 👉 Create a CurrencySummary table from social data

    logger.info("Creating CurrencySummary (from social data) ...")

    drop_sql = "DROP TABLE IF EXISTS CurrencySummary;"
    # 👉 Delete the old table if it already exists (make sure to rebuild cleanly)

    create_sql = """
    CREATE TABLE CurrencySummary AS
    SELECT 
        dc.CurrencyKey,
        dc.Symbol              AS CurrencySymbol,
        dc.CurrencyName        AS CurrencyName,
        dc.BaseCurrency        AS BaseCurrency,

        COUNT(*)               AS TotalEngagements,
        COUNT(DISTINCT f.DateKey) AS ActiveDays,

        SUM(f.Likes)           AS TotalLikes,
        SUM(f.Comments)        AS TotalComments,
        SUM(f.Retweets)        AS TotalRetweets,
        SUM(f.Impressions)     AS TotalImpressions,

        AVG(f.EngagementScore) AS AvgEngagementScore,
        MAX(f.LoadDate)        AS LastEngagementDate

    FROM FactSocialEngagement f
    JOIN DimCurrency dc
        ON f.CurrencyKey = dc.CurrencyKey
    GROUP BY
        dc.CurrencyKey,
        dc.Symbol,
        dc.CurrencyName,
        dc.BaseCurrency;
    """
    # 👉 Gather all social media data by currency

    with engine.begin() as conn:
        conn.execute(text(drop_sql))
        conn.execute(text(create_sql))
    # 👉 Run DROP + CREATE within the same transaction

    logger.info("✓ CurrencySummary created (social-based)")

# -------------------------------------------------
# DailySocialSummary
# -------------------------------------------------
def create_daily_social_summary(engine):
    # 👉 Create a daily social media summary table

    logger.info("Creating DailySocialSummary ...")

    drop_sql = "DROP TABLE IF EXISTS DailySocialSummary;"

    create_sql = """
    CREATE TABLE DailySocialSummary AS
    SELECT
        dd.DateKey,
        dd.FullDate,
        dd.Year,
        dd.Month,
        dd.MonthName,

        COUNT(*)               AS TotalPosts,
        COUNT(DISTINCT f.CurrencyKey) AS ActiveCurrencies,

        SUM(f.Likes)           AS TotalLikes,
        SUM(f.Comments)        AS TotalComments,
        SUM(f.Retweets)        AS TotalRetweets,
        SUM(f.Impressions)     AS TotalImpressions,

        AVG(f.EngagementScore) AS AvgEngagementScore

    FROM FactSocialEngagement f
    JOIN DimDate dd
        ON f.DateKey = dd.DateKey
    GROUP BY
        dd.DateKey,
        dd.FullDate,
        dd.Year,
        dd.Month,
        dd.MonthName;
    """
    # 👉 Gather social media data by day (time series)

    with engine.begin() as conn:
        conn.execute(text(drop_sql))
        conn.execute(text(create_sql))
    # 👉 Run DROP + CREATE within the same transaction

    logger.info("✓ DailySocialSummary created")

# -------------------------------------------------
# SocialEngagementSummary
# -------------------------------------------------
def create_social_engagement_summary(engine):
    # 👉 Create a summary table of social media by currency and platform

    logger.info("Creating SocialEngagementSummary (SQLite) ...")

    drop_sql = "DROP TABLE IF EXISTS SocialEngagementSummary;"

    create_sql = """
    CREATE TABLE SocialEngagementSummary AS
    SELECT 
        dc.CurrencyKey,
        dc.Symbol              AS CurrencySymbol,
        dsp.PlatformName,
        COUNT(*)               AS TotalEngagements,
        SUM(f.Likes)           AS TotalLikes,
        SUM(f.Retweets)        AS TotalRetweets,
        SUM(f.Comments)        AS TotalComments,
        SUM(f.Impressions)     AS TotalImpressions,
        AVG(f.EngagementScore) AS AvgEngagementScore,
        MAX(f.LoadDate)        AS LastEngagement
    FROM FactSocialEngagement f
    JOIN DimCurrency dc 
        ON f.CurrencyKey = dc.CurrencyKey
    JOIN DimPlatform dsp 
        ON f.PlatformKey = dsp.PlatformKey
    GROUP BY 
        dc.CurrencyKey,
        dc.Symbol,
        dsp.PlatformName;
    """
    # 👉 Gather data by platform (Twitter, Reddit, ...)

    with engine.engine.begin() as conn:
        conn.execute(text(drop_sql))
        conn.execute(text(create_sql))
        conn.commit()
   # 👉 Run DROP + CREATE within the same transaction

    logger.info("✓ SocialEngagementSummary created")