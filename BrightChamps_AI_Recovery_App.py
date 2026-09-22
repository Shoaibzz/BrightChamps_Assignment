
import os
from pathlib import Path
import pandas as pd
import streamlit as st

# Optional Gemini integration. The app still works without an API key using a safe fallback template.
try:
    from google import genai
except ImportError:
    genai = None

st.set_page_config(
    page_title="BrightChamps Demo Recovery AI",
    page_icon="🎯",
    layout="wide"
)

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

REVENUE_PER_CONVERSION = 60000
MARKETING_COST_PER_LEAD = 900
MONTHS_IN_DATASET = 2

st.title("🎯 BrightChamps — Demo Recovery AI")
st.caption(
    "Prototype for the proposed two-week intervention: recover scheduled-but-not-joined demos "
    "using an AI-assisted recovery queue and personalized follow-up."
)

# -------------------------------------------------------------------
# Data loading
# -------------------------------------------------------------------
DEFAULT_FILE = "BrightChamps_FDA_Case_Dataset(5).csv"

@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    data["created_at"] = pd.to_datetime(data["created_at"], errors="coerce")
    data["demo_scheduled_at"] = pd.to_datetime(
        data["demo_scheduled_at"], errors="coerce"
    )
    data["joined_flag"] = (
        data["demo_joined"].astype(str).str.upper().eq("Y")
    )
    data["completed_flag"] = (
        data["demo_completed"].astype(str).str.upper().eq("Y")
    )
    data["converted_flag"] = (
        data["converted"].astype(str).str.upper().eq("Y")
    )
    return data

uploaded = st.sidebar.file_uploader(
    "Upload case CSV",
    type=["csv"],
    help="Use the BrightChamps FDA case dataset."
)

if uploaded is not None:
    df = load_data(uploaded)
else:
    local_path = Path(DEFAULT_FILE)
    if not local_path.exists():
        st.error(
            f"Place {DEFAULT_FILE} in the same folder as this app, "
            "or upload the CSV from the sidebar."
        )
        st.stop()
    df = load_data(local_path)

# -------------------------------------------------------------------
# Funnel calculations
# -------------------------------------------------------------------
total_leads = len(df)
scheduled = int(df["demo_scheduled_at"].notna().sum())
joined = int(df["joined_flag"].sum())
completed = int(df["completed_flag"].sum())
converted = int(df["converted_flag"].sum())

no_shows = scheduled - joined
incomplete = joined - completed
not_converted = completed - converted

scheduled_to_joined = joined / scheduled if scheduled else 0
joined_to_completed = completed / joined if joined else 0
completed_to_converted = converted / completed if completed else 0
scheduled_to_converted = converted / scheduled if scheduled else 0

no_show_opportunity_2m = (
    no_shows * scheduled_to_converted * REVENUE_PER_CONVERSION
)
no_show_opportunity_month = no_show_opportunity_2m / MONTHS_IN_DATASET

# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------
st.sidebar.header("Controls")

api_key_present = bool(GEMINI_API_KEY)
if api_key_present:
    st.sidebar.success("Gemini AI: connected")
else:
    st.sidebar.info(
        "Gemini AI: not connected. The app uses a safe fallback message. "
        "Set GEMINI_API_KEY to enable live AI generation."
    )

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Intervention:**\n"
    "1. Prioritize scheduled-but-not-joined leads\n"
    "2. Generate a concise recovery message\n"
    "3. Route the lead to the existing rep\n"
    "4. Track reschedule / join / conversion outcomes"
)

# -------------------------------------------------------------------
# Dashboard
# -------------------------------------------------------------------
st.header("1. Funnel & money baseline")

cols = st.columns(5)
cols[0].metric("Leads", f"{total_leads:,}")
cols[1].metric("Scheduled", f"{scheduled:,}")
cols[2].metric("Joined", f"{joined:,}")
cols[3].metric("Completed", f"{completed:,}")
cols[4].metric("Converted", f"{converted:,}")

st.dataframe(
    pd.DataFrame({
        "Stage": [
            "Leads",
            "Demo scheduled",
            "Demo joined",
            "Demo completed",
            "Converted"
        ],
        "Count": [
            total_leads,
            scheduled,
            joined,
            completed,
            converted
        ],
        "Conversion from previous stage": [
            "-",
            f"{scheduled / total_leads:.2%}" if total_leads else "-",
            f"{joined / scheduled:.2%}" if scheduled else "-",
            f"{completed / joined:.2%}" if joined else "-",
            f"{converted / completed:.2%}" if completed else "-"
        ]
    }),
    use_container_width=True,
    hide_index=True
)

money1, money2, money3 = st.columns(3)
money1.metric(
    "Revenue generated",
    f"₹{converted * REVENUE_PER_CONVERSION / 100000:.1f}L"
)
money2.metric(
    "Marketing cost",
    f"₹{total_leads * MARKETING_COST_PER_LEAD / 100000:.1f}L"
)
money3.metric(
    "No-show opportunity / month",
    f"₹{no_show_opportunity_month / 100000:.1f}L"
)

st.info(
    f"The scheduled→joined leak contains {no_shows:,} no-shows "
    f"({1 - scheduled_to_joined:.2%} of scheduled demos). "
    f"Using the observed scheduled→conversion rate of "
    f"{scheduled_to_converted:.2%}, the estimated gross revenue opportunity "
    f"is ₹{no_show_opportunity_month / 100000:.1f}L/month. "
    "This is an opportunity estimate, not realized lost revenue."
)

# -------------------------------------------------------------------
# Segment diagnostics
# -------------------------------------------------------------------
st.header("2. Where is the leak concentrated?")

scheduled_df = df[df["demo_scheduled_at"].notna()].copy()

tab1, tab2, tab3, tab4 = st.tabs(
    ["Lead source", "Geography", "Rep", "Follow-up attempts"]
)

with tab1:
    x = scheduled_df.groupby("lead_source").agg(
        scheduled=("lead_id", "count"),
        joined=("joined_flag", "sum")
    )
    x["no_shows"] = x["scheduled"] - x["joined"]
    x["no_show_rate"] = x["no_shows"] / x["scheduled"]
    st.dataframe(
        x.sort_values("no_show_rate", ascending=False),
        use_container_width=True
    )

with tab2:
    x = scheduled_df.groupby("geography").agg(
        scheduled=("lead_id", "count"),
        joined=("joined_flag", "sum")
    )
    x["no_shows"] = x["scheduled"] - x["joined"]
    x["no_show_rate"] = x["no_shows"] / x["scheduled"]
    st.dataframe(
        x.sort_values("no_show_rate", ascending=False),
        use_container_width=True
    )

with tab3:
    x = scheduled_df.groupby("rep_assigned").agg(
        scheduled=("lead_id", "count"),
        joined=("joined_flag", "sum")
    )
    x["no_shows"] = x["scheduled"] - x["joined"]
    x["no_show_rate"] = x["no_shows"] / x["scheduled"]
    st.dataframe(
        x.sort_values("no_show_rate", ascending=False),
        use_container_width=True
    )

with tab4:
    x = scheduled_df.groupby("follow_up_attempts").agg(
        scheduled=("lead_id", "count"),
        joined=("joined_flag", "sum")
    )
    x["no_shows"] = x["scheduled"] - x["joined"]
    x["no_show_rate"] = x["no_shows"] / x["scheduled"]
    st.dataframe(
        x.sort_index(),
        use_container_width=True
    )

# -------------------------------------------------------------------
# AI recovery queue
# -------------------------------------------------------------------
st.header("3. AI-assisted recovery queue")

queue = scheduled_df[~scheduled_df["joined_flag"]].copy()

# Operational priority, deliberately transparent rather than pretending this is a trained ML model.
# Lower previous attempts means the lead has more room for a useful recovery touch.
queue["priority_score"] = (
    100
    - queue["follow_up_attempts"].fillna(0).clip(lower=0) * 15
)

queue = queue.sort_values(
    ["priority_score", "demo_scheduled_at"],
    ascending=[False, True]
)

display_cols = [
    "lead_id",
    "lead_source",
    "geography",
    "parent_timezone",
    "demo_scheduled_at",
    "rep_assigned",
    "rep_shift",
    "follow_up_attempts",
    "priority_score"
]

st.dataframe(
    queue[display_cols].head(100),
    use_container_width=True,
    hide_index=True
)

if len(queue) == 0:
    st.success("No scheduled-but-not-joined leads in the current data.")
    st.stop()

selected_id = st.selectbox(
    "Select a no-show lead to recover",
    queue["lead_id"].astype(str).tolist()
)

lead = queue[queue["lead_id"].astype(str) == str(selected_id)].iloc[0]

c1, c2, c3 = st.columns(3)
c1.write(f"**Lead source:** {lead['lead_source']}")
c2.write(f"**Geography:** {lead['geography']}")
c3.write(f"**Parent timezone:** {lead['parent_timezone']}")

c1, c2, c3 = st.columns(3)
c1.write(f"**Scheduled:** {lead['demo_scheduled_at']}")
c2.write(f"**Rep:** {lead['rep_assigned']}")
c3.write(f"**Previous attempts:** {int(lead['follow_up_attempts'])}")

# -------------------------------------------------------------------
# AI generation
# -------------------------------------------------------------------
st.subheader("AI recovery message")

def fallback_message(row):
    attempts = int(row["follow_up_attempts"])
    if attempts >= 3:
        return (
            "Hi,\n\n"
            "We noticed we missed you for your scheduled demo. "
            "If you would still like to continue, reply with a convenient "
            "time and we can help arrange the next available slot.\n\n"
            "Thank you,\nBrightChamps Team"
        )

    return (
        "Hi,\n\n"
        "Looks like we missed you for your scheduled demo. "
        "If you would still like to continue, reply with a convenient "
        "time and we will help arrange a new slot.\n\n"
        "Thank you,\nBrightChamps Team"
    )

def generate_with_gemini(row):
    if not genai or not api_key_present:
        return fallback_message(row)

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    prompt = f"""
You are a demo-recovery assistant for BrightChamps.

Goal:
Recover a scheduled demo that the parent did not join.

Lead information:
- Lead source: {row["lead_source"]}
- Geography: {row["geography"]}
- Parent timezone: {row["parent_timezone"]}
- Scheduled demo: {row["demo_scheduled_at"]}
- Rep: {row["rep_assigned"]}
- Rep shift: {row["rep_shift"]}
- Previous follow-up attempts: {row["follow_up_attempts"]}

Write ONE concise, natural WhatsApp/SMS-style message.

Rules:
1. Be polite and non-judgmental.
2. Acknowledge that the scheduled demo was missed.
3. Ask for a convenient time to reschedule.
4. Do not invent the parent's name, child's name, reason for absence,
   price, discount, offer, or availability.
5. Do not mention internal lead scoring or analytics.
6. If previous attempts are high, make the message less repetitive.
7. Keep it under 55 words.
8. Return only the message.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()

if st.button("✨ Generate AI recovery message", type="primary"):
    with st.spinner("Generating..."):
        message = generate_with_gemini(lead)
    st.session_state["recovery_message"] = message

message = st.session_state.get(
    "recovery_message",
    fallback_message(lead)
)

st.text_area(
    "Message",
    value=message,
    height=150
)

a, b, c = st.columns(3)
if a.button("📌 Queue for rep"):
    st.success(
        f"Lead {selected_id} queued for {lead['rep_assigned']}."
    )

if b.button("🔁 Mark reschedule requested"):
    st.success(
        f"Lead {selected_id}: reschedule requested. "
        "In production, this event would be written back to CRM."
    )

if c.button("✅ Mark recovered"):
    st.success(
        f"Lead {selected_id}: recovered. "
        "In production, this would trigger downstream tracking."
    )

# -------------------------------------------------------------------
# Intervention simulator
# -------------------------------------------------------------------
st.header("4. Intervention sensitivity")

recovery_pct = st.slider(
    "Assumed recovery of no-shows",
    min_value=0,
    max_value=30,
    value=10,
    step=1
)

extra_conversions = (
    no_shows
    * recovery_pct / 100
    * scheduled_to_converted
)

extra_revenue_month = (
    extra_conversions
    * REVENUE_PER_CONVERSION
    / MONTHS_IN_DATASET
)

x, y = st.columns(2)
x.metric("Illustrative extra conversions", f"{extra_conversions:.1f}")
y.metric(
    "Illustrative gross revenue / month",
    f"₹{extra_revenue_month / 100000:.2f}L"
)

st.caption(
    "Sensitivity only — not a forecast. The assumed recovery percentage "
    "must be validated through a controlled rollout."
)

# -------------------------------------------------------------------
# Measurement
# -------------------------------------------------------------------
st.header("5. Experiment measurement")

st.markdown(
    """
**Primary metric:** scheduled → joined rate

**Secondary metrics:** reschedule rate, demo completion rate,
completed-demo → conversion rate, incremental conversions, revenue per
1,000 scheduled demos.

**Guardrail:** do not improve joining at the expense of downstream
conversion quality.

**Recommended rollout:** hold out a comparable control group and compare
the recovery workflow against the existing process.
"""
)

st.success(
    "Prototype logic: identify the leak → prioritize recoverable no-shows → "
    "use AI for message generation → route to existing reps → measure "
    "incremental recovery."
)
