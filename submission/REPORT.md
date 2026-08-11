# Báo cáo cá nhân Day 13 Observability

## 1. Thông tin nhóm

- Họ và tên: **NGUYỄN MẠNH HƯNG**
- MSSV: **2A202601829**
- Hình thức: **Bài cá nhân**
- Repository URL: [Day13-K3-Observability-2A202601829-NguyenManhHung](https://github.com/hungnm13304/Day13-K3-Observability-2A202601829-NguyenManhHung)
- Commit SHA cuối: _Lấy bằng `git rev-parse HEAD` sau commit cuối_
- Thành viên và vai trò: Nguyễn Mạnh Hưng — Logging/PII, tracing, prompt versioning, dashboard và incident evidence.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: **100/100**.
- Tổng số traces: **31 traces** trong project Langfuse `Day13` tại thời điểm kiểm tra.
- Số PII leak còn lại: **0**.
- Kết quả `validate_dashboard.py`: **HỢP LỆ: 6/6 panel**.
- Link/đường dẫn dashboard: [Dashboard runtime evidence](evidence/dashboard.png)

Evidence:

- [Health và tracing](evidence/health-tracing-enabled.png)
- [Kết quả logging/PII](evidence/validate-logs-100.png)
- [Dashboard validator](evidence/10-dashboard-validator.png)

## 3. Logging và tracing

- Evidence correlation ID và metadata: [log-correlation-pii.png](evidence/03-log-correlation-pii.png)
- Evidence PII redaction: [validate-logs-100.png](evidence/validate-logs-100.png)
- Evidence trace waterfall: [trace-waterfall.png](evidence/05-trace-waterfall.png)
- Mỗi request có `correlation_id`, `user_id_hash`, `session_id`, `feature`, `model` và các trường latency/token/cost/quality cần thiết.
- PII được scrub trước khi log JSON được render; validator phát hiện 0 PII leak.
- Span đáng chú ý là generation của agent: trace chứa prompt name/label/version, token usage, cost và latency để liên kết từ trace sang log cùng request.

## 4. Prompt versioning

- Prompt name: `day13-chat`.
- Version/label baseline: version 1, label `production` (và baseline khi kiểm thử).
- Version/label candidate: version 2, label `candidate`.
- Prompt source: `langfuse`.
- Trace version 1: [trace-version-1.png](evidence/06-trace-version-1.png).
- Trace version 2/candidate: [trace-version-2-candidate.png](evidence/07-trace-version-2-candidate.png).
- Production chuyển sang version 2: [production-version-2.png](evidence/08-production-version-2.png).
- Trace metadata xác nhận `prompt_name`, `prompt_label` và `prompt_version` tương ứng với từng trace.
- Bằng chứng rollback: [prompt-rollback.png](evidence/prompt-rollback.png)

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: **HỢP LỆ: 6/6 panel**.
- Evidence validator: [validate-dashboard.txt](evidence/validate-dashboard.txt).
- Evidence dashboard runtime: [dashboard.png](evidence/dashboard.png)
- Dashboard sử dụng `data/logs.jsonl` và gồm latency P50/P95/P99, traffic, error rate, cost, tokens input/output và quality proxy.
- SLO chính: P95 latency không vượt 3000 ms, error rate không vượt 2%, quality trung bình không thấp hơn 0.75. Các ngưỡng được chọn để phản ánh latency, độ ổn định và chất lượng trải nghiệm người dùng.
- Alert rules: [config/alert_rules.yaml](../config/alert_rules.yaml)
- Runbook: [docs/alerts.md](../docs/alerts.md)

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`.
- Cohort: `K3`.
- Incident: `rag_slow`.
- Triệu chứng từ metrics: P95 latency **2650 ms**, vượt threshold chính thức **2000 ms**; error breakdown rỗng.
- Evidence metrics: [challenge-metrics.json](evidence/challenge-metrics.json).
- Trace ID liên quan: `bba43e0af0d3b37f1cb1f6b211f862d0`.
- Session liên quan: `k3-challenge-s01`.
- Log correlation ID liên quan: `req-7447d92b`.
- Evidence trace: [challenge-trace.txt](evidence/challenge-trace.txt).
- Evidence log: [challenge-log-lines.jsonl](evidence/challenge-log-lines.jsonl).
- Root cause: khi incident `rag_slow` được bật, bước retrieval cố ý thêm khoảng 2.5 giây delay; vì vậy latency response tăng lên 2650 ms.
- Fix action: tắt incident sau khi điều tra và loại bỏ/khắc phục độ trễ retrieval trong môi trường production.
- Preventive measure: đặt alert cho P95 retrieval/response latency vượt ngưỡng, theo dõi retrieval span riêng và liên kết metric → trace → log bằng correlation/session ID.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Mạnh Hưng (2A202601829) | Logging/PII, Checkpoint 2, dashboard, prompt versioning, alerts và challenge evidence | _Điền commit SHA cuối_ | Tracing, prompt labels/version và điều tra metrics → traces → logs |
