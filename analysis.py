import pandas as pd
import numpy as np

# ============================================================
# 1. CONFIGURATION
# ============================================================

FILE_PATH = "BrightChamps_FDA_Case_Dataset.csv"

REVENUE_PER_CONVERSION = 60000
MARKETING_COST_PER_LEAD = 900

# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv(FILE_PATH)

print("=" * 70)
print("BRIGHTCHAMPS FDA CASE - DATA ANALYSIS")
print("=" * 70)

print("\nDataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())


# ============================================================
# 3. DATA QUALITY CHECK
# ============================================================

print("\n" + "=" * 70)
print("DATA QUALITY")
print("=" * 70)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nUnique leads:")
print(df["lead_id"].nunique())


# ============================================================
# 4. DATETIME CONVERSION
# ============================================================

df["created_at"] = pd.to_datetime(
    df["created_at"],
    errors="coerce"
)

df["demo_scheduled_at"] = pd.to_datetime(
    df["demo_scheduled_at"],
    errors="coerce"
)


# ============================================================
# 5. BASIC FUNNEL ANALYSIS
# ============================================================

total_leads = len(df)

demo_scheduled = df["demo_scheduled_at"].notna().sum()

demo_joined = (
    df["demo_joined"]
    .astype(str)
    .str.upper()
    .eq("Y")
    .sum()
)

demo_completed = (
    df["demo_completed"]
    .astype(str)
    .str.upper()
    .eq("Y")
    .sum()
)

converted = (
    df["converted"]
    .astype(str)
    .str.upper()
    .eq("Y")
    .sum()
)


print("\n" + "=" * 70)
print("FUNNEL")
print("=" * 70)

print(f"Leads              : {total_leads:,}")
print(f"Demo scheduled     : {demo_scheduled:,}")
print(f"Demo joined        : {demo_joined:,}")
print(f"Demo completed     : {demo_completed:,}")
print(f"Converted          : {converted:,}")


# ============================================================
# 6. FUNNEL CONVERSION RATES
# ============================================================

lead_to_scheduled = demo_scheduled / total_leads

scheduled_to_joined = demo_joined / demo_scheduled

joined_to_completed = demo_completed / demo_joined

completed_to_converted = converted / demo_completed

scheduled_to_converted = converted / demo_scheduled

lead_to_converted = converted / total_leads


print("\n" + "=" * 70)
print("CONVERSION RATES")
print("=" * 70)

print(f"Lead → Scheduled       : {lead_to_scheduled:.2%}")
print(f"Scheduled → Joined     : {scheduled_to_joined:.2%}")
print(f"Joined → Completed     : {joined_to_completed:.2%}")
print(f"Completed → Converted  : {completed_to_converted:.2%}")
print(f"Scheduled → Converted  : {scheduled_to_converted:.2%}")
print(f"Lead → Converted       : {lead_to_converted:.2%}")


# ============================================================
# 7. NUMBER LOST AT EACH STAGE
# ============================================================

lost_before_scheduling = total_leads - demo_scheduled

no_shows = demo_scheduled - demo_joined

incomplete_demos = demo_joined - demo_completed

not_converted = demo_completed - converted


print("\n" + "=" * 70)
print("FUNNEL DROP-OFF")
print("=" * 70)

print(f"Leads not scheduled       : {lost_before_scheduling:,}")
print(f"Scheduled but didn't join : {no_shows:,}")
print(f"Joined but didn't complete: {incomplete_demos:,}")
print(f"Completed but didn't buy  : {not_converted:,}")


# ============================================================
# 8. MONEY ANALYSIS
# ============================================================

total_revenue = converted * REVENUE_PER_CONVERSION

total_marketing_cost = total_leads * MARKETING_COST_PER_LEAD

net_after_marketing = total_revenue - total_marketing_cost


print("\n" + "=" * 70)
print("MONEY ANALYSIS")
print("=" * 70)

print(f"Revenue generated       : ₹{total_revenue:,.0f}")
print(f"Marketing cost          : ₹{total_marketing_cost:,.0f}")
print(f"Revenue - marketing     : ₹{net_after_marketing:,.0f}")


# ============================================================
# 9. REVENUE OPPORTUNITY BY FUNNEL LEAK
# ============================================================

# If the people lost at a particular stage behaved like
# the population entering that stage, estimate the downstream
# revenue opportunity.

# ----------------------------
# Scheduled → Joined
# ----------------------------

no_show_revenue_opportunity = (
    no_shows
    * scheduled_to_converted
    * REVENUE_PER_CONVERSION
)

# ----------------------------
# Joined → Completed
# ----------------------------

incomplete_revenue_opportunity = (
    incomplete_demos
    * joined_to_completed
    * completed_to_converted
    * REVENUE_PER_CONVERSION
)

# ----------------------------
# Completed → Converted
# ----------------------------

non_conversion_opportunity = (
    not_converted
    * completed_to_converted
    * REVENUE_PER_CONVERSION
)


print("\n" + "=" * 70)
print("REVENUE OPPORTUNITY")
print("=" * 70)

print(
    f"Scheduled → Joined leak : "
    f"₹{no_show_revenue_opportunity:,.0f}"
)

print(
    f"Joined → Completed leak : "
    f"₹{incomplete_revenue_opportunity:,.0f}"
)

print(
    f"Completed → Conversion leak : "
    f"₹{non_conversion_opportunity:,.0f}"
)


# ============================================================
# 10. MONTHLY NORMALIZATION
# ============================================================

# Dataset covers approximately two months according to the case.

MONTHS = 2

monthly_revenue = total_revenue / MONTHS
monthly_marketing_cost = total_marketing_cost / MONTHS

monthly_no_show_opportunity = (
    no_show_revenue_opportunity / MONTHS
)

monthly_incomplete_opportunity = (
    incomplete_revenue_opportunity / MONTHS
)

monthly_conversion_opportunity = (
    non_conversion_opportunity / MONTHS
)


print("\n" + "=" * 70)
print("MONTHLY VIEW")
print("=" * 70)

print(f"Revenue/month                 : ₹{monthly_revenue:,.0f}")
print(f"Marketing cost/month          : ₹{monthly_marketing_cost:,.0f}")
print(
    f"No-show opportunity/month     : "
    f"₹{monthly_no_show_opportunity:,.0f}"
)
print(
    f"Demo completion opportunity/month : "
    f"₹{monthly_incomplete_opportunity:,.0f}"
)
print(
    f"Conversion opportunity/month  : "
    f"₹{monthly_conversion_opportunity:,.0f}"
)


# ============================================================
# 11. LEAK COMPARISON
# ============================================================

leak_analysis = pd.DataFrame({
    "Leak": [
        "Lead → Demo Scheduled",
        "Demo Scheduled → Demo Joined",
        "Demo Joined → Demo Completed",
        "Demo Completed → Converted"
    ],

    "Leads Lost": [
        lost_before_scheduling,
        no_shows,
        incomplete_demos,
        not_converted
    ],

    "Revenue Opportunity": [
        np.nan,
        no_show_revenue_opportunity,
        incomplete_revenue_opportunity,
        non_conversion_opportunity
    ]
})


print("\n" + "=" * 70)
print("LEAK COMPARISON")
print("=" * 70)

print(
    leak_analysis.to_string(index=False)
)


# ============================================================
# 12. NO-SHOW ANALYSIS BY LEAD SOURCE
# ============================================================

scheduled_df = df[
    df["demo_scheduled_at"].notna()
].copy()

scheduled_df["joined_flag"] = (
    scheduled_df["demo_joined"]
    .astype(str)
    .str.upper()
    .eq("Y")
)

source_analysis = (
    scheduled_df
    .groupby("lead_source")
    .agg(
        scheduled=("lead_id", "count"),
        joined=("joined_flag", "sum")
    )
)

source_analysis["no_shows"] = (
    source_analysis["scheduled"]
    - source_analysis["joined"]
)

source_analysis["join_rate"] = (
    source_analysis["joined"]
    / source_analysis["scheduled"]
)

source_analysis["no_show_rate"] = (
    source_analysis["no_shows"]
    / source_analysis["scheduled"]
)

source_analysis = source_analysis.sort_values(
    "no_show_rate",
    ascending=False
)


print("\n" + "=" * 70)
print("NO-SHOW ANALYSIS BY LEAD SOURCE")
print("=" * 70)

print(source_analysis)


# ============================================================
# 13. NO-SHOW ANALYSIS BY GEOGRAPHY
# ============================================================

geo_analysis = (
    scheduled_df
    .groupby("geography")
    .agg(
        scheduled=("lead_id", "count"),
        joined=("joined_flag", "sum")
    )
)

geo_analysis["no_shows"] = (
    geo_analysis["scheduled"]
    - geo_analysis["joined"]
)

geo_analysis["join_rate"] = (
    geo_analysis["joined"]
    / geo_analysis["scheduled"]
)

geo_analysis["no_show_rate"] = (
    geo_analysis["no_shows"]
    / geo_analysis["scheduled"]
)

geo_analysis = geo_analysis.sort_values(
    "no_show_rate",
    ascending=False
)


print("\n" + "=" * 70)
print("NO-SHOW ANALYSIS BY GEOGRAPHY")
print("=" * 70)

print(geo_analysis)


# ============================================================
# 14. NO-SHOW ANALYSIS BY REP
# ============================================================

rep_analysis = (
    scheduled_df
    .groupby("rep_assigned")
    .agg(
        scheduled=("lead_id", "count"),
        joined=("joined_flag", "sum")
    )
)

rep_analysis["no_shows"] = (
    rep_analysis["scheduled"]
    - rep_analysis["joined"]
)

rep_analysis["no_show_rate"] = (
    rep_analysis["no_shows"]
    / rep_analysis["scheduled"]
)

rep_analysis = rep_analysis.sort_values(
    "no_show_rate",
    ascending=False
)


print("\n" + "=" * 70)
print("NO-SHOW ANALYSIS BY REP")
print("=" * 70)

print(rep_analysis)


# ============================================================
# 15. FOLLOW-UP ATTEMPT ANALYSIS
# ============================================================

followup_analysis = (
    scheduled_df
    .groupby("follow_up_attempts")
    .agg(
        scheduled=("lead_id", "count"),
        joined=("joined_flag", "sum")
    )
)

followup_analysis["no_shows"] = (
    followup_analysis["scheduled"]
    - followup_analysis["joined"]
)

followup_analysis["no_show_rate"] = (
    followup_analysis["no_shows"]
    / followup_analysis["scheduled"]
)


print("\n" + "=" * 70)
print("FOLLOW-UP ATTEMPTS VS NO-SHOW")
print("=" * 70)

print(followup_analysis)


# ============================================================
# 16. NO-SHOW RECOVERY QUEUE
# ============================================================

recovery_queue = scheduled_df[
    scheduled_df["joined_flag"] == False
].copy()

# Prioritize leads with fewer existing attempts.
recovery_queue = recovery_queue.sort_values(
    by=["follow_up_attempts", "demo_scheduled_at"]
)

print("\n" + "=" * 70)
print("NO-SHOW RECOVERY QUEUE")
print("=" * 70)

print(
    recovery_queue[
        [
            "lead_id",
            "lead_source",
            "geography",
            "parent_timezone",
            "demo_scheduled_at",
            "rep_assigned",
            "rep_shift",
            "follow_up_attempts"
        ]
    ].head(20)
)


# ============================================================
# 17. SAVE ANALYSIS OUTPUTS
# ============================================================

leak_analysis.to_csv(
    "funnel_leak_analysis.csv",
    index=False
)

source_analysis.to_csv(
    "no_show_by_source.csv"
)

geo_analysis.to_csv(
    "no_show_by_geography.csv"
)

rep_analysis.to_csv(
    "no_show_by_rep.csv"
)

followup_analysis.to_csv(
    "no_show_by_followup_attempts.csv"
)

recovery_queue.to_csv(
    "demo_recovery_queue.csv",
    index=False
)


# ============================================================
# 18. FINAL EXECUTIVE SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("EXECUTIVE SUMMARY")
print("=" * 70)

print(f"""
Total leads: {total_leads:,}

Funnel:
    Scheduled : {demo_scheduled:,} ({lead_to_scheduled:.2%})
    Joined    : {demo_joined:,} ({scheduled_to_joined:.2%})
    Completed : {demo_completed:,} ({joined_to_completed:.2%})
    Converted : {converted:,} ({completed_to_converted:.2%})

Largest operational leak:
    Scheduled → Joined

    Scheduled demos : {demo_scheduled:,}
    No-shows         : {no_shows:,}
    No-show rate     : {no_shows / demo_scheduled:.2%}

Estimated revenue opportunity:
    Two months : ₹{no_show_revenue_opportunity:,.0f}
    Per month  : ₹{monthly_no_show_opportunity:,.0f}

Recommended intervention:
    Two-touch reminder + immediate no-show recovery workflow
    + rep recovery queue.

The opportunity figure is an estimate, not realized lost revenue.
It assumes no-show leads convert at the observed
scheduled → conversion rate.
""")

print("\nAnalysis complete.")