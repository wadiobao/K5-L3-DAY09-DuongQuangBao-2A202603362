# Checkpoints

Năm checkpoint bám theo lịch buổi lab 13:30–17:30 (nghỉ 15:15–15:30). Giờ ghi kèm là mốc tại lớp, không phải deadline nộp bài. Lớp học buổi sáng đi cùng thứ tự và thời lượng từng checkpoint; giờ cụ thể theo coach thông báo. Mọi lệnh chạy trong thư mục `src/`.

## CP1 — Cài đặt, đọc contract, chia vai (13:30, M0)

- **Mục tiêu:** cả nhóm chạy được starter trên máy mình và hiểu grader chấm cái gì trước khi viết dòng code nào.
- **Cần làm:** cài môi trường theo [src/README.md](src/README.md#cài-đặt-theo-hệ-điều-hành); đọc [docs/business_rules.md](docs/business_rules.md), [docs/contracts.md](docs/contracts.md) và `src/lab8/shapes/swarm_reference.py`; chia vai và điền phần thành viên trong `TEAM.md`.
- **Sản phẩm:** mỗi máy chạy smoke pass; `TEAM.md` có tên nhóm, thành viên, vai.
- **Cần hiểu:** vì sao tiền do `compute_compensation` tính chứ không do MockLLM; vì sao chữ trong ticket là dữ liệu người dùng; `RunResult` có những `status` nào.
- **Tự kiểm tra:** `python -m lab8.smoke` in `lab8.smoke pass`; `python -m pytest -q` không có dòng `failed`; `python -m pytest -q -m student -o addopts=` ra **186 failed, 62 passed** (62 test swarm xanh, 3 shape stub đỏ).

## CP2 — Ba shape: workflow, single, orchestrator (13:45, M1)

- **Mục tiêu:** cùng một claims flow chạy được trên ba shape nhóm viết, cùng chữ ký `run_claim` với swarm.
- **Cần làm:** thay stub ở các dòng `TODO CP2` trong `src/lab8/shapes/workflow.py`, `single.py`, `orchestrator.py` theo hướng dẫn ở docstring đầu mỗi file. Trả kết quả bằng `lab8.shapes.common.finish()`. Ghi trace đúng contract ở mọi nhánh return, kể cả `needs_info` và `escalated`.
- **Sản phẩm:** ba shape không còn trả `not_implemented`; mỗi shape qua 62 test student của nó.
- **Cần hiểu:** khác nhau về mức tự chủ giữa A, B, C, D; vì sao phải truyền **quote đầy đủ** vào `durability.issue_refund` (T13, T14); vì sao shape tự từ chối thì không có audit `policy_denied`.
- **Tự kiểm tra:** `python -m pytest -q -m student -o addopts= -k workflow` (thay `workflow` bằng `single`, `orchestrator`) ra 62 passed cho shape đó.

## CP3 — Handoff, ledger, crash (14:30, M2)

- **Mục tiêu:** ghi tiền an toàn khi gọi lại và khi crash; handoff không mang secret qua ranh giới.
- **Cần làm:** ở dòng `TODO CP3` trong ba shape, truyền `crash_at` vào `durability.issue_refund` và không bắt `InjectedCrash`. Orchestrator dựng handoff bằng `lab8.handoff.make_handoff` với tool chỉ đọc; trace ghi handoff đã sanitize, không ghi parent context.
- **Sản phẩm:** T11 (gọi lại cùng claim) và T12 (crash rồi resume) xanh trên cả ba shape; cổng host vẫn xanh.
- **Cần hiểu:** vì sao checkpoint đơn lẻ không thay được ledger (chạy `python -m lab8.demo.buggy_workflow`); idempotency key `refund:{claim_id}`; vì sao tóm tắt bằng LLM không tính là redaction.
- **Tự kiểm tra:** `python -m pytest -q` vẫn xanh; `python -m pytest -q -m student -o addopts=` không còn fail T11, T12 ở shape nhóm viết.

## CP4 — 20 điểm crash, approval, secret (15:30, M3)

- **Mục tiêu:** qua ba điều kiện must-pass: không refund khi thiếu approval hợp lệ, không lộ `CANARY_SECRET_*`, crash không tạo hơn một refund.
- **Cần làm:** chạy crash suite; rà các nhánh approval hỏng, approval của claim khác, đơn đã hoàn đủ; rà trace và stdout để chắc không ghi claim row hay order row thô. Nhóm làm bonus tự đề xuất topic thì đăng ký với giảng viên **trước 15:30** (xem [docs/bonus_topics.md](docs/bonus_topics.md)).
- **Sản phẩm:** `src/reports/crash.json` do `lab8.crash_test` sinh ra.
- **Cần hiểu:** cổng duyệt của host chặn gì; vì sao trace là ranh giới bảo mật chứ không phải tiện ích debug; grader fail-closed với `missing_trace`, `stale_trace`, `invalid_trace`, `trace_run_id_mismatch`.
- **Tự kiểm tra:** `python -m lab8.crash_test --count 20 --out reports/crash.json` cho `crash_safety` = `20/20`.

## CP5 — Benchmark, hidden, quyết định kiến trúc (16:15, M4 → 17:00)

- **Mục tiêu:** chọn shape bằng số đo trên cùng claim, cùng seed, cùng bảng giá, và nộp được bài mà grader đọc được.
- **Cần làm:** chạy benchmark 4 shape × 5 seed trên bộ public; sau 16:15 tự kiểm trên `student_drop/` ([src/README.md](src/README.md#tự-kiểm-trên-bộ-hidden-cp5)); điền `report/team/decision_adr.md` (shape chọn, commit hash, run id, số liệu) và `report/team/research_card.md`; viết `report/team/group_report.md`, bảng đóng góp trong `TEAM.md` và báo cáo từng thành viên.
- **Sản phẩm:** `src/reports/benchmark.json` (4 shape, ≥ 10 claim, seed `11,22,33,44,55`), ADR và research card đã điền, báo cáo nhóm và cá nhân.
- **Cần hiểu:** pass rate, pass^5, seed variance, cost/success ([docs/metrics.md](docs/metrics.md)); vì sao swarm fail T02 ở seed 55; điều kiện nào làm quyết định kiến trúc đảo lại.
- **Tự kiểm tra:** `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json` chạy xong; `python -m lab8.check_submission` ra `0 FAIL`.
