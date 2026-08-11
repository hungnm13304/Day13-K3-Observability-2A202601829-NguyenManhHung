from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import streamlit as st
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"
CONFIG_PATH = REPO_ROOT / "config" / "dashboard.yaml"


def load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_records() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    records: list[dict] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            record["_timestamp"] = parse_timestamp(record["ts"])
            records.append(record)
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=60)
    return [record for record in records if record["_timestamp"] >= cutoff]


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    index = min(len(values) - 1, max(0, math.ceil((p / 100) * len(values)) - 1))
    return values[index]


def response_records(records: list[dict]) -> list[dict]:
    return [record for record in records if record.get("event") == "response_sent"]


def request_count(records: list[dict], event: str) -> int:
    return sum(1 for record in records if record.get("event") == event)


def minute_series(records: list[dict], field: str) -> dict[str, float]:
    buckets: defaultdict[str, float] = defaultdict(float)
    for record in records:
        timestamp = record["_timestamp"].replace(second=0, microsecond=0).isoformat()
        buckets[timestamp] += float(record.get(field) or 0)
    return dict(sorted(buckets.items()))


def render_dashboard() -> None:
    config = load_config()["dashboard"]
    records = load_records()
    responses = response_records(records)
    latencies = [float(record.get("latency_ms") or 0) for record in responses]
    errors = [record for record in records if record.get("event") == "request_failed"]
    total_requests = request_count(records, "request_received")
    error_rate = (len(errors) / total_requests * 100) if total_requests else 0.0
    traffic_per_minute = total_requests / max(config["time_range_minutes"], 1)
    total_cost = sum(float(record.get("cost_usd") or 0) for record in responses)
    total_tokens_in = sum(int(record.get("tokens_in") or 0) for record in responses)
    total_tokens_out = sum(int(record.get("tokens_out") or 0) for record in responses)
    quality_values = [float(record.get("quality_score") or 0) for record in responses]
    quality_avg = sum(quality_values) / len(quality_values) if quality_values else 0.0

    st.title(config["title"])
    st.caption(
        f"Nguồn: data/logs.jsonl · Time range: {config['time_range_minutes']} phút · "
        f"Refresh: {config['refresh_seconds']} giây · Records: {len(records)}"
    )

    if not records:
        st.warning("Chưa có log trong 60 phút gần nhất. Hãy chạy API và load test trước.")
        return

    latency_threshold = config["panels"][0]["threshold"]["value"]
    error_threshold = config["panels"][2]["threshold"]["value"]
    cost_threshold = config["panels"][3]["threshold"]["value"]
    token_threshold = config["panels"][4]["threshold"]["value"]
    quality_threshold = config["panels"][5]["threshold"]["value"]

    left, right = st.columns(2)
    with left:
        st.subheader("Latency percentiles")
        p50, p95, p99 = (percentile(latencies, p) for p in (50, 95, 99))
        a, b, c = st.columns(3)
        a.metric("P50 (ms)", f"{p50:.0f}")
        b.metric("P95 (ms)", f"{p95:.0f}", delta=f"threshold {latency_threshold} ms")
        c.metric("P99 (ms)", f"{p99:.0f}")
        st.caption(f"SLO: P95 ≤ {latency_threshold} ms")
    with right:
        st.subheader("Request traffic")
        st.metric("Requests", total_requests)
        st.metric("Rate", f"{traffic_per_minute:.2f} requests/min")

    left, right = st.columns(2)
    with left:
        st.subheader("Error rate and breakdown")
        st.metric("Error rate", f"{error_rate:.2f}%", delta=f"threshold {error_threshold}%")
        breakdown = Counter(record.get("error_type", "unknown") for record in errors)
        if breakdown:
            st.bar_chart(dict(breakdown))
        else:
            st.info("No errors in the selected 60-minute window.")
    with right:
        st.subheader("Cost over time")
        st.metric("Total cost", f"${total_cost:.4f}", delta=f"threshold ${cost_threshold}")
        cost_series = minute_series(responses, "cost_usd")
        if cost_series:
            st.line_chart(cost_series)

    left, right = st.columns(2)
    with left:
        st.subheader("Input and output tokens")
        st.metric("Input tokens", f"{total_tokens_in:,}")
        st.metric("Output tokens", f"{total_tokens_out:,}")
        st.caption(f"Combined SLO threshold: {token_threshold:,} tokens")
    with right:
        st.subheader("Quality proxy")
        st.metric("Average quality", f"{quality_avg:.2f}", delta=f"threshold {quality_threshold:.2f}")
        st.caption("SLO: average quality ≥ 0.75")

    st.divider()
    st.caption(f"Last refresh: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}")


st.set_page_config(page_title=load_config()["dashboard"]["title"], layout="wide")

if hasattr(st, "fragment"):
    @st.fragment(run_every="30s")
    def auto_refresh_dashboard() -> None:
        render_dashboard()

    auto_refresh_dashboard()
else:  # pragma: no cover - compatibility with older Streamlit versions
    render_dashboard()
