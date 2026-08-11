# Alert và Runbook Day 13

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: High response latency
- Severity: Critical
- SLI/SLO liên quan: `latency_p95_ms`, mục tiêu P95 không vượt 3000 ms.
- Điều kiện và thời gian duy trì: `latency_p95_ms > 3000` trong 5 phút liên tục.
- Ảnh hưởng tới người dùng: Chat phản hồi chậm, timeout hoặc trải nghiệm suy giảm.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra latency P50/P95/P99 và feature bị ảnh hưởng.
  2. Mở trace chậm nhất trong cùng time window, so sánh thời gian các observation.
  3. Tìm log có cùng correlation ID để xác định bước gây chậm.
- Mitigation tạm thời: giảm concurrency/traffic, tắt feature hoặc incident đang làm tăng latency, rồi theo dõi P95 hồi phục.
- Owner: platform-oncall

## Alert 2

- Tên: Elevated error rate
- Severity: High
- SLI/SLO liên quan: `error_rate_pct`, mục tiêu error rate không vượt 2%.
- Điều kiện và thời gian duy trì: `error_rate_pct > 2` trong 5 phút liên tục.
- Ảnh hưởng tới người dùng: Request thất bại, trả lỗi 5xx hoặc không nhận được câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra error rate và breakdown theo `error_type`.
  2. Mở một trace lỗi trong khoảng thời gian alert.
  3. Tìm log `request_failed` có cùng correlation ID và kiểm tra exception.
- Mitigation tạm thời: rollback thay đổi gần nhất, giảm traffic hoặc chuyển sang fallback an toàn nếu có.
- Owner: platform-oncall

## Alert 3

- Tên: Quality or cost degradation
- Severity: Warning
- SLI/SLO liên quan: `quality_score_avg` mục tiêu tối thiểu 0.75 và `daily_cost_usd` mục tiêu không vượt 2.5 USD.
- Điều kiện và thời gian duy trì: `quality_score_avg < 0.75` trong 10 phút hoặc `daily_cost_usd > 2.5`.
- Ảnh hưởng tới người dùng: Câu trả lời kém hữu ích hoặc chi phí vận hành tăng bất thường.
- Ba bước kiểm tra đầu tiên:
  1. So sánh quality, token input/output và cost với traffic cùng thời gian.
  2. Kiểm tra prompt name/label/version và model trên trace.
  3. Kiểm tra câu trả lời mẫu, retrieved document count và log response tương ứng.
- Mitigation tạm thời: rollback prompt label, giới hạn output/token, giảm traffic hoặc tạm tắt feature tốn chi phí.
- Owner: ai-platform
