-- This file creates the final VIEW layer for Power BI, enabling fast Power BI imports – without complex processing.

-- ============================================
-- View: Executive Dashboard
-- ============================================

DROP VIEW IF EXISTS vw_ExecutiveDashboard;
-- 👉 Delete the old view if it already exists (make sure to rebuild it cleanly).

CREATE VIEW vw_ExecutiveDashboard AS
SELECT 
    cs.CurrencySymbol,
    cs.CurrencyName,
    -- 👉 Currency identification information

    -- Social metrics
    ses.TotalEngagements,
    ses.TotalLikes,
    ses.TotalComments,
    ses.TotalRetweets,
    ses.TotalImpressions,
    ses.AvgEngagementScore
    -- 👉 The social media metrics have already been compiled.

FROM CurrencySummary cs
LEFT JOIN SocialEngagementSummary ses
    ON cs.CurrencyKey = ses.CurrencyKey;
    -- 👉 Join theo CurrencyKey
    -- 👉 Left Join allows you to retain your currency even without social data.

-- ============================================
-- View: Time Series
-- ============================================

DROP VIEW IF EXISTS vw_TimeSeries;

CREATE VIEW vw_TimeSeries AS
SELECT
    FullDate,
    Year,
    Month,
    MonthName,
    -- 👉 Timeline

    TotalPosts,
    ActiveCurrencies,
    TotalLikes,
    TotalComments,
    TotalRetweets,
    TotalImpressions,
    AvgEngagementScore,
    -- 👉 Daily social media metrics

    -- Derived metric
    (TotalLikes + TotalComments + TotalRetweets) AS TotalEngagements
    -- 👉 Total engagement, calculated directly in the view.

FROM DailySocialSummary;
   
-- ============================================
-- View: Social Analytics
-- ============================================

DROP VIEW IF EXISTS vw_SocialAnalytics;

CREATE VIEW vw_SocialAnalytics AS
SELECT 
    dc.Symbol,
    dsp.PlatformName,
    -- 👉 Currency + Platform

    ses.TotalEngagements,
    ses.TotalLikes,
    ses.TotalRetweets,
    ses.AvgEngagementScore,
    ses.LastEngagement
    -- 👉 Social metrics by platform

FROM SocialEngagementSummary ses
JOIN DimCurrency dc ON ses.CurrencyKey = dc.CurrencyKey
JOIN DimPlatform dsp ON ses.PlatformName = dsp.PlatformName;