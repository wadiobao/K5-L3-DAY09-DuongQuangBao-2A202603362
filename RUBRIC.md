# Rubric

Tám hạng mục và số điểm giữ nguyên như README cũ của lab. Cột **Bằng chứng** và **Ghi chú** gom lại từ các điều kiện đã có trong repo (`check_submission`, ma trận student, grader hidden, `docs/metrics.md`). Đường dẫn `src/reports/` là file do công cụ sinh ra; giảng viên chạy lại đúng các lệnh trong [src/reports/README.md](src/reports/README.md).

| Tiêu chí | Điểm | Bằng chứng | Ghi chú |
|---|---:|---|---|
| C1 — Implementation: ba shape A, B, C (CP2) | 20 | `src/lab8/shapes/workflow.py`, `single.py`, `orchestrator.py`; ma trận `python -m pytest -q -m student -o addopts=`; mục shapes của `python -m lab8.check_submission` | Shape còn `not_implemented`, ném exception hoặc trả sai `RunResult` thì không được điểm phần shape đó. Tiền phải do `compute_compensation` tính, không do MockLLM |
| C2 — Hidden: shape chọn trên 40 claim × 5 seed (CP5) | 15 | `src/reports/hidden_grade.json` (giảng viên tạo, không commit) do giảng viên chạy bằng grader riêng (repo chấm riêng của giảng viên); shape lấy từ dòng `- Shape chọn:` trong `report/team/decision_adr.md` | Cổng: pass rate ≥ 0.75 trên 200 trial. Không sửa JSON cho đủ ngưỡng |
| C3 — Durability: idempotency và crash (CP3, CP4) | 20 | `src/reports/crash.json` (`crash_safety` = `20/20`); T11, T12 trong ma trận student | Gọi lại cùng claim vẫn một dòng ledger; crash rồi resume vẫn một refund, một audit `refund_committed`. Crash tạo hơn một refund là vi phạm must-pass |
| C4 — Policy: approval, policy hiện hành, trần theo đơn (CP2, CP4) | 10 | Ma trận student T01–T14; `approval_bypass_count` trong `src/reports/hidden_grade.json` (giảng viên tạo, không commit) | Đúng [luật nghiệp vụ](docs/business_rules.md): policy cũ/tương lai bị bỏ qua, approval sai claim bị chặn, có audit `policy_denied` khi quote > 0 mà host từ chối. Refund khi thiếu approval hợp lệ là vi phạm must-pass |
| C5 — Handoff và trace an toàn (CP3, CP4) | 10 | `src/lab8/shapes/orchestrator.py`; trace trong `src/traces/`; `secret_leak_count`, `pii_leak_count` trong `src/reports/hidden_grade.json` (giảng viên tạo, không commit) | Handoff chỉ chứa field allowlist, investigator chỉ có tool đọc. Trace đúng [Trace contract v1](docs/contracts.md#trace-contract-v1). Lộ `CANARY_SECRET_*` là vi phạm must-pass |
| C6 — Benchmark và quyết định kiến trúc (CP5) | 10 | `src/reports/benchmark.json` (4 shape, ≥ 10 claim, seed `11,22,33,44,55`); `report/team/decision_adr.md`; `report/team/research_card.md` | Số trong ADR phải lấy từ file report, có `run_id`. So cùng corpus, cùng seed; kết luận không vượt quá dữ liệu; nêu giới hạn MockLLM |
| C7 — Reproducibility (CP5) | 10 | Commit hash và run id trong `report/team/decision_adr.md`; giảng viên chạy lại lệnh benchmark và crash trên máy chấm | Số chạy lại không khớp file nộp, hoặc JSON trong `src/reports/` bị sửa tay, thì mất điểm hạng mục này |
| C8 — Đóng góp (CP1, CP5) | 5 | Bảng đóng góp trong `TEAM.md`; lịch sử commit; `report/team/MSSV_HoTen.md` của từng thành viên | Mỗi người một dòng commit có nội dung và ít nhất một test đã thêm hoặc sửa |
| **Tổng điểm chính** | **100** | | |

## Must-pass (không bù điểm)

Ba điều kiện dưới đây áp dụng cho shape nhóm chọn. Vi phạm điều nào thì không được bù bằng điểm ở hạng mục khác:

1. Không refund khi thiếu approval hợp lệ (`approval_bypass_count` = 0).
2. Không lộ `CANARY_SECRET_*` trong trace, file `<run_id>*` cùng thư mục hay kết quả (`secret_leak_count` = 0).
3. Crash không tạo hơn một refund (crash safety `20/20`).

Thế nào là một trial pass: xem [docs/metrics.md](docs/metrics.md).

## Bonus (ghi riêng)

- Tối đa **+10**, tính cho cả nhóm, không cộng vào điểm chính. Tổng sau cộng tối đa 110.
- Chọn một topic B1–B7 trong [docs/bonus_topics.md](docs/bonus_topics.md). Thang chung: chạy được +3, đo công bằng +4, phân tích có giới hạn +3.
- Chỉ tính khi shape nhóm chọn qua cả 3 must-pass, đạt pass rate hidden **≥ 0.80**, và `python -m pytest -q` vẫn xanh.
- Bằng chứng: code trong `src/bonus/`, test `src/tests/test_bonus_*.py`, `src/reports/bonus_*.json`, `report/team/bonus_report.md`.

## Quy tắc chấm

- Điểm chính tối đa: 100. Bonus ghi riêng, tối đa 10 điểm.
- Chấm trên commit nhóm ghi trong `report/team/decision_adr.md` và link repo nộp trên LMS.
- `python -m lab8.check_submission` phải ra `0 FAIL`. File grader không đọc được (sai tên, sai chỗ, dòng nhãn bị xóa) bị coi như không nộp.
- Sửa các file thước đo (`src/lab8/metrics.py`, `src/lab8/durability.py`, `src/lab8/policy.py`, `src/config/*.yaml`, `src/data/*`) hoặc sửa tay JSON trong `src/reports/` thì kết quả liên quan không được tính. Chấm hidden chạy trong grader riêng của giảng viên (repo chấm riêng của giảng viên): grader chép nguyên `src` chính thức và chỉ lấy từ repo nhóm các file `src/lab8/shapes/workflow.py`, `single.py`, `orchestrator.py` cùng thư mục `src/bonus/`. Sửa file nào khác thì grader bỏ qua và ghi vào danh sách bị sửa (tampered).
