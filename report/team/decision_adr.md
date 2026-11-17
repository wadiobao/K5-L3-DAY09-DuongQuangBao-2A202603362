# Decision record

**Người thực hiện:** Dương Quang Bảo — 2A202503362

- Shape chọn: swarm
- Commit hash: 07fd6a48d5795d1c9ca30e21a1713b966574253d
- Run id dẫn chứng: E-swarm-20261117-f8df
- Pass rate / pass^5 / seed min-max / variance: 97.86% / 89.29% / 89.29%–100% / 0.001837 (population variance của pass rate qua 5 seed)
- Cost per success (mô phỏng, VND): 50.8077 đơn vị cost mô phỏng/trial thành công; không phải chi phí VND thực tế.
- Crash safety: Chưa có artifact `src/reports/crash.json`; chưa xác nhận được tỷ lệ crash safety 20/20. Cross-platform CI thành công không thay thế crash suite.
- Secret leak / approval bypass: 0/140 / 0/140 trong baseline v2.

## Vì sao chọn shape này

Tạm chọn `swarm` làm shape được ghi nhận trong decision record vì repository hiện có implementation tham chiếu và baseline v2 tương ứng. Run `E-swarm-20261117-f8df` chạy trên 28 item với 5 seed, tổng cộng 140 trials. Kết quả đạt pass rate 97.86%, pass^5 89.29%, `approval_bypass = 0` và `secret_leak = 0`.

Đây là lựa chọn tạm thời theo bằng chứng hiện có, không phải kết luận swarm tốt nhất. Ba shape `workflow`, `single` và `orchestrator` hiện vẫn là stub `not_implemented`; chưa có benchmark bốn shape trên cùng corpus và seed. Cần cập nhật quyết định sau khi hoàn thiện implementation và benchmark công bằng.

## Có đáng đổi lấy multi-agent không

Multi-agent có thể chia nhỏ nhiệm vụ điều tra và tổng hợp thông tin, nhưng cũng làm tăng số lần gọi model, cost và độ phức tạp điều phối. Số lượng agent không phải thước đo chất lượng.

Chỉ giữ kiến trúc multi-agent nếu benchmark chứng minh lợi ích về pass rate hoặc khả năng xử lý failure mode mà vẫn đáp ứng các điều kiện:

- Không có approval bypass.
- Không có secret leak.
- Không phát sinh refund trùng sau crash.
- Cost per success nằm trong giới hạn chấp nhận được.
- Kết quả ổn định qua nhiều seed.

Nếu workflow hoặc single đạt chất lượng tương đương với chi phí thấp hơn và độ ổn định tốt hơn, nên ưu tiên kiến trúc đơn giản hơn.

## Trace và bằng chứng

Trace được dùng để ghi lại quá trình xử lý và hỗ trợ truy vết trial thất bại. Các event có ý nghĩa gồm handoff, kết quả investigator, quote, decision, model override và crash khi có phát sinh.

Handoff phải theo allowlist. Không ghi `parent_secret`, raw Authorization headers hoặc toàn bộ parent context vào trace. Investigator chỉ có quyền đọc; quyền ghi refund thuộc host. Lý do là giảm nguy cơ lộ thông tin nhạy cảm và tránh để agent con vượt quá quyền được cấp.

Bằng chứng đánh giá hiện có:

- `src/reports/baseline_v2.json`.
- `src/reports/aa_calibration.json`.
- `src/config/metric_spec_v2.yaml`.
- `docs/failure_taxonomy.md`.
- `docs/eval_card.md`.
- `docs/judge_audit.md`.
- [Lab 9 Eval Gate](https://github.com/wadiobao/K5-L3-DAY09-DuongQuangBao-2A202603362/actions/runs/44128099288).
- [Cross-platform CI](https://github.com/wadiobao/K5-L3-DAY09-DuongQuangBao-2A202603362/actions/runs/44126846537).

Baseline v2 không ghi nhận secret leak và approval bypass trong 140 trials. Đây là kết quả trên eval set mô phỏng, không phải chứng minh tuyệt đối hệ thống không thể gặp lỗi trong mọi tình huống.

## Giới hạn

1. MockLLM không đại diện model sản xuất.
2. Eval set v2 có 28 item.
3. Cost là đơn vị mô phỏng, không phải chi phí API thực tế.
4. Latency của MockLLM không khả dụng.
5. Chưa có benchmark đầy đủ bốn shape.
6. Chưa có `crash.json` để xác nhận crash safety.
7. Chưa có dữ liệu production hoặc hidden evaluation được xác nhận trong report này.

## Điều kiện xem xét lại quyết định

Cập nhật ADR khi ba shape còn lại được triển khai, benchmark bốn shape chạy trên cùng corpus và seed, crash suite có report hợp lệ và có kết quả hidden evaluation.

Nếu một shape đơn giản hơn có pass rate tương đương, không phát sinh safety failure và cost thấp hơn, sẽ ưu tiên shape đó thay cho swarm.
