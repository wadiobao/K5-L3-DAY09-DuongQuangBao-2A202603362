# Báo cáo nhóm — Lab 8 và Lab 9 LogiX-VN

## 1. Thông tin nhóm

- Hình thức thực hiện: Cá nhân.
- Người thực hiện: **Dương Quang Bảo — 2A202503362**.
- GitHub: [wadiobao](https://github.com/wadiobao).
- Repository: https://github.com/wadiobao/K5-L3-DAY09-DuongQuangBao-2A202603362
- Nhánh: `main`.
- Commit code snapshot dùng làm mốc đánh giá: `07fd6a48d5795d1c9ca30e21a1713b966574253d`.

## 2. Mục tiêu và cách tiếp cận

Bài toán yêu cầu xây dựng agent xử lý yêu cầu hoàn phí vận chuyển cho LogiX-VN. Hệ thống cần trả lời dựa trên dữ liệu đơn hàng và policy, không vượt qua approval, không làm lộ dữ liệu nhạy cảm và bảo đảm tính nhất quán của ledger.

Công việc được chia thành hai phần:

1. **Thực thi nghiệp vụ:** phân tách trách nhiệm giữa agent và host. Agent hỗ trợ đọc yêu cầu, tra cứu và soạn phản hồi; host kiểm tra policy, approval, giới hạn hoàn tiền và thực hiện ghi ledger.
2. **Đánh giá:** xây dựng evaluation set, failure taxonomy, metric specification, judge audit và CI gate để đo chất lượng, an toàn và khả năng tái lập.

## 3. Giải pháp và kiến trúc

### 3.1. Ranh giới code và model

| Nghiệp vụ | Thành phần chịu trách nhiệm |
|---|---|
| Kiểm tra principal và quyền truy cập | Host |
| Đọc đơn hàng và policy | Read tools có kiểm soát |
| Tính số tiền bồi thường | Code: `compute_compensation` |
| Kiểm tra approval | Host |
| Ghi refund và kiểm tra idempotency | Host: `durability.issue_refund` |
| Soạn câu trả lời | Agent / MockLLM |

Model không được tự quyết định số tiền hoàn cuối cùng hoặc trực tiếp ghi giao dịch. Host nhận quote và tự kiểm tra giới hạn theo order, approval và lịch sử refund trong transaction.

### 3.2. Bốn shape trong thiết kế

- **Workflow:** chuỗi bước Python cố định; model chỉ hỗ trợ soạn nội dung.
- **Single:** một agent ReAct, giới hạn tối đa 8 bước; host vẫn là thành phần duy nhất có quyền ghi.
- **Orchestrator:** agent điều phối investigator chỉ có quyền đọc; handoff phải theo allowlist.
- **Swarm:** nhiều agent phối hợp, được cung cấp làm shape tham chiếu để đánh giá cost và variance.

Handoff không được chứa `parent_secret`, raw headers hoặc toàn bộ claim row. Investigator không được cấp tool ghi refund.

### 3.3. Trạng thái triển khai

Tại commit code snapshot nêu trên, `src/lab8/shapes/swarm_reference.py` có implementation tham chiếu. Ba module `workflow.py`, `single.py` và `orchestrator.py` vẫn trả về `not_implemented`. Vì vậy, chưa có cơ sở để tuyên bố cả bốn shape đã hoàn thành hoặc đã được benchmark so sánh công bằng. Đây là hạng mục cần hoàn thiện trước khi chốt kết quả Lab 8.

## 4. Kết quả đánh giá

### 4.1. Baseline v2

Nguồn: `src/reports/baseline_v2.json`.

- Run ID: `E-swarm-20261117-f8df`.
- Eval set: `data/eval/eval_set_v2.jsonl`.
- SHA: `f8df34ea9092`.
- 28 items × 5 seeds = 140 trials.
- Model: MockLLM; Python 3.14.2; metric spec 2.0.

| Metric | Kết quả |
|---|---:|
| `approval_bypass` | 0/140 |
| `secret_leak` | 0/140 |
| `db_fact_kept` | 137/140 = 97.86% |
| `refund_amount_correct` | 137/140 = 97.86% |
| `pass_rate` | 137/140 = 97.86% |
| `pass_hat_5` | 25/28 = 89.29% |
| `reply_matches_ledger` | 140/140 = 100% |

### 4.2. Độ ổn định theo seed

| Seed | Pass rate |
|---:|---:|
| 11 | 100% |
| 22 | 100% |
| 33 | 100% |
| 44 | 100% |
| 55 | 89.29% |

Có 25/28 item pass ở cả năm seed, tương ứng `pass_hat_5 = 89.29%`. Kết quả cho thấy vẫn có trường hợp phụ thuộc seed; không nên chỉ dùng một lần chạy để đánh giá agent.

### 4.3. A/A calibration

Nguồn: `src/reports/aa_calibration.json`.

Hai nhóm seed độc lập:

- Nhóm A: 121, 132, 143, 154, 165.
- Nhóm B: 176, 187, 198, 209, 220.

| Metric | Nhóm A | Nhóm B | Delta |
|---|---:|---:|---:|
| `pass_rate` | 97.86% | 97.86% | 0 |
| `pass_hat_5` | 89.29% | 89.29% | 0 |

Khoảng tin cậy 95% của delta được report ghi nhận là [0, 0]. Đây là kết quả trên MockLLM deterministic, không thể suy rộng thành kết luận model thật không có nhiễu.

### 4.4. Judge audit

Nguồn: `docs/judge_audit.md`.

| Criterion | Cohen's κ | Precision | Recall | Quyết định |
|---|---:|---:|---:|---|
| `tone_ok` | 0.757 | 0.857 | 0.800 | Giữ lại |
| `helpful` | 0.375 | 1.000 | 0.300 | Loại khỏi gate |

Judge `helpful` có recall thấp nên không phù hợp làm cổng đánh giá. Các nghiệp vụ quan trọng như tiền, approval và ledger cần được kiểm tra bằng code thay vì phụ thuộc vào LLM judge.

### 4.5. CI

Các workflow đã được xác nhận thành công:

- [Lab 9 Eval Gate](https://github.com/wadiobao/K5-L3-DAY09-DuongQuangBao-2A202603362/actions/runs/44128099288).
- [Cross-platform CI](https://github.com/wadiobao/K5-L3-DAY09-DuongQuangBao-2A202603362/actions/runs/44126846537).
- [Baseline refresh](https://github.com/wadiobao/K5-L3-DAY09-DuongQuangBao-2A202603362/actions/runs/44127091991).

Cross-platform CI chạy trên Ubuntu, Windows và macOS với Python 3.11 và 3.13. Eval Gate chạy các bước kiểm thử Lab 9, evalset và mutation gate.

CI thành công không thay thế cho benchmark bốn shape hoặc crash suite. Repository chưa có `src/reports/benchmark.json` và `src/reports/crash.json`, do đó chưa đủ bằng chứng để báo cáo kết quả benchmark bốn shape và crash safety 20/20.

## 5. Khó khăn và cách xử lý

### 5.1. Eval set không khớp baseline

CI từng báo lỗi `eval_set_sha` do eval set thay đổi trong khi baseline chưa được chạy lại trên cùng dữ liệu.

Cách xử lý: kiểm tra SHA, chạy lại baseline trên eval set hiện tại, cập nhật baseline và chạy lại Eval Gate. Sau đó, workflow Eval Gate hoàn thành thành công.

### 5.2. Độ tin cậy của LLM judge

Judge `helpful` có recall thấp. Tiêu chí này được loại khỏi gate; tiêu chí `tone_ok` được giữ lại. Những điều kiện an toàn và tính đúng đắn nghiệp vụ tiếp tục được đánh giá bằng code.

## 6. Đóng góp cá nhân

Bài tập được thực hiện bởi một người: **Dương Quang Bảo (2A202503362)**.

Các phần việc được ghi nhận trong repository gồm triển khai/tích hợp nội dung Lab 9, quản lý eval set và baseline, cấu hình workflow CI, kiểm tra kết quả CI và chuẩn bị tài liệu đánh giá. Chi tiết bằng chứng được đối chiếu qua lịch sử commit, các file trong `src/reports/` và GitHub Actions.

Không phân chia đóng góp cho thành viên khác vì đây là bài làm cá nhân.

## 7. Hạn chế và hướng cải thiện

1. MockLLM không đại diện đầy đủ cho model thật.
2. Eval set v2 có 28 item, chưa đủ để khẳng định khả năng tổng quát hóa.
3. Cost là đơn vị mô phỏng, không phải chi phí API thực tế.
4. A/A có noise margin bằng 0 do MockLLM deterministic.
5. Ba shape workflow, single và orchestrator vẫn cần implementation hoàn chỉnh.
6. Chưa có artifact benchmark bốn shape và crash suite.
7. Chưa có dữ liệu production hoặc người dùng thật.

Hướng tiếp theo là hoàn thiện ba shape, chạy benchmark trên cùng corpus và seed, chạy crash suite, sau đó cập nhật quyết định kiến trúc dựa trên bằng chứng.

## 8. Tài liệu tham khảo

- `README.md`, `RULES.md`, `CHECKPOINTS.md`, `RUBRIC.md`, `SUBMISSION.md`.
- `docs/architecture.md`, `docs/contracts.md`, `docs/metrics.md`.
- `docs/failure_taxonomy.md`, `docs/eval_card.md`, `docs/judge_audit.md`.
- `src/config/metric_spec_v2.yaml`.
- `src/reports/baseline_v2.json`, `src/reports/aa_calibration.json`.
