# Research card

**Người thực hiện:** Dương Quang Bảo — 2A202503362  
**Hướng nghiên cứu:** R4 · Evaluation confounders

## Phiếu nghiên cứu

| Field | Nội dung |
|---|---|
| CÂU | R4 — Evaluation confounders |
| SOURCE | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* (nguồn tham khảo được liệt kê trong template bài lab; cần bổ sung URL/bản paper chính thức nếu giảng viên yêu cầu trích dẫn đầy đủ). |
| CLAIM | Khi so sánh hiệu quả các kiến trúc multi-agent, cần kiểm soát các yếu tố gây nhiễu như model, tool, seed, corpus, pricing và evaluator. Nếu nhiều biến thay đổi cùng lúc, không thể quy kết chênh lệch metric cho riêng topology. |
| BOUNDARY | Thực nghiệm hiện có sử dụng MockLLM deterministic, eval set mô phỏng LogiX-VN và seed cố định. Kết quả chỉ mô tả setup này, không đại diện model thật hoặc môi trường production. |
| HYPOTHESIS | Nếu thay đổi topology trong khi giữ nguyên model, tools, seed, corpus, pricing và evaluator, pass rate/cost có thể thay đổi do cách phối hợp agent. Multi-agent có thể tăng khả năng xử lý nhưng cũng có thể tăng cost và variance; topology phức tạp hơn không mặc nhiên tốt hơn. |
| METHOD | Giữ cố định MockLLM, tool registry, eval set SHA, seeds, pricing, evaluator và môi trường. Chỉ thay đổi topology: workflow, single, orchestrator hoặc swarm. |
| FAILURE / METRIC | Theo dõi `pass_rate`, `pass_hat_5`, variance, `cost_per_success`, `approval_bypass` và `secret_leak`. Không chấp nhận cải thiện pass rate nếu phát sinh safety failure. |

## Kết quả thực nghiệm hiện có

### Baseline v2

Nguồn: `src/reports/baseline_v2.json`.

- Run ID: `E-swarm-20261117-f8df`.
- Shape: `swarm`.
- Eval set SHA: `f8df34ea9092`.
- 28 items × 5 seeds = 140 trials.
- `pass_rate`: 97.86%.
- `pass_hat_5`: 89.29%.
- `approval_bypass`: 0/140.
- `secret_leak`: 0/140.
- `cost_per_success`: 50.8077 đơn vị cost mô phỏng.

### A/A calibration

Nguồn: `src/reports/aa_calibration.json`.

- Nhóm A seeds: 121, 132, 143, 154, 165.
- Nhóm B seeds: 176, 187, 198, 209, 220.
- `pass_rate`: 0.978571 ở cả hai nhóm.
- `pass_hat_5`: 0.892857 ở cả hai nhóm.
- Delta: 0; CI 95% được report ghi nhận [0, 0].

Hai nhóm seed cho kết quả giống nhau trên setup hiện tại. Điều này cho thấy phép đo ổn định với MockLLM deterministic, nhưng không chứng minh model thật không có biến động.

## Phân biệt A/A và ablation topology

A/A calibration kiểm tra độ ổn định của setup đánh giá giữa hai nhóm seed. Nó **không** phải là ablation topology và không chứng minh swarm tốt hơn workflow, single hoặc orchestrator.

Tại thời điểm lập phiếu, chưa có artifact benchmark so sánh bốn shape trên cùng corpus và seed. Các module `workflow.py`, `single.py`, `orchestrator.py` vẫn là stub `not_implemented`; do đó chưa thể kết luận hypothesis về topology đúng hay sai.

## Kế hoạch ablation cần thực hiện

Sau khi hoàn thiện ba shape còn lại:

1. Dùng chung một eval corpus và xác nhận SHA.
2. Dùng cùng danh sách seed cho cả bốn shape.
3. Giữ nguyên model, tools, pricing, evaluator và môi trường.
4. Chỉ thay đổi shape.
5. Sinh `src/reports/benchmark.json`.
6. So sánh pass rate, pass^5, seed min–max, variance, cost/success và safety metrics.

Lệnh benchmark cần dùng đúng CLI được khai báo trong repository sau khi xác nhận implementation và help của module; không ghi nhận một lệnh chưa chạy như kết quả thực nghiệm.

## Kết luận

Kết quả hiện có xác nhận baseline swarm v2 đạt pass rate 97.86%, pass_hat_5 89.29%, không ghi nhận approval bypass hoặc secret leak trong 140 trials. A/A calibration cho delta bằng 0 trên MockLLM deterministic.

Tuy nhiên, chưa có ablation topology hợp lệ để xác định shape nào tốt nhất. Kết luận về lợi ích của multi-agent cần chờ benchmark bốn shape với các yếu tố còn lại được kiểm soát.
