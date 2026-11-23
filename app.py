"""Streamlit dashboard for Python Long Method analysis."""

from __future__ import annotations

import html
import json
import os
import textwrap
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.analysis import analyze_code, load_model_bundle, result_rows
from src.dataset_evaluation import evaluate_submitted_dataset
from src.examples import LONG_METHOD, SHORT_METHOD
from src.feature_extraction import FEATURE_LABELS
from src.glossary import TERM_HELP
from src.model_versions import (
    create_next_version,
    load_version_registry,
    load_version_payload,
    reset_versions_to_v1,
)
from src.pylint_oracle import add_automatic_labels
from src.user_evaluation import evaluate_user_cases


BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "long_method_model.joblib"
METRICS_PATH = ARTIFACTS_DIR / "metrics.json"
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed" / "long_method_dataset.csv"
QUALITY_PATH = BASE_DIR / "data" / "processed" / "data_quality.json"
MULTI_FUNCTION_TEST_PATH = BASE_DIR / "examples" / "multi_function_test.py"
AUTO_RETRAIN_ENABLED = os.environ.get("CODESCOPE_DISABLE_RETRAIN") != "1"

st.set_page_config(
    page_title="CodeScope | Long Method Analyzer",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_resource
def cached_model(path: str) -> dict:
    return load_model_bundle(path)


def cached_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #102723;
            --muted: #63736f;
            --teal: #0f766e;
            --mint: #dff3eb;
            --amber: #d97706;
            --red: #b42318;
            --red-bg: #fff1ef;
            --line: #dce6e2;
            --paper: #ffffff;
            --canvas: #f5f8f6;
        }
        html, body, [class*="css"] {
            font-family: "Segoe UI Variable", "Segoe UI", Arial, sans-serif;
            font-size: 18px;
        }
        .stApp {
            background:
                radial-gradient(circle at 92% 1%, rgba(38, 166, 154, .10), transparent 26rem),
                linear-gradient(180deg, #fafcfb 0%, var(--canvas) 34rem);
        }
        .block-container {
            width: 100%;
            max-width: 100%;
            padding-top: 1.4rem;
            padding-right: clamp(1rem, 2.2vw, 3rem);
            padding-bottom: 4rem;
            padding-left: clamp(1rem, 2.2vw, 3rem);
        }
        header[data-testid="stHeader"] {
            visibility: hidden;
            height: 0;
        }
        #MainMenu, footer { visibility: hidden; }
        .hero {
            position: relative;
            overflow: hidden;
            padding: 2.15rem 2.35rem 2rem;
            border-radius: 24px;
            color: #ffffff;
            background:
                radial-gradient(circle at 82% 22%, rgba(94, 234, 212, .22), transparent 23rem),
                linear-gradient(125deg, #0d332f 0%, #0f4c45 54%, #0f766e 100%);
            box-shadow: 0 22px 60px rgba(15, 76, 69, .16);
            margin-bottom: 1.4rem;
        }
        .hero::after {
            content: "";
            position: absolute;
            right: -46px;
            bottom: -72px;
            width: 260px;
            height: 260px;
            border: 1px solid rgba(255,255,255,.15);
            border-radius: 50%;
            box-shadow: 0 0 0 38px rgba(255,255,255,.025), 0 0 0 82px rgba(255,255,255,.018);
        }
        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 9px;
            margin-bottom: .9rem;
            color: #bce9df;
            font-size: .76rem;
            font-weight: 700;
            letter-spacing: .13em;
            text-transform: uppercase;
        }
        .eyebrow-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #7ee2ca;
            box-shadow: 0 0 0 5px rgba(126,226,202,.13);
        }
        .hero h1 {
            margin: 0;
            max-width: 760px;
            color: #ffffff;
            font-size: clamp(2rem, 4vw, 3.35rem);
            line-height: 1.03;
            letter-spacing: -.045em;
        }
        .hero p {
            max-width: 720px;
            margin: 1rem 0 1.35rem;
            color: #d5ebe6;
            font-size: 1rem;
            line-height: 1.65;
        }
        .hero-badges {
            display: flex;
            flex-wrap: wrap;
            gap: .55rem;
        }
        .hero-badge {
            padding: .45rem .72rem;
            border: 1px solid rgba(255,255,255,.16);
            border-radius: 999px;
            background: rgba(255,255,255,.07);
            color: #e7f7f3;
            font-size: .78rem;
            font-weight: 600;
        }
        .section-heading {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 1rem;
            margin: 1.7rem 0 .85rem;
        }
        .section-heading h2 {
            margin: 0;
            color: var(--ink);
            font-size: 1.35rem;
            letter-spacing: -.025em;
        }
        .section-heading p {
            margin: 0;
            color: var(--muted);
            font-size: .84rem;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: .8rem;
            margin: .7rem 0 1rem;
        }
        .metric-card {
            min-height: 110px;
            padding: 1.05rem 1.1rem;
            border: 1px solid var(--line);
            border-radius: 17px;
            background: rgba(255,255,255,.88);
            box-shadow: 0 8px 26px rgba(16,39,35,.045);
        }
        .metric-card.accent {
            color: #ffffff;
            border-color: transparent;
            background: linear-gradient(145deg, #0e5f56, #0f766e);
        }
        .metric-card.danger {
            border-color: #f2c4bd;
            background: var(--red-bg);
        }
        .metric-label {
            display: flex;
            align-items: center;
            gap: .42rem;
            color: var(--muted);
            font-size: .76rem;
            font-weight: 700;
            letter-spacing: .055em;
            text-transform: uppercase;
        }
        .accent .metric-label { color: #c6ebe2; }
        .danger .metric-label { color: #9d372c; }
        .info-tip {
            position: relative;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex: 0 0 auto;
            width: 16px;
            height: 16px;
            border: 1px solid currentColor;
            border-radius: 50%;
            color: #61736e;
            background: rgba(255,255,255,.68);
            font-family: Georgia, serif;
            font-size: 10px;
            font-style: normal;
            font-weight: 700;
            line-height: 1;
            letter-spacing: 0;
            text-transform: none;
            cursor: help;
            outline: none;
        }
        .info-tip:hover,
        .info-tip:focus-visible {
            color: var(--teal);
            border-color: var(--teal);
            background: #ffffff;
        }
        .info-tip .tip-content {
            position: absolute;
            top: calc(100% + 8px);
            left: 50%;
            z-index: 9999;
            width: min(290px, 76vw);
            padding: .72rem .78rem;
            border: 1px solid #ceddd8;
            border-radius: 10px;
            color: #203a35;
            background: #ffffff;
            box-shadow: 0 14px 34px rgba(16,39,35,.17);
            font-family: "Segoe UI Variable", "Segoe UI", Arial, sans-serif;
            font-size: .76rem;
            font-style: normal;
            font-weight: 500;
            line-height: 1.48;
            letter-spacing: 0;
            text-align: left;
            text-transform: none;
            white-space: normal;
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
            transform: translate(-50%, -3px);
            transition: opacity .14s ease, transform .14s ease, visibility .14s ease;
        }
        .info-tip .tip-content::before {
            content: "";
            position: absolute;
            top: -6px;
            left: calc(50% - 5px);
            width: 10px;
            height: 10px;
            border-top: 1px solid #ceddd8;
            border-left: 1px solid #ceddd8;
            background: #ffffff;
            transform: rotate(45deg);
        }
        .info-tip:hover .tip-content,
        .info-tip:focus .tip-content,
        .info-tip:focus-visible .tip-content {
            opacity: 1;
            visibility: visible;
            transform: translate(-50%, 0);
        }
        .info-tip.tip-left .tip-content {
            left: auto;
            right: 0;
            transform: translateY(-3px);
        }
        .info-tip.tip-left:hover .tip-content,
        .info-tip.tip-left:focus .tip-content,
        .info-tip.tip-left:focus-visible .tip-content {
            transform: translateY(0);
        }
        .info-tip.tip-left .tip-content::before {
            left: auto;
            right: 3px;
        }
        .info-tip.tip-start .tip-content {
            left: 0;
            transform: translateY(-3px);
        }
        .info-tip.tip-start:hover .tip-content,
        .info-tip.tip-start:focus .tip-content,
        .info-tip.tip-start:focus-visible .tip-content {
            transform: translateY(0);
        }
        .info-tip.tip-start .tip-content::before {
            left: 3px;
        }
        .accent .info-tip,
        .hero .info-tip {
            color: currentColor;
            background: rgba(255,255,255,.10);
        }
        .accent .info-tip:hover,
        .accent .info-tip:focus-visible,
        .hero .info-tip:hover,
        .hero .info-tip:focus-visible {
            color: #ffffff;
            background: rgba(255,255,255,.18);
        }
        .hero .info-tip .tip-content {
            color: #203a35;
            background: #ffffff;
        }
        .hero-badge .info-tip {
            margin-left: .36rem;
            vertical-align: -3px;
        }
        .inline-help-heading {
            display: flex;
            align-items: center;
            gap: .4rem;
            margin: .55rem 0 .65rem;
            color: var(--ink);
            font-weight: 700;
            font-size: .92rem;
        }
        .help-hint {
            display: flex;
            align-items: center;
            gap: .5rem;
            margin: -.45rem 0 1.25rem;
            color: #5f716c;
            font-size: .8rem;
        }
        .side-results {
            margin-top: .8rem;
            padding: 1rem;
            border: 1px solid var(--line);
            border-radius: 17px;
            background: rgba(255,255,255,.9);
            box-shadow: 0 8px 26px rgba(16,39,35,.045);
        }
        .side-results + .side-results {
            margin-top: .7rem;
        }
        .side-results-title {
            display: flex;
            align-items: center;
            gap: .4rem;
            margin-bottom: .7rem;
            color: var(--ink);
            font-size: .84rem;
            font-weight: 750;
        }
        .ide-status {
            display: inline-flex;
            align-items: center;
            padding: .32rem .55rem;
            border-radius: 999px;
            font-size: .7rem;
            font-weight: 750;
        }
        .ide-status.flagged {
            color: var(--red);
            background: #fee4e2;
        }
        .ide-status.clear {
            color: var(--teal);
            background: var(--mint);
        }
        .ide-summary {
            margin-top: .55rem;
            color: var(--muted);
            font-size: .78rem;
            line-height: 1.45;
        }
        .ide-function-list {
            margin-top: .65rem;
            border-top: 1px solid #e8efec;
        }
        .ide-function-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .7rem;
            padding: .42rem 0;
            border-bottom: 1px solid #edf2f0;
            color: #334844;
            font-size: .74rem;
        }
        .ide-function-row code {
            overflow: hidden;
            color: #1f3934;
            font-family: "Cascadia Code", "Consolas", monospace;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .ide-function-probability {
            flex: 0 0 auto;
            font-weight: 750;
        }
        .eval-triplet {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .5rem;
        }
        .eval-set + .eval-set {
            margin-top: .8rem;
            padding-top: .8rem;
            border-top: 1px solid #e7eeeb;
        }
        .eval-set-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: .45rem;
            color: #38534d;
            font-size: .7rem;
            font-weight: 750;
        }
        .eval-set-title small {
            color: var(--muted);
            font-size: .64rem;
            font-weight: 600;
        }
        .eval-cell {
            padding: .7rem .6rem;
            border: 1px solid #e0ebe7;
            border-radius: 11px;
            background: #f6faf8;
        }
        .eval-cell span {
            display: flex;
            align-items: center;
            gap: .25rem;
            color: var(--muted);
            font-size: .64rem;
            font-weight: 750;
            letter-spacing: .035em;
            text-transform: uppercase;
            white-space: nowrap;
        }
        .eval-cell strong {
            display: block;
            margin-top: .3rem;
            color: var(--ink);
            font-size: 1.08rem;
        }
        .eval-value-line {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: .35rem;
        }
        .metric-delta {
            flex: 0 0 auto;
            color: #6c7d78;
            font-size: .62rem;
            font-weight: 750;
            letter-spacing: -.01em;
            white-space: nowrap;
        }
        .metric-delta.positive { color: #087a6d; }
        .metric-delta.negative { color: #b42318; }
        .side-note {
            margin-top: .65rem;
            color: #65766f;
            font-size: .7rem;
            line-height: 1.4;
        }
        .version-compare-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: .9rem;
            margin: .65rem 0 1rem;
        }
        .version-card {
            position: relative;
            overflow: hidden;
            padding: 1.05rem;
            border: 1px solid var(--line);
            border-radius: 18px;
            background: rgba(255,255,255,.93);
            box-shadow: 0 9px 28px rgba(16,39,35,.05);
        }
        .version-card.candidate {
            border-color: #9fd4c8;
            background:
                linear-gradient(145deg, rgba(223,243,235,.7), rgba(255,255,255,.96) 54%);
        }
        .version-card.placeholder {
            border-style: dashed;
            background: rgba(255,255,255,.58);
            box-shadow: none;
        }
        .version-card-head {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: .75rem;
            margin-bottom: .85rem;
        }
        .version-tag {
            display: block;
            margin-bottom: .25rem;
            color: var(--teal);
            font-size: .65rem;
            font-weight: 800;
            letter-spacing: .11em;
            text-transform: uppercase;
        }
        .version-card h3 {
            margin: 0;
            color: var(--ink);
            font-size: 1.16rem;
            letter-spacing: -.025em;
        }
        .version-card h3 small {
            color: var(--muted);
            font-size: .72rem;
            font-weight: 600;
        }
        .version-badge {
            flex: 0 0 auto;
            padding: .28rem .48rem;
            border-radius: 999px;
            color: #4d625c;
            background: #edf3f1;
            font-size: .62rem;
            font-weight: 800;
            letter-spacing: .05em;
        }
        .version-badge.new {
            color: #0c655b;
            background: #dff3eb;
        }
        .version-counts {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .4rem;
            margin-bottom: .8rem;
        }
        .version-count {
            padding: .55rem .5rem;
            border-radius: 10px;
            background: #f5f9f7;
        }
        .version-count span {
            display: block;
            color: var(--muted);
            font-size: .58rem;
            font-weight: 750;
            letter-spacing: .035em;
            text-transform: uppercase;
        }
        .version-count strong {
            display: block;
            margin-top: .2rem;
            color: var(--ink);
            font-size: .9rem;
        }
        .version-metric-block {
            padding-top: .72rem;
            border-top: 1px solid #e7eeeb;
        }
        .version-metric-block + .version-metric-block {
            margin-top: .72rem;
        }
        .version-metric-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .5rem;
            margin-bottom: .42rem;
            color: #37524c;
            font-size: .7rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .035em;
        }
        .version-metric-title small {
            color: var(--muted);
            font-size: .6rem;
            font-weight: 650;
            letter-spacing: 0;
            text-transform: none;
        }
        .version-threshold {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .7rem;
            margin-top: .8rem;
            padding: .62rem .7rem;
            border-radius: 11px;
            color: #d6f1eb;
            background: #0f5f56;
            font-size: .72rem;
        }
        .version-threshold strong {
            color: #ffffff;
            font-size: 1rem;
        }
        .version-threshold-value {
            display: flex;
            align-items: baseline;
            gap: .4rem;
            white-space: nowrap;
        }
        .version-threshold .metric-delta {
            color: #d6f1eb;
        }
        .version-threshold .metric-delta.positive {
            color: #b8f3df;
        }
        .version-threshold .metric-delta.negative {
            color: #ffd0cb;
        }
        .version-placeholder-copy {
            display: flex;
            align-items: flex-start;
            gap: .8rem;
            margin-top: 1.1rem;
            color: var(--muted);
            font-size: .8rem;
            line-height: 1.55;
        }
        .version-empty-mark {
            display: grid;
            flex: 0 0 auto;
            width: 52px;
            height: 52px;
            place-items: center;
            border: 1px solid #b9ddd4;
            border-radius: 15px;
            color: #0f766e;
            background:
                radial-gradient(circle at 28% 22%, #ffffff, transparent 45%),
                #dff3eb;
            font-size: .86rem;
            font-weight: 850;
            letter-spacing: -.02em;
        }
        .version-placeholder-copy strong {
            display: block;
            margin-bottom: .16rem;
            color: var(--ink);
            font-size: .84rem;
        }
        .version-history-note {
            margin-top: -.2rem;
            color: #60736d;
            font-size: .7rem;
            line-height: 1.45;
        }
        .metric-value {
            margin-top: .48rem;
            color: var(--ink);
            font-size: 1.85rem;
            font-weight: 750;
            letter-spacing: -.04em;
            line-height: 1;
        }
        .accent .metric-value { color: #ffffff; }
        .danger .metric-value { color: var(--red); }
        .metric-note {
            margin-top: .55rem;
            color: var(--muted);
            font-size: .76rem;
            line-height: 1.35;
        }
        .accent .metric-note { color: #d6f1eb; }
        .result-banner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 1rem 1.15rem;
            border-radius: 16px;
            margin: .3rem 0 1rem;
            border: 1px solid var(--line);
            background: #ffffff;
        }
        .result-banner.flagged {
            border-color: #f0beb7;
            background: #fff7f5;
        }
        .result-banner.clear {
            border-color: #bde3d8;
            background: #f4fbf8;
        }
        .result-title {
            color: var(--ink);
            font-weight: 750;
            font-size: 1rem;
        }
        .result-copy {
            color: var(--muted);
            font-size: .82rem;
            margin-top: .2rem;
        }
        .pill {
            flex: 0 0 auto;
            padding: .5rem .72rem;
            border-radius: 999px;
            font-size: .76rem;
            font-weight: 750;
        }
        .pill.flagged { color: var(--red); background: #fee4e2; }
        .pill.clear { color: var(--teal); background: var(--mint); }
        .empty-state {
            padding: 2.2rem 1.5rem;
            text-align: center;
            border: 1px dashed #bdd1cb;
            border-radius: 18px;
            background: rgba(255,255,255,.62);
        }
        .empty-state strong {
            display: block;
            color: var(--ink);
            font-size: 1rem;
            margin-bottom: .38rem;
        }
        .empty-state span { color: var(--muted); font-size: .86rem; }
        .note {
            padding: .8rem .95rem;
            border-left: 3px solid #5bb7a7;
            border-radius: 0 10px 10px 0;
            background: #eff8f5;
            color: #34554f;
            font-size: .84rem;
            line-height: 1.5;
        }
        .mini-feature-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: .6rem;
            margin: .55rem 0 .8rem;
        }
        .mini-feature {
            padding: .75rem .8rem;
            border-radius: 12px;
            background: #f5f9f7;
            border: 1px solid #e0ebe7;
        }
        .mini-feature span {
            display: flex;
            align-items: center;
            gap: .34rem;
            color: var(--muted);
            font-size: .7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .045em;
        }
        .mini-feature strong {
            display: block;
            margin-top: .25rem;
            color: var(--ink);
            font-size: 1.15rem;
        }
        div[data-testid="stTextArea"] textarea {
            font-family: "Cascadia Code", "Consolas", monospace;
            font-size: .95rem;
            line-height: 1.55;
            border-radius: 14px;
            background: #fbfdfc;
        }
        div.stButton > button, div.stDownloadButton > button {
            border-radius: 10px;
            font-weight: 700;
            min-height: 2.65rem;
        }
        div.stButton > button[kind="primary"] {
            border: 0;
            background: #0f766e;
            box-shadow: 0 7px 18px rgba(15,118,110,.18);
        }
        div[data-testid="stExpander"] {
            border-color: var(--line);
            border-radius: 14px;
            background: rgba(255,255,255,.82);
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 14px;
            overflow: hidden;
        }
        @media (max-width: 900px) {
            .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .hero { padding: 1.6rem 1.4rem; }
            .section-heading { align-items: start; flex-direction: column; gap: .2rem; }
        }
        @media (max-width: 560px) {
            .metric-grid { grid-template-columns: 1fr; }
            .version-compare-grid { grid-template-columns: 1fr; }
            .mini-feature-grid { grid-template-columns: 1fr; }
            .result-banner { align-items: flex-start; flex-direction: column; }
            .info-tip .tip-content { width: min(260px, 84vw); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def info_icon(help_key: str, tip_side: str = "right") -> str:
    explanation = html.escape(TERM_HELP[help_key], quote=True)
    return (
        f'<span class="info-tip tip-{tip_side}" tabindex="0" role="button" '
        f'aria-label="{explanation}" title="{explanation}">i'
        f'<span class="tip-content">{explanation}</span></span>'
    )


def inline_help_heading(label: str, help_key: str) -> str:
    return (
        f'<div class="inline-help-heading"><span>{html.escape(label)}</span>'
        f"{info_icon(help_key)}</div>"
    )


def metric_card(
    label: str,
    value: str,
    note: str,
    style: str = "",
    help_key: str | None = None,
    tip_side: str = "right",
) -> str:
    tooltip = info_icon(help_key, tip_side) if help_key else ""
    return (
        f'<div class="metric-card {style}">'
        f'<div class="metric-label"><span>{html.escape(label)}</span>{tooltip}</div>'
        f'<div class="metric-value">{html.escape(value)}</div>'
        f'<div class="metric-note">{html.escape(note)}</div>'
        "</div>"
    )


def render_metric_grid(cards: list[str]) -> None:
    st.markdown(
        f'<div class="metric-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def _metric_delta(
    current: float,
    baseline: float | None,
    *,
    digits: int = 3,
) -> str:
    if baseline is None:
        return ""
    delta_points = (float(current) - float(baseline)) * 100
    if abs(delta_points) < 0.0005:
        css_class = "metric-delta"
        value = "0,00"
    else:
        css_class = (
            "metric-delta positive"
            if delta_points > 0
            else "metric-delta negative"
        )
        value = f"{delta_points:+.{digits}f}".replace(".", ",")
    signed_value = value if value.startswith(("+", "-")) else value
    return f'<span class="{css_class}">{signed_value} pp</span>'


def _version_metric_triplet(
    metrics: dict,
    baseline_metrics: dict | None = None,
) -> str:
    baseline = baseline_metrics or {}

    def value_line(metric_key: str) -> str:
        return (
            '<div class="eval-value-line">'
            f"<strong>{metrics[metric_key]:.1%}</strong>"
            f"{_metric_delta(metrics[metric_key], baseline.get(metric_key))}"
            "</div>"
        )

    return (
        '<div class="eval-triplet">'
        '<div class="eval-cell">'
        f'<span>Precision {info_icon("precision", "start")}</span>'
        f"{value_line('precision')}</div>"
        '<div class="eval-cell">'
        f'<span>Recall {info_icon("recall", "start")}</span>'
        f"{value_line('recall')}</div>"
        '<div class="eval-cell">'
        f'<span>F1-score {info_icon("f1_score", "start")}</span>'
        f"{value_line('f1_score')}</div>"
        "</div>"
    )


def _version_card(
    version: dict,
    payload: dict,
    *,
    candidate: bool,
    baseline_payload: dict | None = None,
) -> str:
    metrics = payload["metrics"]
    dataset = payload["dataset"]
    training = metrics.get("training_metrics", metrics)
    testing = metrics.get("testing_metrics", metrics)
    baseline_metrics = baseline_payload["metrics"] if baseline_payload else None
    baseline_training = (
        baseline_metrics.get("training_metrics", baseline_metrics)
        if baseline_metrics
        else None
    )
    baseline_testing = (
        baseline_metrics.get("testing_metrics", baseline_metrics)
        if baseline_metrics
        else None
    )
    train_rows = f"{version['training_rows']:,}".replace(",", ".")
    benchmark_rows = f"{version['benchmark_rows']:,}".replace(",", ".")
    added_rows = int(version.get("added_rows", 0))
    added_label = f"+{added_rows}" if added_rows else "0"
    css_class = "version-card candidate" if candidate else "version-card"
    badge = "VERSI BARU" if candidate else "BEKU"
    badge_class = "version-badge new" if candidate else "version-badge"
    description = (
        "Dataset awal ditambah input IDE"
        if candidate
        else "Model awal sebagai pembanding"
    )
    threshold = float(version["threshold"])
    threshold_delta = _metric_delta(
        threshold,
        (
            float(baseline_payload["metrics"]["threshold"])
            if baseline_payload
            else None
        ),
        digits=2,
    )
    return textwrap.dedent(
        f"""
        <article class="{css_class}">
            <div class="version-card-head">
                <div>
                    <span class="version-tag">Model {version['label']}</span>
                    <h3>{html.escape(version['label'])}
                        <small>{html.escape(description)}</small>
                    </h3>
                </div>
                <span class="{badge_class}">{badge}</span>
            </div>
            <div class="version-counts">
                <div class="version-count">
                    <span>Data latih</span>
                    <strong>{train_rows}</strong>
                </div>
                <div class="version-count">
                    <span>Input baru</span>
                    <strong>{added_label}</strong>
                </div>
                <div class="version-count">
                    <span>Benchmark</span>
                    <strong>{benchmark_rows}</strong>
                </div>
            </div>
            <div class="version-metric-block">
                <div class="version-metric-title">
                    <span>Kinerja data latih</span>
                    <small>{dataset['train_rows']:,} record</small>
                </div>
                {_version_metric_triplet(training, baseline_training)}
            </div>
            <div class="version-metric-block">
                <div class="version-metric-title">
                    <span>Kinerja benchmark tetap</span>
                    <small>{dataset['test_rows']:,} record</small>
                </div>
                {_version_metric_triplet(testing, baseline_testing)}
            </div>
            <div class="version-threshold"><span>Threshold klasifikasi {info_icon("threshold", "start")}</span><span class="version-threshold-value"><strong>{threshold * 100:.2f}%</strong>{threshold_delta}</span></div>
        </article>
        """
    ).strip()


def render_version_comparison(
    artifacts_dir: Path,
    versions: list[dict],
) -> None:
    baseline = versions[0]
    latest = versions[-1]
    baseline_model, baseline_payload = load_version_payload(
        artifacts_dir,
        int(baseline["version"]),
    )
    baseline_payload = dict(baseline_payload)
    baseline_payload["model_path"] = str(baseline_model)
    baseline_card = _version_card(
        baseline,
        baseline_payload,
        candidate=False,
    )
    if int(latest["version"]) == int(baseline["version"]):
        candidate_card = textwrap.dedent(
            """
            <article class="version-card placeholder">
                <div class="version-card-head">
                    <div>
                        <span class="version-tag">Model berikutnya</span>
                        <h3>V2 <small>Belum dibuat</small></h3>
                    </div>
                    <span class="version-badge">MENUNGGU INPUT</span>
                </div>
                <div class="version-placeholder-copy">
                    <span class="version-empty-mark">V2</span>
                    <span>
                        <strong>Siap menerima kode baru</strong>
                        Submit kode Python melalui editor. Sistem akan membuat
                        snapshot latih V2 tanpa mengubah V1, lalu menguji keduanya
                        pada data benchmark yang sama.
                    </span>
                </div>
            </article>
            """
        ).strip()
        candidate_version = "V2"
    else:
        candidate_model, candidate_payload = load_version_payload(
            artifacts_dir,
            int(latest["version"]),
        )
        candidate_payload = dict(candidate_payload)
        candidate_payload["model_path"] = str(candidate_model)
        candidate_card = _version_card(
            latest,
            candidate_payload,
            candidate=True,
            baseline_payload=baseline_payload,
        )
        candidate_version = latest["label"]

    comparison_html = textwrap.dedent(
        f"""
        <div class="section-heading">
            <div>
                <h2>Perbandingan versi model {info_icon("model_version", "start")}</h2>
                <p>V1 dan {candidate_version} diuji pada benchmark yang sama.</p>
            </div>
        </div>
        <div class="version-compare-grid">{baseline_card}{candidate_card}</div>
        <div class="version-history-note">
            V1 disimpan sebagai artefak beku. Setiap submit membuat versi baru
            dari snapshot latih sebelumnya; threshold dan metrik versi lama tidak
            ditimpa. Data benchmark tidak dipakai untuk melatih atau mengkalibrasi
            model.
        </div>
        """
    ).strip()
    st.markdown(
        comparison_html,
        unsafe_allow_html=True,
    )


def render_version_management(versions: list[dict]) -> None:
    additional_versions = [
        version
        for version in versions
        if int(version["version"]) > 1
    ]
    with st.expander("Kembali ke model V1", expanded=False):
        if not additional_versions:
            st.success(
                "Saat ini hanya V1 yang tersimpan. Belum ada V2 atau versi "
                "berikutnya untuk dihapus."
            )
            return

        labels = ", ".join(
            version["label"] for version in additional_versions
        )
        st.warning(
            f"Tindakan ini menghapus permanen {labels} beserta model, metrik, "
            "dan snapshot latihnya. V1 tetap dipertahankan. Setelah refresh, "
            "dashboard hanya akan menampilkan V1."
        )
        confirmed = st.checkbox(
            f"Saya memahami bahwa {labels} akan dihapus permanen.",
            key="confirm_reset_to_v1",
        )
        if st.button(
            "Hapus versi tambahan dan kembali ke V1",
            key="reset_versions_to_v1",
            type="primary",
            width="stretch",
            disabled=not confirmed,
        ):
            try:
                reset_result = reset_versions_to_v1(
                    ARTIFACTS_DIR,
                    PROCESSED_DATA_PATH,
                )
                removed = ", ".join(
                    f"V{version}"
                    for version in reset_result["removed_versions"]
                )
                for key in (
                    "latest_result",
                    "submitted_dataset_eval",
                    "retrain_notice",
                    "confirm_reset_to_v1",
                ):
                    st.session_state.pop(key, None)
                st.session_state.code_input = SHORT_METHOD
                st.session_state.flash_message = (
                    f"Reset selesai. {removed} dihapus dan model aktif "
                    "kembali ke V1."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Reset ke V1 gagal: {exc}")


def render_testing_panel(
    latest: dict | None,
    bundle: dict,
    metrics_payload: dict,
) -> None:
    evaluation_payload = metrics_payload
    analysis_version = latest.get("analysis_version") if latest else None
    if analysis_version is not None:
        _, evaluation_payload = load_version_payload(
            ARTIFACTS_DIR,
            int(analysis_version),
        )
    metrics = evaluation_payload["metrics"]
    test_dataset = evaluation_payload["dataset"]
    training_metrics = metrics.get("training_metrics", metrics)
    testing_metrics = metrics.get("testing_metrics", metrics)
    submitted_eval = st.session_state.get("submitted_dataset_eval")
    ide_test_metrics = (
        latest.get("ide_test_metrics") if latest else None
    )
    train_rows_label = f"{test_dataset['train_rows']:,}".replace(",", ".")
    training_label = "Data latih"
    if analysis_version is not None:
        training_label += f" V{analysis_version}"
    if ide_test_metrics and ide_test_metrics.get("available"):
        comparison_metrics = ide_test_metrics
        model_label = (
            f" · prediksi V{analysis_version}"
            if analysis_version is not None
            else ""
        )
        comparison_title = f"Data uji IDE{model_label}"
        comparison_rows_label = f"{comparison_metrics['sample_count']:,}".replace(
            ",", "."
        )
        comparison_note = (
            "Data uji IDE dihitung dari seluruh fungsi pada submit terakhir. "
            "Label aktual berasal dari Pylint R0915 dan dibandingkan dengan "
            "prediksi Decision Tree"
            + (
                f" versi V{analysis_version}."
                if analysis_version is not None
                else "."
            )
        )
        comparison_html = (
            '<div class="eval-set">'
            f'<div class="eval-set-title">{comparison_title} '
            f"<small>{comparison_rows_label} record</small></div>"
            '<div class="eval-triplet">'
            '<div class="eval-cell">'
            f"<span>Precision {info_icon('precision', 'start')}</span>"
            f"<strong>{comparison_metrics['precision']:.1%}</strong></div>"
            '<div class="eval-cell">'
            f"<span>Recall {info_icon('recall', 'start')}</span>"
            f"<strong>{comparison_metrics['recall']:.1%}</strong></div>"
            '<div class="eval-cell">'
            f"<span>F1-score {info_icon('f1_score', 'start')}</span>"
            f"<strong>{comparison_metrics['f1_score']:.1%}</strong></div>"
            "</div></div>"
        )
        if not comparison_metrics.get("sufficient", False):
            comparison_html += (
                '<div class="side-note" style="margin-top:.7rem">'
                f"{html.escape(comparison_metrics['reason'])}</div>"
            )
    elif submitted_eval:
        comparison_metrics = submitted_eval["metrics"]
        comparison_title = (
            "Data uji internal"
            if submitted_eval.get("source") == "internal"
            else "Data uji input"
        )
        comparison_rows_label = f"{comparison_metrics['sample_count']:,}".replace(
            ",", "."
        )
        comparison_html = (
            '<div class="eval-set">'
            f'<div class="eval-set-title">{comparison_title} '
            f"<small>{comparison_rows_label} record</small></div>"
            '<div class="eval-triplet">'
            '<div class="eval-cell">'
            f"<span>Precision {info_icon('precision', 'start')}</span>"
            f"<strong>{comparison_metrics['precision']:.1%}</strong></div>"
            '<div class="eval-cell">'
            f"<span>Recall {info_icon('recall', 'start')}</span>"
            f"<strong>{comparison_metrics['recall']:.1%}</strong></div>"
            '<div class="eval-cell">'
            f"<span>F1-score {info_icon('f1_score', 'start')}</span>"
            f"<strong>{comparison_metrics['f1_score']:.1%}</strong></div>"
            "</div></div>"
        )
        comparison_note = (
            "Data uji internal berasal dari 24 repository holdout yang tidak "
            "dipakai saat pelatihan dan dibandingkan langsung dengan data latih."
            if submitted_eval.get("source") == "internal"
            else (
                "Data uji input dihitung dari file baru yang diunggah dan "
                "dibandingkan langsung dengan data latih."
            )
        )
    elif ide_test_metrics:
        comparison_html = (
            '<div class="side-note">'
            f"{html.escape(ide_test_metrics['reason'])}</div>"
        )
        comparison_note = (
            "Prediksi setiap fungsi tetap bisa dilihat pada panel hasil input IDE."
        )
    else:
        comparison_html = (
            '<div class="side-note">Belum ada metrik data uji IDE yang valid. '
            "Submit kode yang memuat fungsi Long Method dan bukan Long Method, "
            "atau buka <strong>Uji dataset baru dari file</strong>.</div>"
        )
        comparison_note = (
            "Data latih bersifat tetap. Angka uji benchmark tetap tersedia "
            "pada bagian evaluasi model dan kualitas dataset."
        )

    if latest:
        summary = latest["summary"]
        functions = latest["functions"]
        flagged = summary["flagged_count"]
        status_class = "flagged" if flagged else "clear"
        status_label = "PERLU DITINJAU" if flagged else "TIDAK TERINDIKASI"
        function_rows = "".join(
            (
                '<div class="ide-function-row">'
                f"<code>{html.escape(item['name'])}</code>"
                f'<span class="ide-function-probability">'
                f"{item['probability'] * 100:.1f}%</span>"
                "</div>"
            )
            for item in functions[:6]
        )
        if len(functions) > 6:
            function_rows += (
                '<div class="ide-function-row">'
                f"<span>{len(functions) - 6} fungsi lainnya</span>"
                "<span></span></div>"
            )
        st.markdown(
            f"""
            <div class="side-results">
                <div class="side-results-title">
                    Hasil prediksi input IDE {info_icon("ide_result", "start")}
                </div>
                <span class="ide-status {status_class}">{status_label}</span>
                <div class="ide-summary">
                    <strong>{summary['function_count']}</strong> fungsi dianalisis,
                    <strong>{flagged}</strong> terindikasi, dan
                    <strong>{summary['clear_count']}</strong> tidak terindikasi.
                    Probabilitas tertinggi
                    <strong>{summary['max_probability'] * 100:.1f}%</strong>.
                </div>
                <div class="ide-function-list">{function_rows}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="side-results">
                <div class="side-results-title">
                    Hasil prediksi input IDE {info_icon("ide_result", "start")}
                </div>
                <div class="side-note">
                    Belum ada kode yang dianalisis. Jalankan analisis untuk
                    melihat label dan probabilitas pada panel ini.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if latest:
        unavailable = [
            item for item in functions if item.get("actual_label") is None
        ]
        if unavailable:
            st.warning(
                "Label pembanding R0915 tidak tersedia untuk sebagian fungsi. "
                "Model tetap dapat menampilkan prediksi."
            )
        else:
            st.caption(
                "Label pembanding R0915 ditambahkan otomatis. Tidak perlu memilih "
                "label secara manual."
            )

    st.markdown(
        f"""
        <div class="side-results">
            <div class="side-results-title">
                Perbandingan data latih dan data uji
                {info_icon("test_metrics", "start")}
            </div>
            <div class="eval-set">
                <div class="eval-set-title">
                    {training_label} <small>{train_rows_label} record</small>
                </div>
                <div class="eval-triplet">
                    <div class="eval-cell">
                        <span>Precision {info_icon("precision", "start")}</span>
                        <strong>{training_metrics['precision']:.1%}</strong>
                    </div>
                    <div class="eval-cell">
                        <span>Recall {info_icon("recall", "start")}</span>
                        <strong>{training_metrics['recall']:.1%}</strong>
                    </div>
                    <div class="eval-cell">
                        <span>F1-score {info_icon("f1_score", "start")}</span>
                        <strong>{training_metrics['f1_score']:.1%}</strong>
                    </div>
                </div>
            </div>{comparison_html}
            <div class="side-note">
                {comparison_note}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def probability_chart(result: dict) -> go.Figure:
    functions = result["functions"]
    names = [item["name"] for item in functions]
    probabilities = [item["probability"] * 100 for item in functions]
    colors = ["#d64b3f" if item["is_flagged"] else "#0f8a7d" for item in functions]
    figure = go.Figure(
        go.Bar(
            x=probabilities,
            y=names,
            orientation="h",
            marker={"color": colors, "line": {"width": 0}},
            text=[f"{value:.1f}%" for value in probabilities],
            textposition="outside",
            hovertemplate="%{y}<br>Probabilitas: %{x:.1f}%<extra></extra>",
        )
    )
    figure.update_layout(
        height=max(260, 82 + len(functions) * 33),
        margin={"l": 10, "r": 48, "t": 8, "b": 20},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Segoe UI", "color": "#40524e", "size": 12},
        xaxis={
            "range": [0, 108],
            "ticksuffix": "%",
            "gridcolor": "#e8efec",
            "zeroline": False,
            "title": "",
        },
        yaxis={"autorange": "reversed", "title": ""},
        showlegend=False,
        bargap=0.34,
    )
    return figure


def distribution_chart(flagged: int, clear: int) -> go.Figure:
    figure = go.Figure(
        go.Pie(
            values=[flagged, clear],
            labels=["Terindikasi", "Tidak terindikasi"],
            hole=0.69,
            sort=False,
            marker={"colors": ["#d64b3f", "#d8e8e3"], "line": {"width": 0}},
            textinfo="none",
            hovertemplate="%{label}: %{value}<extra></extra>",
        )
    )
    figure.update_layout(
        height=260,
        margin={"l": 8, "r": 8, "t": 14, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Segoe UI", "color": "#40524e"},
        showlegend=True,
        legend={"orientation": "h", "x": 0.5, "xanchor": "center", "y": -0.08},
        annotations=[
            {
                "text": f"<b>{flagged}</b><br><span style='font-size:11px'>terindikasi</span>",
                "showarrow": False,
                "font": {"size": 24, "color": "#102723"},
            }
        ],
    )
    return figure


def render_result(result: dict) -> None:
    summary = result["summary"]
    flagged = summary["flagged_count"]
    clear = summary["clear_count"]
    status_class = "flagged" if flagged else "clear"
    status_label = "PERLU DITINJAU" if flagged else "TIDAK TERINDIKASI"
    status_copy = (
        f"{flagged} dari {summary['function_count']} fungsi melewati threshold model."
        if flagged
        else "Semua fungsi berada di bawah threshold model Long Method."
    )
    st.markdown(
        f"""
        <div class="result-banner {status_class}">
            <div>
                <div class="result-title">
                    Dashboard hasil analisis {info_icon("prediction", "right")}
                </div>
                <div class="result-copy">{html.escape(status_copy)}</div>
            </div>
            <div class="pill {status_class}">{status_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_metric_grid(
        [
            metric_card(
                "Fungsi dianalisis",
                str(summary["function_count"]),
                "Satu record per fungsi",
                help_key="function_count",
                tip_side="start",
            ),
            metric_card(
                "Terindikasi",
                str(flagged),
                "Long Method terdeteksi",
                "danger" if flagged else "",
                help_key="flagged",
            ),
            metric_card(
                "Tidak terindikasi",
                str(clear),
                "Fungsi di bawah threshold",
                help_key="clear",
            ),
            metric_card(
                "Probabilitas tertinggi",
                f"{summary['max_probability'] * 100:.1f}%",
                f"Threshold model {summary['threshold'] * 100:.2f}%",
                "accent",
                help_key="max_probability",
                tip_side="left",
            ),
        ]
    )

    chart_left, chart_right = st.columns([0.72, 1.28])
    with chart_left:
        st.markdown(
            inline_help_heading("Komposisi prediksi", "composition"),
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            distribution_chart(flagged, clear),
            width="stretch",
            config={"displayModeBar": False},
        )
    with chart_right:
        st.markdown(
            inline_help_heading("Probabilitas per fungsi", "probability"),
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            probability_chart(result),
            width="stretch",
            config={"displayModeBar": False},
        )

    table = pd.DataFrame(result_rows(result))
    st.markdown(
        inline_help_heading("Rincian fungsi", "static_features"),
        unsafe_allow_html=True,
    )
    st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        column_config={
            "Fungsi": st.column_config.TextColumn(
                "Fungsi",
                help=TERM_HELP["function_count"],
            ),
            "Baris": st.column_config.TextColumn(
                "Baris",
                help=TERM_HELP["line_range"],
            ),
            "Prediksi": st.column_config.TextColumn(
                "Prediksi",
                help=TERM_HELP["prediction"],
            ),
            "Probabilitas": st.column_config.ProgressColumn(
                "Probabilitas",
                min_value=0.0,
                max_value=1.0,
                format="%.1%%",
                help=TERM_HELP["probability"],
            ),
            "LOC": st.column_config.NumberColumn(
                "LOC",
                help=TERM_HELP["nloc"],
            ),
            "Parameter": st.column_config.NumberColumn(
                "Parameter",
                help=TERM_HELP["parameter_count"],
            ),
            "Percabangan": st.column_config.NumberColumn(
                "Percabangan",
                help=TERM_HELP["branch_count"],
            ),
            "Aktual R0915": st.column_config.TextColumn(
                "Aktual R0915",
                help=(
                    "Label pembanding otomatis dari Pylint R0915. Label ini "
                    "tidak diambil dari prediksi model."
                ),
            ),
            "Status uji": st.column_config.TextColumn(
                "Status uji",
                help=(
                    "Perbandingan label aktual R0915 dengan prediksi model: "
                    "benar positif, benar negatif, salah positif, atau salah negatif."
                ),
            ),
        },
    )

    for item in result["functions"]:
        badge = "Terindikasi" if item["is_flagged"] else "Tidak terindikasi"
        with st.expander(
            f"{item['name']} | {badge} | probabilitas {item['probability'] * 100:.1f}%"
        ):
            features = item["features"]
            feature_cards = "".join(
                [
                    (
                        '<div class="mini-feature">'
                        f'<span><span>{html.escape(FEATURE_LABELS[feature])}</span>'
                        f"{info_icon(feature, 'start' if feature == 'nloc' else 'right')}</span>"
                        f"<strong>{features[feature]}</strong>"
                        "</div>"
                    )
                    for feature in ("nloc", "parameter_count", "branch_count")
                ]
            )
            st.markdown(
                f'<div class="mini-feature-grid">{feature_cards}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="note"><strong>Label aktual otomatis:</strong> '
                f"{html.escape(item.get('actual_label_name', 'Tidak tersedia'))}"
                f"<br><strong>Status pengujian:</strong> "
                f"{html.escape(item.get('test_outcome', 'Tidak tersedia'))}</div>",
                unsafe_allow_html=True,
            )
            rule_text = (
                "<br>".join(
                    f"{index + 1}. {html.escape(rule)}"
                    for index, rule in enumerate(item["decision_rules"])
                )
                or "Model berhenti pada akar keputusan."
            )
            st.markdown(
                inline_help_heading("Jalur keputusan model", "decision_path"),
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="note">{rule_text}<br><br>'
                f"<strong>Saran {info_icon('recommendation', 'right')}:</strong> "
                f"{html.escape(item['suggestion'])}</div>",
                unsafe_allow_html=True,
            )

    st.download_button(
        "Unduh hasil JSON",
        data=json.dumps(result, indent=2, ensure_ascii=False).encode("utf-8"),
        file_name="codescope_analysis.json",
        mime="application/json",
        help=TERM_HELP["json"],
    )


def render_model_summary(metrics_payload: dict, quality: dict) -> None:
    metrics = metrics_payload["metrics"]
    dataset = metrics_payload["dataset"]
    training_metrics = metrics.get("training_metrics", metrics)
    testing_metrics = metrics.get("testing_metrics", metrics)
    submitted_eval = st.session_state.get("submitted_dataset_eval")
    latest_result = st.session_state.get("latest_result")
    ide_test_metrics = (
        latest_result.get("ide_test_metrics") if latest_result else None
    )
    with st.expander("Evaluasi model dan kualitas dataset", expanded=False):
        st.markdown(
            inline_help_heading(
                "Perbandingan metrik per sumber data",
                "test_metrics",
            ),
            unsafe_allow_html=True,
        )
        comparison_rows = [
            {
                "Data": "Latih",
                "Status": "Data pelatihan",
                "Record": dataset["train_rows"],
                "Repository": dataset["train_repositories"],
                "Precision": f"{training_metrics['precision']:.1%}",
                "Recall": f"{training_metrics['recall']:.1%}",
                "F1-score": f"{training_metrics['f1_score']:.1%}",
                "ROC-AUC": f"{training_metrics['roc_auc']:.1%}",
            },
        ]
        if ide_test_metrics and ide_test_metrics.get("available"):
            comparison_rows.append(
                {
                    "Data": (
                        f"Uji IDE V{latest_result['analysis_version']}"
                        if latest_result.get("analysis_version") is not None
                        else "Uji IDE"
                    ),
                    "Status": "Submit terakhir; model tetap",
                    "Record": ide_test_metrics["sample_count"],
                    "Repository": None,
                    "Precision": f"{ide_test_metrics['precision']:.1%}",
                    "Recall": f"{ide_test_metrics['recall']:.1%}",
                    "F1-score": f"{ide_test_metrics['f1_score']:.1%}",
                    "ROC-AUC": (
                        f"{ide_test_metrics['roc_auc']:.1%}"
                        if ide_test_metrics.get("roc_auc") is not None
                        else "n.a."
                    ),
                }
            )
        comparison_rows.append(
            {
                "Data": "Uji benchmark",
                "Status": "Data uji asli",
                "Record": dataset["test_rows"],
                "Repository": dataset["test_repositories"],
                "Precision": f"{testing_metrics['precision']:.1%}",
                "Recall": f"{testing_metrics['recall']:.1%}",
                "F1-score": f"{testing_metrics['f1_score']:.1%}",
                "ROC-AUC": f"{testing_metrics['roc_auc']:.1%}",
            }
        )
        if submitted_eval:
            submitted_metrics = submitted_eval["metrics"]
            comparison_rows.append(
                {
                    "Data": (
                        "Uji internal"
                        if submitted_eval.get("source") == "internal"
                        else "Uji data baru"
                    ),
                    "Status": (
                        "Holdout internal"
                        if submitted_eval.get("source") == "internal"
                        else "Dari file input"
                    ),
                    "Record": submitted_metrics["sample_count"],
                    "Repository": None,
                    "Precision": f"{submitted_metrics['precision']:.1%}",
                    "Recall": f"{submitted_metrics['recall']:.1%}",
                    "F1-score": f"{submitted_metrics['f1_score']:.1%}",
                    "ROC-AUC": (
                        f"{submitted_metrics['roc_auc']:.1%}"
                        if submitted_metrics.get("roc_auc") is not None
                        else "n.a."
                    ),
                }
            )
        comparison_frame = pd.DataFrame(comparison_rows)
        st.dataframe(
            comparison_frame,
            width="stretch",
            hide_index=True,
            column_config={
                "Data": st.column_config.TextColumn(
                    "Sumber data",
                    help="Setiap baris dihitung terpisah dan tidak digabungkan.",
                ),
                "Status": st.column_config.TextColumn(
                    "Status",
                    help=(
                        "Data latih membentuk model. Uji benchmark merupakan "
                        "holdout asli. Uji data baru berasal dari file yang diunggah pengguna."
                    ),
                ),
                "Record": st.column_config.NumberColumn(
                    "Record",
                    format="%d",
                ),
                "Repository": st.column_config.NumberColumn(
                    "Repository",
                    format="%d",
                ),
            },
        )
        st.caption(
            "Metrik setiap baris dihitung dari dataset masing-masing. "
            "Kode dari editor dapat membentuk snapshot latih versi baru, "
            "sedangkan file upload hanya dipakai untuk evaluasi. Data benchmark "
            "tidak pernah ditambahkan ke pelatihan."
        )
        left, right = st.columns([1, 1])
        with left:
            importance = dataset["feature_importances"]
            figure = go.Figure(
                go.Bar(
                    x=[importance[name] * 100 for name in FEATURE_LABELS],
                    y=[FEATURE_LABELS[name] for name in FEATURE_LABELS],
                    orientation="h",
                    marker_color=["#0f766e", "#70aa9e", "#bad6d0"],
                    text=[f"{importance[name] * 100:.1f}%" for name in FEATURE_LABELS],
                    textposition="outside",
                )
            )
            figure.update_layout(
                height=260,
                margin={"l": 8, "r": 35, "t": 44, "b": 10},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis={"gridcolor": "#ebf1ef", "ticksuffix": "%", "range": [0, 108]},
                yaxis={"autorange": "reversed"},
                showlegend=False,
            )
            st.markdown(
                inline_help_heading("Kontribusi fitur", "feature_importance"),
                unsafe_allow_html=True,
            )
            st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})
        with right:
            confusion = metrics["confusion_matrix"]
            st.markdown(
                inline_help_heading("Confusion matrix data uji", "confusion_matrix"),
                unsafe_allow_html=True,
            )
            confusion_labels = (
                f'<span>Benar negatif {info_icon("true_negative", "right")}</span>'
                f'<span>Salah positif {info_icon("false_positive", "right")}</span>'
                f'<span>Salah negatif {info_icon("false_negative", "right")}</span>'
                f'<span>Benar positif {info_icon("true_positive", "right")}</span>'
            )
            st.markdown(
                f'<div class="metric-label" style="flex-wrap:wrap;gap:.8rem;'
                f'margin:.1rem 0 .6rem">{confusion_labels}</div>',
                unsafe_allow_html=True,
            )
            st.dataframe(
                pd.DataFrame(
                    [
                        ["Benar negatif", confusion["true_negative"]],
                        ["Salah positif", confusion["false_positive"]],
                        ["Salah negatif", confusion["false_negative"]],
                        ["Benar positif", confusion["true_positive"]],
                    ],
                    columns=["Kategori", "Jumlah"],
                ),
                width="stretch",
                hide_index=True,
                column_config={
                    "Kategori": st.column_config.TextColumn(
                        "Kategori",
                        help=TERM_HELP["confusion_matrix"],
                    ),
                    "Jumlah": st.column_config.NumberColumn(
                        "Jumlah",
                        help="Jumlah record yang masuk ke kategori tersebut.",
                    ),
                },
            )
            st.markdown(
                f'<div class="note">{html.escape(metrics["split_protocol"] if "split_protocol" in metrics else dataset["split_protocol"])} '
                f'Threshold {metrics["threshold"] * 100:.2f}% dipilih dari out-of-fold data latih.</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            inline_help_heading(
                "Jejak pembersihan data",
                "duplicates_removed",
            ),
            unsafe_allow_html=True,
        )
        render_metric_grid(
            [
                metric_card(
                    "Baris mentah",
                    f"{quality['raw_rows']:,}",
                    "Pesan Pylint",
                    help_key="raw_rows",
                    tip_side="start",
                ),
                metric_card(
                    "Duplikasi dihapus",
                    f"{quality['duplicate_rows_removed']:,}",
                    "Satu baris per kode unik",
                    help_key="duplicates_removed",
                ),
                metric_card(
                    "Dataset bersih",
                    f"{dataset['rows']:,}",
                    "Record siap latih",
                    help_key="clean_rows",
                ),
                metric_card(
                    "Repository",
                    f"{dataset['repositories']:,}",
                    f"{dataset['repositories']} sumber proyek",
                    help_key="repositories",
                    tip_side="left",
                ),
            ]
        )
        st.markdown(
            f'<div class="note">Label positif menggunakan Pylint <strong>R0915</strong> '
            f'(too-many-statements). Data uji memakai {dataset["test_rows"]:,} record dari '
            f'{dataset["test_repositories"]} repository yang terpisah dari data latih.</div>',
            unsafe_allow_html=True,
        )


def hero() -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow"><span class="eyebrow-dot"></span>CodeScope / Research Prototype</div>
            <h1>Deteksi Long Method pada kode Python.</h1>
            <p>Masukkan fungsi Python, ekstrak fitur statis melalui AST, lalu baca hasil klasifikasi Decision Tree beserta aturan keputusan yang memengaruhinya.</p>
            <div class="hero-badges">
                <span class="hero-badge">Python AST {info_icon("ast", "start")}</span>
                <span class="hero-badge">3 fitur statis {info_icon("static_features", "right")}</span>
                <span class="hero-badge">Decision Tree {info_icon("decision_tree", "right")}</span>
                <span class="hero-badge">Dashboard terpadu {info_icon("dashboard", "left")}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_styles()
    hero()
    st.markdown(
        f'<div class="help-hint">{info_icon("tooltip", "start")}'
        "<span>Arahkan kursor ke ikon i untuk melihat penjelasan istilah.</span></div>",
        unsafe_allow_html=True,
    )
    flash_message = st.session_state.pop("flash_message", None)
    if flash_message:
        st.toast(flash_message)
    retrain_notice = st.session_state.pop("retrain_notice", None)
    if retrain_notice:
        level, message = retrain_notice
        if level == "success":
            st.success(message)
        else:
            st.warning(message)

    missing = [
        path
        for path in (MODEL_PATH, METRICS_PATH, PROCESSED_DATA_PATH, QUALITY_PATH)
        if not path.exists()
    ]
    if missing:
        st.error(
            "Artifact belum lengkap. Jalankan pipeline data dan pelatihan terlebih dahulu."
        )
        st.code(
            ".\\.venv\\Scripts\\python.exe -m scripts.prepare_dataset path\\ke\\codesmell_dataset.csv\n"
            ".\\.venv\\Scripts\\python.exe -m scripts.train_model"
        )
        st.stop()

    version_registry = load_version_registry(ARTIFACTS_DIR, PROCESSED_DATA_PATH)
    versions = version_registry["versions"]
    active_version = versions[-1]
    active_model_path, metrics_payload = load_version_payload(
        ARTIFACTS_DIR,
        int(active_version["version"]),
    )
    bundle = cached_model(str(active_model_path))
    quality = cached_json(str(QUALITY_PATH))

    st.session_state.setdefault("code_input", SHORT_METHOD)
    input_column, info_column = st.columns([1.65, 0.75], gap="large")

    with input_column:
        st.markdown(
            """
            <div class="section-heading">
                <h2>Analisis kode Python</h2>
                <p>Satu skrip dapat berisi beberapa fungsi atau method.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        example_a, example_b, ide_test_button, example_c = st.columns(4)
        if example_a.button("Contoh pendek", width="stretch", key="example_short"):
            st.session_state.code_input = SHORT_METHOD
            st.rerun()
        if example_b.button("Contoh panjang", width="stretch", key="example_long"):
            st.session_state.code_input = LONG_METHOD
            st.rerun()
        if ide_test_button.button(
            "Contoh uji 60 fungsi",
            width="stretch",
            key="example_ide_test",
        ):
            st.session_state.code_input = MULTI_FUNCTION_TEST_PATH.read_text(
                encoding="utf-8"
            )
            st.rerun()
        if example_c.button("Kosongkan", width="stretch", key="example_clear"):
            st.session_state.code_input = ""
            st.rerun()

        with st.form("analysis_form", clear_on_submit=False):
            st.text_area(
                "Kode Python",
                key="code_input",
                height=380,
                placeholder="def fungsi_saya(...): ...",
                label_visibility="collapsed",
            )
            if AUTO_RETRAIN_ENABLED:
                st.caption(
                    "Setiap submit membuat snapshot latih versi baru. V1 dan "
                    "seluruh nilai versi lama tetap beku; data benchmark tidak "
                    "ikut dilatih."
                )
            submitted = st.form_submit_button(
                "Analisis dan tampilkan dashboard",
                type="primary",
                width="stretch",
                key="analyze_button",
            )
        if submitted:
            try:
                with st.spinner(
                    "Menganalisis kode dan menyiapkan snapshot model baru..."
                ):
                    result = analyze_code(st.session_state.code_input, bundle)
                    result["analysis_version"] = int(active_version["version"])
                    try:
                        result = add_automatic_labels(
                            st.session_state.code_input,
                            result,
                        )
                    except Exception as oracle_error:
                        for function in result["functions"]:
                            function["actual_label"] = None
                            function["actual_label_name"] = "Tidak tersedia"
                            function["actual_label_source"] = "Pylint R0915"
                            function["test_outcome"] = "Tidak tersedia"
                        result["oracle"] = {"error": str(oracle_error)}
                        st.warning(
                            "Prediksi model berhasil, tetapi label pembanding "
                            f"R0915 tidak dapat dihitung: {oracle_error}"
                        )
                    ide_records = [
                        {
                            "code_hash": function["code_hash"],
                            "function_name": function["name"],
                            "actual_label": function["actual_label"],
                            "predicted_label": int(function["is_flagged"]),
                            "probability": float(function["probability"]),
                            "test_outcome": function["test_outcome"],
                        }
                        for function in result["functions"]
                        if function.get("actual_label") is not None
                    ]
                    result["ide_test_metrics"] = evaluate_user_cases(
                        ide_records,
                    )
                    result["ide_test_records"] = ide_records
                    st.session_state.latest_result = result

                    if AUTO_RETRAIN_ENABLED:
                        training_records = [
                            {
                                "code_hash": function["code_hash"],
                                "function_name": function["name"],
                                "features": dict(function["features"]),
                                "actual_label": function["actual_label"],
                            }
                            for function in result["functions"]
                            if function.get("actual_label") is not None
                        ]
                        retrain = create_next_version(
                            ARTIFACTS_DIR,
                            PROCESSED_DATA_PATH,
                            training_records,
                        )
                        if retrain and retrain.get("created"):
                            skipped_parts = []
                            if retrain["duplicates_skipped"]:
                                skipped_parts.append(
                                    f"{retrain['duplicates_skipped']} duplikat"
                                )
                            if retrain["benchmark_overlap_skipped"]:
                                skipped_parts.append(
                                    f"{retrain['benchmark_overlap_skipped']} "
                                    "record yang sama dengan benchmark"
                                )
                            skipped_text = (
                                " Bagian yang dilewati: "
                                + ", ".join(skipped_parts)
                                + "."
                                if skipped_parts
                                else ""
                            )
                            st.session_state.retrain_notice = (
                                "success",
                                f"V{retrain['version']} berhasil dilatih dari "
                                f"{retrain['added_rows']} record input baru. "
                                "V1 dan nilai sebelumnya tetap tersimpan."
                                f"{skipped_text}",
                            )
                        elif retrain:
                            st.session_state.retrain_notice = (
                                "warning",
                                retrain["reason"],
                            )
                        else:
                            st.session_state.retrain_notice = (
                                "warning",
                                "Model tidak dilatih ulang karena label R0915 "
                                "belum tersedia untuk input ini.",
                            )
                st.session_state.flash_message = "Analisis selesai."
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    with info_column:
        st.markdown(
            f"""
            <div class="section-heading">
                <h2>Model aktif {active_version['label']}
                    {info_icon("model_version", "left")}</h2>
                <p>Versi terbaru yang dipakai untuk prediksi</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        metrics = metrics_payload["metrics"]
        threshold = bundle["threshold"]
        st.markdown(
            f"""
            <div class="metric-card accent">
                <div class="metric-label">
                    <span>Decision Tree</span>{info_icon("decision_tree", "right")}
                </div>
                <div class="metric-value">{metrics['f1_score']:.1%}</div>
                <div class="metric-note">
                    F1-score pada data uji repository terpisah
                    {info_icon("f1_score", "left")}
                </div>
            </div>
            <div style="height:.75rem"></div>
            <div class="metric-card">
                <div class="metric-label">
                    <span>Threshold klasifikasi</span>{info_icon("threshold", "left")}
                </div>
                <div class="metric-value">{threshold * 100:.2f}%</div>
                <div class="metric-note">Dikalibrasi dari out-of-fold data latih</div>
            </div>
            <div style="height:.75rem"></div>
            <div class="metric-card">
                <div class="metric-label">
                    <span>Fitur input</span>{info_icon("static_features", "left")}
                </div>
                <div class="metric-value" style="font-size:1.1rem;line-height:1.6">
                    LOC {info_icon("nloc", "right")}<br>
                    Parameter {info_icon("parameter_count", "right")}<br>
                    Percabangan {info_icon("branch_count", "right")}
                </div>
                <div class="metric-note">Diekstraksi langsung dari Python AST</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_testing_panel(
            st.session_state.get("latest_result"),
            bundle,
            metrics_payload,
        )

    render_version_comparison(ARTIFACTS_DIR, versions)
    render_version_management(versions)

    with st.expander("Uji dataset baru dari file", expanded=False):
        st.write(
            "Unggah beberapa fungsi Python berlabel otomatis R0915 untuk "
            "membandingkan precision, recall, dan F1-score dengan data latih."
        )
        if st.button(
            "Gunakan data uji internal",
            key="load_internal_test",
            width="stretch",
        ):
            internal_metrics = dict(
                metrics_payload["metrics"].get(
                    "testing_metrics",
                    metrics_payload["metrics"],
                )
            )
            internal_metrics["sample_count"] = metrics_payload["dataset"]["test_rows"]
            st.session_state.submitted_dataset_eval = {
                "filename": "Data uji internal (24 repository holdout)",
                "source": "internal",
                "metrics": internal_metrics,
                "records": [],
            }
            st.rerun()
        st.caption(
            "Gunakan file .py berisi beberapa fungsi, atau .csv dengan kolom "
            "`code`. File harus memuat fungsi Long Method dan bukan Long Method."
        )
        uploaded_dataset = st.file_uploader(
            "File data uji baru",
            type=["py", "csv"],
            key="submitted_dataset_file",
        )
        if st.button(
            "Hitung metrik data uji",
            key="evaluate_submitted_dataset",
            type="primary",
            width="stretch",
            disabled=uploaded_dataset is None,
        ):
            try:
                with st.spinner("Mengevaluasi dataset uji baru..."):
                    uploaded_content = uploaded_dataset.getvalue()
                    st.session_state.submitted_dataset_eval = (
                        evaluate_submitted_dataset(
                            uploaded_dataset.name,
                            uploaded_content,
                            bundle,
                        )
                    )
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

        submitted_eval = st.session_state.get("submitted_dataset_eval")
        if submitted_eval:
            submitted_metrics = submitted_eval["metrics"]
            st.success(
                f"{submitted_eval['filename']} berhasil diuji pada "
                f"{submitted_metrics['sample_count']:,} fungsi."
            )
            st.markdown(
                f"Precision **{submitted_metrics['precision']:.1%}**, "
                f"Recall **{submitted_metrics['recall']:.1%}**, "
                f"F1-score **{submitted_metrics['f1_score']:.1%}**."
            )
            if st.button(
                "Hapus hasil uji dataset",
                key="clear_submitted_dataset",
            ):
                del st.session_state["submitted_dataset_eval"]
                st.rerun()

    latest = st.session_state.get("latest_result")
    if latest:
        render_result(latest)
    else:
        st.markdown(
            """
            <div style="height:1rem"></div>
            <div class="empty-state">
                <strong>Dashboard menunggu kode untuk dianalisis.</strong>
                <span>Pilih contoh di atas atau tempel fungsi Python, lalu jalankan analisis.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_model_summary(metrics_payload, quality)


if __name__ == "__main__":
    main()

