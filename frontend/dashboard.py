
from __future__ import annotations

from datetime import datetime
from textwrap import dedent
from typing import Any

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# =========================================================
# CONFIGURATION
# =========================================================

API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 10

st.set_page_config(
    page_title="Internship Coordinator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# PROFESSIONAL LIGHT THEME
# =========================================================

st.markdown(
    """
    <style>
    :root {
        --page-bg: #f4f7fb;
        --sidebar-bg: #ffffff;
        --surface: #ffffff;
        --surface-soft: #f8fafc;
        --surface-hover: #eef2ff;
        --border: #e2e8f0;

        --text-primary: #172033;
        --text-secondary: #526079;
        --text-muted: #8a97aa;

        --primary: #5368e8;
        --primary-hover: #4055d6;
        --primary-soft: #eef0ff;

        --success: #16a66a;
        --success-soft: #e8f8f0;

        --warning: #e69222;
        --warning-soft: #fff4df;

        --danger: #e05252;
        --danger-soft: #fdecec;

        --info: #2698d4;
        --info-soft: #e8f5fc;

        --purple: #8b5cf6;
        --purple-soft: #f2edff;
    }

    html, body, [class*="css"] {
        font-family:
            Inter,
            ui-sans-serif,
            system-ui,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at top right,
                rgba(83, 104, 232, 0.07),
                transparent 30%
            ),
            var(--page-bg);
        color: var(--text-primary);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: var(--sidebar-bg);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.25rem;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 2.25rem;
        padding-right: 2.25rem;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
    }

    .app-header {
        margin-bottom: 1.8rem;
    }

    .app-title {
        color: var(--text-primary);
        font-size: 2.15rem;
        line-height: 1.2;
        font-weight: 800;
        letter-spacing: -0.04em;
        margin-bottom: 0.45rem;
    }

    .app-subtitle {
        color: var(--text-secondary);
        font-size: 0.96rem;
        line-height: 1.65;
        max-width: 880px;
    }

    .eyebrow {
        color: var(--primary);
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        margin-bottom: 0.55rem;
    }

    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: end;
        gap: 1rem;
        margin-top: 1.8rem;
        margin-bottom: 1rem;
    }

    .section-title {
        color: var(--text-primary);
        font-size: 1.2rem;
        font-weight: 800;
        letter-spacing: -0.015em;
    }

    .section-subtitle {
        color: var(--text-muted);
        font-size: 0.82rem;
        margin-top: 0.25rem;
    }

    .metric-card {
        position: relative;
        overflow: hidden;
        min-height: 142px;
        padding: 1.2rem 1.25rem;
        border: 1px solid var(--border);
        border-radius: 18px;
        background: var(--surface);
        box-shadow: 0 10px 28px rgba(31, 45, 75, 0.07);
    }

    .metric-card::after {
        content: "";
        position: absolute;
        width: 92px;
        height: 92px;
        border-radius: 999px;
        right: -32px;
        top: -34px;
        background: var(--card-accent-soft);
    }

    .metric-top {
        position: relative;
        z-index: 2;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }

    .metric-icon {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 38px;
        height: 38px;
        border-radius: 12px;
        color: var(--card-accent);
        background: var(--card-accent-soft);
        font-size: 1rem;
        font-weight: 800;
    }

    .metric-label {
        color: var(--text-secondary);
        font-size: 0.78rem;
        font-weight: 700;
    }

    .metric-value {
        position: relative;
        z-index: 2;
        color: var(--text-primary);
        font-size: 2rem;
        line-height: 1;
        font-weight: 850;
        letter-spacing: -0.045em;
    }

    .metric-note {
        position: relative;
        z-index: 2;
        color: var(--text-muted);
        font-size: 0.74rem;
        margin-top: 0.6rem;
    }

    .surface-card,
    .detail-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1.3rem;
        box-shadow: 0 10px 28px rgba(31, 45, 75, 0.06);
    }

    .detail-card {
        min-height: 100%;
    }

    .detail-title {
        color: var(--text-primary);
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 1.15rem;
    }

    .detail-label {
        color: var(--text-muted);
        font-size: 0.69rem;
        font-weight: 800;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }

    .detail-value {
        color: var(--text-primary);
        font-size: 0.9rem;
        font-weight: 650;
        margin-bottom: 1rem;
        overflow-wrap: anywhere;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        width: fit-content;
        padding: 0.4rem 0.72rem;
        border-radius: 999px;
        border: 1px solid transparent;
        font-size: 0.7rem;
        line-height: 1;
        font-weight: 800;
    }

    .badge-success {
        color: #08784a;
        background: var(--success-soft);
        border-color: #bcebd6;
    }

    .badge-warning {
        color: #a85c05;
        background: var(--warning-soft);
        border-color: #f5d9a6;
    }

    .badge-danger {
        color: #b52f2f;
        background: var(--danger-soft);
        border-color: #f3c2c2;
    }

    .badge-info {
        color: #176b96;
        background: var(--info-soft);
        border-color: #b8e2f4;
    }

    .badge-purple {
        color: #6540bd;
        background: var(--purple-soft);
        border-color: #dcd0fb;
    }

    .badge-neutral {
        color: #5e6b80;
        background: #f1f5f9;
        border-color: #dbe3ec;
    }

    .recommendation-box {
        padding: 1rem;
        border-radius: 14px;
        background: var(--surface-soft);
        border: 1px solid var(--border);
        color: var(--text-secondary);
        font-size: 0.86rem;
        line-height: 1.65;
        margin-top: 0.9rem;
        margin-bottom: 1rem;
    }

    .audit-card {
        display: grid;
        grid-template-columns: 42px minmax(0, 1fr);
        gap: 0.9rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 7px 20px rgba(31, 45, 75, 0.04);
    }

    .audit-icon {
        width: 38px;
        height: 38px;
        border-radius: 12px;
        display: flex;
        justify-content: center;
        align-items: center;
        color: var(--primary);
        background: var(--primary-soft);
        font-size: 0.9rem;
        font-weight: 800;
    }

    .audit-agent {
        color: var(--text-primary);
        font-weight: 800;
        font-size: 0.84rem;
        margin-bottom: 0.35rem;
    }

    .audit-message {
        color: var(--text-secondary);
        font-size: 0.78rem;
        line-height: 1.55;
    }

    .sidebar-brand {
        padding: 0.4rem 0.2rem 1.2rem;
    }

    .sidebar-title {
        color: var(--text-primary);
        font-size: 1.08rem;
        font-weight: 850;
    }

    .sidebar-subtitle {
        color: var(--text-muted);
        font-size: 0.73rem;
        margin-top: 0.3rem;
    }

    .backend-box {
        background: #f8fafc;
        border: 1px solid var(--border);
        border-radius: 13px;
        padding: 0.85rem;
        margin-top: 0.55rem;
    }

    .backend-label {
        color: var(--text-muted);
        font-size: 0.68rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .backend-value {
        color: #168a76;
        font-size: 0.76rem;
        font-family: "SFMono-Regular", Consolas, monospace;
        margin-top: 0.4rem;
    }

    .footer {
        color: var(--text-muted);
        text-align: center;
        font-size: 0.72rem;
        padding-top: 2.5rem;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 15px;
        overflow: hidden;
        background: var(--surface);
    }

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] > div > div {
        background: var(--surface) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 11px !important;
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 1px var(--primary) !important;
    }

    [data-testid="stRadio"] p {
        color: var(--text-secondary);
        font-size: 0.85rem;
    }

    .stButton > button {
        width: 100%;
        min-height: 44px;
        border-radius: 11px;
        border: 1px solid var(--border);
        background: var(--surface);
        color: var(--text-primary);
        font-weight: 750;
        transition: 0.16s ease;
    }

    .stButton > button:hover {
        background: var(--surface-hover);
        border-color: var(--primary);
        color: var(--primary);
        transform: translateY(-1px);
    }

    button[kind="primary"] {
        background: linear-gradient(135deg, #5368e8, #7c5ce3) !important;
        border: none !important;
        color: white !important;
    }

    [data-testid="stAlert"] {
        border-radius: 13px;
    }

    hr {
        border-color: var(--border) !important;
    }

    @media (max-width: 950px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .app-title {
            font-size: 1.7rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# API HELPERS
# =========================================================

def api_get(path: str) -> Any:
    response = requests.get(
        f"{API_BASE_URL}{path}",
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict[str, Any]) -> Any:
    response = requests.post(
        f"{API_BASE_URL}{path}",
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=20, show_spinner=False)
def get_cases() -> list[dict[str, Any]]:
    return api_get("/cases")


@st.cache_data(ttl=20, show_spinner=False)
def get_audit_logs(case_id: str) -> list[dict[str, Any]]:
    return api_get(f"/cases/{case_id}/audit-logs")


def approve_case(case_id: str, decision_by: str, note: str) -> dict[str, Any]:
    return api_post(
        f"/cases/{case_id}/approve",
        {"decision_by": decision_by, "note": note},
    )


def reject_case(case_id: str, decision_by: str, note: str) -> dict[str, Any]:
    return api_post(
        f"/cases/{case_id}/reject",
        {"decision_by": decision_by, "note": note},
    )


def request_clarification(
    case_id: str,
    decision_by: str,
    note: str,
) -> dict[str, Any]:
    return api_post(
        f"/cases/{case_id}/request-clarification",
        {"decision_by": decision_by, "note": note},
    )


# =========================================================
# UI HELPERS
# =========================================================

def safe(value: Any, fallback: str = "—") -> str:
    if value is None:
        return fallback

    value_str = str(value).strip()
    return value_str if value_str else fallback


def format_datetime(value: Any) -> str:
    if not value:
        return "—"

    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.strftime("%d %b %Y · %H:%M")
    except (ValueError, TypeError):
        return str(value)


def normalize_label(value: Any) -> str:
    if not value:
        return "Not set"

    return str(value).replace("_", " ").title()


def badge_class(value: Any) -> str:
    text = str(value or "").upper()

    if any(word in text for word in ["APPROVE", "APPROVED", "COMPLETE"]):
        return "badge-success"

    if any(word in text for word in ["CLARIFICATION", "PENDING"]):
        return "badge-warning"

    if any(word in text for word in ["REJECT", "VIOLATION"]):
        return "badge-danger"

    if any(word in text for word in ["WAIT", "SUPERVISOR"]):
        return "badge-info"

    if any(word in text for word in ["REVIEW", "COORDINATOR"]):
        return "badge-purple"

    return "badge-neutral"


def render_badge(value: Any) -> None:
    st.markdown(
        (
            f"<span class='badge {badge_class(value)}'>"
            f"{normalize_label(value)}"
            "</span>"
        ),
        unsafe_allow_html=True,
    )


def render_metric(
    label: str,
    value: int,
    icon: str,
    note: str,
    accent: str,
    accent_soft: str,
) -> None:
    html = dedent(
        f"""
        <div
            class="metric-card"
            style="
                --card-accent: {accent};
                --card-accent-soft: {accent_soft};
            "
        >
            <div class="metric-top">
                <div class="metric-icon">{icon}</div>
                <div class="metric-label">{label}</div>
            </div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """
    ).strip()

    st.markdown(html, unsafe_allow_html=True)


def render_detail(label: str, value: Any) -> None:
    html = dedent(
        f"""
        <div class="detail-label">{label}</div>
        <div class="detail-value">{safe(value)}</div>
        """
    ).strip()

    st.markdown(html, unsafe_allow_html=True)


def clear_cache_and_rerun() -> None:
    get_cases.clear()
    get_audit_logs.clear()
    st.rerun()


def cases_to_dataframe(cases: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for case in cases:
        rows.append(
            {
                "Case ID": case.get("case_id"),
                "Student": case.get("student_name"),
                "Company": case.get("company_name"),
                "Recommendation": normalize_label(case.get("recommendation")),
                "Next Action": normalize_label(case.get("next_action")),
                "Final Decision": (
                    normalize_label(case.get("final_decision"))
                    if case.get("final_decision")
                    else "Pending"
                ),
                "Status": normalize_label(case.get("status")),
                "Created At": format_datetime(case.get("created_at")),
            }
        )

    return pd.DataFrame(rows)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-title">🎓 Internship Office</div>
            <div class="sidebar-subtitle">
                Agentic Coordination Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Workspace",
        ["Overview", "Case Review", "Audit Trail", "System"],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown(
        f"""
        <div class="backend-label">Backend connection</div>
        <div class="backend-box">
            <div class="backend-value">{API_BASE_URL}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    if st.button("↻ Refresh data"):
        clear_cache_and_rerun()

    st.caption("Human-in-the-loop workflow")


# =========================================================
# LOAD DATA
# =========================================================

try:
    cases = get_cases()

except requests.exceptions.ConnectionError:
    st.error(
        "The dashboard could not connect to the FastAPI backend. "
        "Start the backend with `uvicorn main:app --reload`."
    )
    st.stop()

except requests.exceptions.Timeout:
    st.error("The FastAPI backend did not respond in time.")
    st.stop()

except requests.exceptions.RequestException as exc:
    st.error(f"Backend request failed: {exc}")
    st.stop()


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="app-header">
        <div class="eyebrow">University Operations</div>
        <div class="app-title">Agentic Internship Coordinator</div>
        <div class="app-subtitle">
            Review internship applications, inspect agent decisions,
            monitor workflow status, and record final coordinator
            outcomes from one secure workspace.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# OVERVIEW PAGE
# =========================================================

if page == "Overview":
    total_cases = len(cases)

    pending_cases = sum(
        1 for case in cases if not case.get("final_decision")
    )

    approved_recommendations = sum(
        1 for case in cases if case.get("recommendation") == "APPROVE"
    )

    clarification_cases = sum(
        1
        for case in cases
        if case.get("recommendation") == "REQUEST_CLARIFICATION"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_metric(
            label="Total applications",
            value=total_cases,
            icon="▦",
            note="All processed cases",
            accent="#5368E8",
            accent_soft="#EEF0FF",
        )

    with c2:
        render_metric(
            label="Pending decisions",
            value=pending_cases,
            icon="◷",
            note="Require coordinator action",
            accent="#E69222",
            accent_soft="#FFF4DF",
        )

    with c3:
        render_metric(
            label="Approve recommendations",
            value=approved_recommendations,
            icon="✓",
            note="Validated by all agents",
            accent="#16A66A",
            accent_soft="#E8F8F0",
        )

    with c4:
        render_metric(
            label="Clarification required",
            value=clarification_cases,
            icon="?",
            note="Waiting for missing data",
            accent="#2698D4",
            accent_soft="#E8F5FC",
        )

    st.markdown(
        """
        <div class="section-header">
            <div>
                <div class="section-title">Application intelligence</div>
                <div class="section-subtitle">
                    Distribution of recommendations and case statuses
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chart_left, chart_right = st.columns([1, 1])

    if cases:
        recommendation_counts = (
            pd.Series(
                [
                    normalize_label(case.get("recommendation"))
                    for case in cases
                ]
            )
            .value_counts()
            .reset_index()
        )
        recommendation_counts.columns = ["Recommendation", "Cases"]

        status_counts = (
            pd.Series(
                [normalize_label(case.get("status")) for case in cases]
            )
            .value_counts()
            .reset_index()
        )
        status_counts.columns = ["Status", "Cases"]

        with chart_left:
            fig_recommendations = px.pie(
                recommendation_counts,
                values="Cases",
                names="Recommendation",
                hole=0.62,
                color_discrete_sequence=[
                    "#5368E8",
                    "#16A66A",
                    "#E69222",
                    "#E05252",
                    "#2698D4",
                ],
            )

            fig_recommendations.update_layout(
                title="Recommendation distribution",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#526079",
                title_font_color="#172033",
                title_font_size=15,
                legend_font_color="#526079",
                margin=dict(l=12, r=12, t=55, b=18),
                height=340,
            )

            fig_recommendations.update_traces(
                textposition="inside",
                textinfo="percent+label",
                marker=dict(
                    line=dict(color="#FFFFFF", width=3)
                ),
            )

            st.plotly_chart(
                fig_recommendations,
                use_container_width=True,
                config={"displayModeBar": False},
            )

        with chart_right:
            fig_status = px.bar(
                status_counts,
                x="Cases",
                y="Status",
                orientation="h",
                color="Cases",
                color_continuous_scale=[
                    "#CAD1FF",
                    "#7888EC",
                    "#5368E8",
                ],
            )

            fig_status.update_layout(
                title="Workflow status",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#526079",
                title_font_color="#172033",
                title_font_size=15,
                showlegend=False,
                coloraxis_showscale=False,
                margin=dict(l=12, r=12, t=55, b=18),
                height=340,
                xaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(82,96,121,0.10)",
                    zeroline=False,
                    color="#526079",
                ),
                yaxis=dict(showgrid=False, color="#526079"),
            )

            fig_status.update_traces(
                marker_line_width=0,
                hovertemplate=(
                    "<b>%{y}</b><br>Cases: %{x}<extra></extra>"
                ),
            )

            st.plotly_chart(
                fig_status,
                use_container_width=True,
                config={"displayModeBar": False},
            )

    else:
        st.info("No applications have been processed yet.")

    st.markdown(
        """
        <div class="section-header">
            <div>
                <div class="section-title">Recent applications</div>
                <div class="section-subtitle">
                    Search and inspect processed internship cases
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filter_col1, filter_col2 = st.columns([2.2, 1])

    with filter_col1:
        search_value = st.text_input(
            "Search applications",
            placeholder=(
                "Search by case ID, student, company, "
                "recommendation, or status"
            ),
            label_visibility="collapsed",
        )

    recommendation_options = sorted(
        {
            normalize_label(case.get("recommendation"))
            for case in cases
        }
    )

    with filter_col2:
        recommendation_filter = st.selectbox(
            "Recommendation filter",
            ["All recommendations"] + recommendation_options,
            label_visibility="collapsed",
        )

    dataframe = cases_to_dataframe(cases)

    if search_value and not dataframe.empty:
        search_lower = search_value.lower()
        dataframe = dataframe[
            dataframe.apply(
                lambda row: search_lower
                in " ".join(row.astype(str)).lower(),
                axis=1,
            )
        ]

    if (
        recommendation_filter != "All recommendations"
        and not dataframe.empty
    ):
        dataframe = dataframe[
            dataframe["Recommendation"] == recommendation_filter
        ]

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
        height=360,
        column_config={
            "Case ID": st.column_config.TextColumn(
                "Case ID", width="medium"
            ),
            "Student": st.column_config.TextColumn(
                "Student", width="medium"
            ),
            "Company": st.column_config.TextColumn(
                "Company", width="large"
            ),
            "Recommendation": st.column_config.TextColumn(
                "Recommendation", width="medium"
            ),
            "Next Action": st.column_config.TextColumn(
                "Next Action", width="large"
            ),
            "Final Decision": st.column_config.TextColumn(
                "Final Decision", width="medium"
            ),
            "Status": st.column_config.TextColumn(
                "Status", width="large"
            ),
            "Created At": st.column_config.TextColumn(
                "Created At", width="medium"
            ),
        },
    )


# =========================================================
# CASE REVIEW PAGE
# =========================================================

elif page == "Case Review":
    if not cases:
        st.info("No applications are available for review.")
        st.stop()

    case_options = {
        (
            f"{case.get('case_id')} · "
            f"{safe(case.get('student_name'))} · "
            f"{normalize_label(case.get('recommendation'))}"
        ): case.get("case_id")
        for case in cases
    }

    selected_label = st.selectbox(
        "Select an application",
        options=list(case_options.keys()),
    )

    selected_case_id = case_options[selected_label]

    selected_case = next(
        case
        for case in cases
        if case.get("case_id") == selected_case_id
    )

    st.markdown(
        """
        <div class="section-header">
            <div>
                <div class="section-title">Application review</div>
                <div class="section-subtitle">
                    Inspect extracted data and record a final decision
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    detail_left, detail_middle, detail_right = st.columns(
        [1, 1, 1.05]
    )

    with detail_left:
        st.markdown(
            "<div class='detail-card'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='detail-title'>Student details</div>",
            unsafe_allow_html=True,
        )

        render_detail("Case ID", selected_case.get("case_id"))
        render_detail("Student name", selected_case.get("student_name"))
        render_detail("Student ID", selected_case.get("student_id"))
        render_detail(
            "Student email",
            selected_case.get("student_email"),
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with detail_middle:
        st.markdown(
            "<div class='detail-card'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='detail-title'>Company details</div>",
            unsafe_allow_html=True,
        )

        render_detail("Company", selected_case.get("company_name"))
        render_detail(
            "Supervisor",
            selected_case.get("supervisor_name"),
        )
        render_detail(
            "Supervisor email",
            selected_case.get("supervisor_email"),
        )
        render_detail(
            "Internship period",
            (
                f"{safe(selected_case.get('internship_start_date'))}"
                f" → "
                f"{safe(selected_case.get('internship_end_date'))}"
            ),
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with detail_right:
        st.markdown(
            "<div class='detail-card'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='detail-title'>Agent assessment</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div class='detail-label'>Recommendation</div>",
            unsafe_allow_html=True,
        )
        render_badge(selected_case.get("recommendation"))

        st.markdown(
            """
            <div class="detail-label" style="margin-top: 1rem;">
                Next action
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_badge(selected_case.get("next_action"))

        st.markdown(
            """
            <div class="detail-label" style="margin-top: 1rem;">
                Current status
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_badge(selected_case.get("status"))

        st.markdown(
            (
                "<div class='recommendation-box'>"
                f"{safe(selected_case.get('recommendation_reason'))}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-header">
            <div>
                <div class="section-title">Human final decision</div>
                <div class="section-subtitle">
                    The agent recommendation is advisory.
                    A coordinator must record the final outcome.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    current_decision = selected_case.get("final_decision")

    if current_decision:
        st.success(
            (
                "Final decision: "
                f"{normalize_label(current_decision)} · "
                "Recorded by "
                f"{safe(selected_case.get('final_decision_by'))}"
            )
        )

        if selected_case.get("final_decision_note"):
            st.info(selected_case.get("final_decision_note"))
    else:
        st.warning(
            "This application is still waiting for a "
            "coordinator decision."
        )

    form_left, form_right = st.columns([0.8, 1.7])

    with form_left:
        decision_by = st.text_input(
            "Coordinator name",
            value="Internship Coordinator",
        )

    with form_right:
        decision_note = st.text_area(
            "Decision note",
            value=(
                "Application reviewed by the internship "
                "coordination office."
            ),
            height=110,
        )

    action1, action2, action3 = st.columns(3)

    with action1:
        approve_clicked = st.button(
            "✓ Approve application",
            type="primary",
        )

    with action2:
        reject_clicked = st.button("✕ Reject application")

    with action3:
        clarification_clicked = st.button(
            "? Request clarification"
        )

    if approve_clicked:
        try:
            result = approve_case(
                selected_case_id,
                decision_by,
                decision_note,
            )
            st.success(result["message"])
            clear_cache_and_rerun()
        except requests.exceptions.RequestException as exc:
            st.error(f"Could not approve case: {exc}")

    if reject_clicked:
        try:
            result = reject_case(
                selected_case_id,
                decision_by,
                decision_note,
            )
            st.error(result["message"])
            clear_cache_and_rerun()
        except requests.exceptions.RequestException as exc:
            st.error(f"Could not reject case: {exc}")

    if clarification_clicked:
        try:
            result = request_clarification(
                selected_case_id,
                decision_by,
                decision_note,
            )
            st.info(result["message"])
            clear_cache_and_rerun()
        except requests.exceptions.RequestException as exc:
            st.error(
                f"Could not request clarification: {exc}"
            )


# =========================================================
# AUDIT TRAIL PAGE
# =========================================================

elif page == "Audit Trail":
    if not cases:
        st.info("No applications are available.")
        st.stop()

    case_options = {
        (
            f"{case.get('case_id')} · "
            f"{safe(case.get('student_name'))}"
        ): case.get("case_id")
        for case in cases
    }

    selected_label = st.selectbox(
        "Select case",
        options=list(case_options.keys()),
    )

    selected_case_id = case_options[selected_label]

    st.markdown(
        """
        <div class="section-header">
            <div>
                <div class="section-title">Agent audit trail</div>
                <div class="section-subtitle">
                    Review every recorded action and agent decision
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        logs = get_audit_logs(selected_case_id)
    except requests.exceptions.RequestException as exc:
        st.error(f"Could not load audit logs: {exc}")
        st.stop()

    if not logs:
        st.info("No audit entries were found for this case.")

    for index, log in enumerate(logs, start=1):
        audit_html = dedent(
            f"""
            <div class="audit-card">
                <div class="audit-icon">{index}</div>
                <div>
                    <div class="audit-agent">
                        {safe(log.get("agent_name"))}
                    </div>
                    <div class="audit-message">
                        {safe(log.get("message"))}
                    </div>
                </div>
            </div>
            """
        ).strip()

        st.markdown(audit_html, unsafe_allow_html=True)


# =========================================================
# SYSTEM PAGE
# =========================================================

elif page == "System":
    st.markdown(
        """
        <div class="section-header">
            <div>
                <div class="section-title">System overview</div>
                <div class="section-subtitle">
                    Architecture, services, and operational status
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    status_col1, status_col2, status_col3, status_col4 = st.columns(4)

    with status_col1:
        render_metric(
            label="FastAPI backend",
            value=1,
            icon="API",
            note="Connected",
            accent="#16A66A",
            accent_soft="#E8F8F0",
        )

    with status_col2:
        render_metric(
            label="LangGraph agents",
            value=6,
            icon="AI",
            note="Active agents",
            accent="#5368E8",
            accent_soft="#EEF0FF",
        )

    with status_col3:
        render_metric(
            label="Database",
            value=1,
            icon="DB",
            note="PostgreSQL",
            accent="#2698D4",
            accent_soft="#E8F5FC",
        )

    with status_col4:
        render_metric(
            label="Automation",
            value=1,
            icon="↻",
            note="n8n workflow",
            accent="#8B5CF6",
            accent_soft="#F2EDFF",
        )

    st.write("")

    architecture_left, architecture_right = st.columns([1.15, 0.85])

    with architecture_left:
        st.markdown(
            """
            <div class="surface-card">
                <div class="detail-title">
                    Processing workflow
                </div>
                <div class="recommendation-box">
                    1. Internship application arrives by email.<br>
                    2. n8n IMAP Trigger downloads the PDF attachment.<br>
                    3. FastAPI receives and stores the document.<br>
                    4. LangGraph coordinates six specialized agents.<br>
                    5. PostgreSQL stores the case and audit history.<br>
                    6. n8n sends the appropriate notification email.<br>
                    7. A coordinator records the final human decision.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with architecture_right:
        st.markdown(
            f"""
            <div class="surface-card">
                <div class="detail-title">Core services</div>

                <div class="detail-label">Backend</div>
                <div class="detail-value">
                    FastAPI · {API_BASE_URL}
                </div>

                <div class="detail-label">Orchestration</div>
                <div class="detail-value">
                    LangGraph · 6 agents
                </div>

                <div class="detail-label">Automation</div>
                <div class="detail-value">
                    n8n · IMAP and Gmail
                </div>

                <div class="detail-label">Persistence</div>
                <div class="detail-value">
                    PostgreSQL
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="section-header">
            <div>
                <div class="section-title">API endpoints</div>
                <div class="section-subtitle">
                    Main backend interfaces used by the dashboard
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.code(
        """
GET  /cases
GET  /cases/{case_id}
GET  /cases/{case_id}/audit-logs

POST /cases/upload
POST /cases/{case_id}/approve
POST /cases/{case_id}/reject
POST /cases/{case_id}/request-clarification
        """.strip(),
        language="text",
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        Agentic Internship Coordinator ·
        Human-in-the-loop application processing
    </div>
    """,
    unsafe_allow_html=True,
)
