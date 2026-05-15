# The calculated_columns.py file is used to add analytical logic (analytics layer) to the aggregated data, helping Power BI avoid complex calculations.

import pandas as pd
# 👉 pandas: used to read/process tabular data

import numpy as np
# 👉 numpy: supports arithmetic and conditional calculations

from .logger import setup_logger
# 👉 Import logger for shared use with ETL

logger = setup_logger("calculated_columns")
# 👉 Create a separate logger for the calculated_columns.py file

# -------------------------------------------------
# Social Categories (REPLACE price categories)
# -------------------------------------------------
def add_engagement_categories(engine):

    logger.info("Adding engagement categories...")

    df = pd.read_sql("SELECT * FROM CurrencySummary", engine)

    # ---- Engagement category
    df["EngagementCategory"] = pd.cut(
        df["TotalEngagements"],
        bins=[0, 100, 1_000, 10_000, float("inf")],
        labels=["Low", "Medium", "High", "Viral"],
    )

    # ---- Influence level
    df["InfluenceLevel"] = pd.cut(
        df["AvgEngagementScore"],
        bins=[0, 0.3, 0.6, 1],
        labels=["Low", "Medium", "High"],
    )

    # ✅ WRITE TO NEW TABLE (DO NOT TOUCH CurrencySummary)
    df.to_sql(
        "CurrencySummary_Enriched",
        engine,
        if_exists="replace",
        index=False
    )

    logger.info("✓ Engagement categories added → CurrencySummary_Enriched")

# -------------------------------------------------
# Social Trend Indicators (REPLACE price trend)
# -------------------------------------------------
def calculate_social_trend_indicators(engine):
    logger.info("Calculating social trend indicators...")

    query = """
    SELECT
        f.CurrencyKey,
        dc.Symbol        AS CurrencySymbol,
        dd.FullDate,
        f.EngagementScore,
        f.Likes,
        f.Comments,
        f.Retweets,
        f.Impressions
    FROM FactSocialEngagement f
    JOIN DimCurrency dc
        ON f.CurrencyKey = dc.CurrencyKey
    JOIN DimDate dd
        ON f.DateKey = dd.DateKey
    ORDER BY f.CurrencyKey, dd.FullDate;
    """

    df = pd.read_sql(query, engine)

    # ------------------------------------------------
    # 1. Moving averages
    # ------------------------------------------------
    df["Engagement_MA_7d"] = (
        df.groupby("CurrencyKey")["EngagementScore"]
        .transform(lambda x: x.rolling(7, min_periods=1).mean())
    )

    df["Engagement_MA_30d"] = (
        df.groupby("CurrencyKey")["EngagementScore"]
        .transform(lambda x: x.rolling(30, min_periods=1).mean())
    )

    # ------------------------------------------------
    # 2. SAFE Momentum calculation (NO inf)
    # ------------------------------------------------
    prev_7d = (
        df.groupby("CurrencyKey")["EngagementScore"]
        .shift(7)
    )

    df["EngagementMomentum_7d"] = np.where(
        prev_7d > 0,
        (df["EngagementScore"] - prev_7d) / prev_7d,
        None
    )

    # ------------------------------------------------
    # 3. Trend direction
    # ------------------------------------------------
    df["TrendDirection"] = np.where(
        df["Engagement_MA_7d"] >= df["Engagement_MA_30d"],
        "Upward",
        "Downward",
    )

    # ------------------------------------------------
    # 4. FINAL SANITIZATION (MySQL-safe)
    # ------------------------------------------------
    df.replace([np.inf, -np.inf], None, inplace=True)
    df = df.where(pd.notnull(df), None)

    # ------------------------------------------------
    # 5. Save enriched fact table
    # ------------------------------------------------
    df.to_sql(
        "FactSocialEngagementEnriched",
        engine,
        if_exists="replace",
        index=False,
    )

    logger.info("✓ Social trend indicators calculated successfully")