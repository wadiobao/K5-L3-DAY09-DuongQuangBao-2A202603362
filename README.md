# Lab 8 — From Workflows to Agents (LogiX-VN: một task, bốn kiến trúc)

AI20K K5, ngày 8. Nhóm xử lý claim hoàn phí vận chuyển của công ty giả lập LogiX-VN bằng **bốn kiến trúc** (workflow, single agent, orchestrator, swarm), rồi dựa trên số đo để chọn kiến trúc **ít tự chủ nhất mà vẫn làm được việc**. Dữ liệu là dữ liệu giả. Không cần GPU, API key hay internet trong giờ lab; chạy được trên Windows, macOS và Linux.

**Loại bài:** Nhóm · **Thời lượng:** 4 giờ tại lớp (13:30–17:30) · **Deadline:** lớp sáng 23h59 GMT+7 ngày lab; lớp chiều/tối 11h59 GMT+7 ngày hôm sau ([SUBMISSION.md](SUBMISSION.md#deadline-gmt7))

## Mục tiêu học tập

- Cài cùng một quy trình xử lý claim theo bốn kiến trúc, cùng chữ ký `run_claim`, và hiểu ranh giới: số tiền, approval, chống ghi trùng do **code** quyết; model chỉ đọc và soạn chữ.
- Làm cho thao tác ghi tiền an toàn khi chạy lại và khi crash: một claim chỉ có một refund.
- Giữ ranh giới bảo mật giữa các agent: chỉ chuyển cho agent khác những field được cho phép, trace không lộ secret hay thông tin cá nhân, chữ trong ticket là dữ liệu chứ không phải lệnh.
- So sánh các kiến trúc trên cùng claim, cùng seed, cùng bảng giá, rồi viết quyết định kiến trúc bằng số liệu thay vì mặc định "multi-agent tốt hơn".

## Thuật ngữ dùng trong lab

| Từ | Nghĩa trong lab này |
| --- | --- |
| Shape | Một kiến trúc xử lý claim: A `workflow`, B `single`, C `orchestrator`, D `swarm` |
| Host | Phần code có sẵn đứng giữa shape và database: kiểm policy, approval, trần hoàn tiền, rồi mới ghi ledger. Shape không ghi thẳng vào database |
| Cổng host | Lệnh `python -m pytest -q`: test của phần host. Phải luôn xanh |
| Ledger | Bảng SQLite ghi các lần hoàn tiền. Mỗi claim tối đa một dòng |
| Idempotency | Gọi lại cùng claim bao nhiêu lần cũng chỉ ra một refund. Khóa là `refund:{claim_id}` |
| Audit `refund_committed` | Dòng nhật ký host ghi khi một refund đã được ghi thật |
| ReAct | Vòng lặp model: suy nghĩ → chọn tool → đọc kết quả → lặp lại |
| Handoff | Gói dữ kiện orchestrator chuyển cho investigator. Chỉ chứa field trong allowlist (danh sách field được phép) |
| Trace | File JSON ghi lại từng bước của một lần chạy. Grader đọc file này, nên không được chứa secret hay thông tin cá nhân |
| Seed | Số khởi tạo cho MockLLM. Cùng seed thì cùng kết quả, đổi seed để đo độ dao động |
| Pass rate, pass^5, variance, cost/success | Tỉ lệ trial pass, tỉ lệ claim pass cả 5 seed, độ dao động giữa các seed, chi phí cho mỗi lần thành công. Công thức: [docs/metrics.md](docs/metrics.md) |

## Việc nhóm làm

Repo này là starter. Các phần đã chạy được ngay: swarm tham chiếu, world, MockLLM, host. Ba shape còn lại do nhóm viết.

| Shape | Việc của nhóm | Ai tính tiền và gọi ghi refund |
| --- | --- | --- |
| A `workflow` | Viết các bước Python cố định | Code của shape tính bằng `compute_compensation` rồi gọi `durability.issue_refund` |
| B `single` | Viết vòng ReAct, tối đa 8 bước | Model chỉ được chọn tool đọc. Sau vòng lặp, code của shape gọi `durability.issue_refund` |
| C `orchestrator` | Viết orchestrator và investigator | Investigator chỉ có tool đọc. Orchestrator gọi `durability.issue_refund` |
| D `swarm` | Có sẵn. Dùng để đối chứng cost và variance | Swarm gọi `durability.issue_refund` |

Ở cả bốn shape, `durability.issue_refund` là cửa của host: host kiểm approval, trần theo đơn và idempotency rồi mới ghi ledger. Shape truyền **quote đầy đủ**, không tự trừ phần đã hoàn trước đó.

Code viết vào `src/lab8/shapes/workflow.py`, `single.py`, `orchestrator.py`. Đầu mỗi file có hướng dẫn từng bước, chỗ cần sửa có dòng `TODO CP2` và `TODO CP3`. Giữ nguyên chữ ký hàm:

```python
run_claim(claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None) -> RunResult
```

## Thế nào là qua bài

- **Ba điều kiện must-pass** cho shape nhóm chọn, vi phạm thì không bù được bằng điểm khác: không refund khi thiếu approval hợp lệ; không lộ `CANARY_SECRET_*` trong trace hay kết quả; crash không tạo hơn một refund (crash suite `20/20`).
- **Bộ hidden:** shape nhóm chọn phải đạt pass rate ≥ 0.75 trên 40 claim × 5 seed.
- `python -m pytest -q` vẫn xanh khi nộp; không sửa các file thước đo (`metrics.py`, `grade_hidden.py`, `durability.py`, `policy.py`, `config/`, `data/`).

Thang 100 điểm và bonus: [RUBRIC.md](RUBRIC.md).

## Bắt đầu

**Bước 0 — tạo repo nhóm.** Nhóm trưởng fork repo này rồi đổi tên theo mẫu `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents`. Không fork được thì làm theo [SUBMISSION.md](SUBMISSION.md#tạo-repo-nhóm). Các thành viên clone **repo nhóm**, không làm trên repo đề bài.

**Bước 1 — cài và chạy thử.** Cần Python 3.11–3.13. **Mọi lệnh chạy trong thư mục `src/`.**

macOS / Linux:

```bash
cd src
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m lab8.smoke
python -m pytest -q
```

Windows PowerShell:

```powershell
cd src
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m lab8.smoke
python -m pytest -q
```

PowerShell báo `running scripts is disabled`, hoặc bạn dùng cmd / Git Bash: xem [src/README.md](src/README.md#cài-đặt-theo-hệ-điều-hành).

Smoke đúng in ra `lab8.smoke pass`. `python -m pytest -q` (cổng host) phải xanh trước khi chia việc và giữ xanh suốt buổi. Bộ test student (`-m student`) lúc đầu **đỏ là bình thường** vì ba shape còn là stub; số đỏ/xanh mong đợi ghi ở [CHECKPOINTS.md](CHECKPOINTS.md).

## Đọc gì, khi nào

15 phút đầu (CP1):

1. [CHECKPOINTS.md](CHECKPOINTS.md): 5 checkpoint theo lịch buổi lab và cách tự kiểm tra.
2. [docs/business_rules.md](docs/business_rules.md) và [docs/contracts.md](docs/contracts.md): luật nghiệp vụ, `RunResult` và trace mà grader chấm.

Khi cần:

- [src/README.md](src/README.md): cài đặt chi tiết, bảng lệnh, file được sửa, tự kiểm trên bộ hidden ở CP5.
- [RULES.md](RULES.md): dùng AI, liêm chính, file không được sửa, nộp muộn.
- [RUBRIC.md](RUBRIC.md): 100 điểm chính, must-pass, bonus ghi riêng.
- [SUBMISSION.md](SUBMISSION.md): tên repo, deliverable, deadline, checklist. Đọc trước khi nộp.
- [docs/README.md](docs/README.md): kiến trúc, metric, bonus, xử lý sự cố.

## Cấu trúc repo

| Đường dẫn | Nội dung |
| --- | --- |
| `README.md`, `RULES.md`, `CHECKPOINTS.md`, `RUBRIC.md`, `SUBMISSION.md` | Đề bài, luật, checkpoint, cách chấm, cách nộp |
| `TEAM.md` | Thông tin nhóm, thành viên và **bảng đóng góp** (`check_submission` đọc bảng này) |
| `src/` | Code (`lab8/`), config, dữ liệu public, test, bằng chứng sinh ra (`src/reports/`) |
| `docs/` | Luật nghiệp vụ, contract, kiến trúc, metric, bonus, xử lý sự cố, ghi chú giảng viên |
| `report/team/` | Báo cáo nhóm, ADR, research card, báo cáo từng thành viên |
| `.github/workflows/ci.yml` | CI chạy smoke, pytest, crash suite và benchmark swarm trên 3 hệ điều hành |

## Báo cáo phải nộp

- `report/team/group_report.md`: báo cáo nhóm.
- `report/team/decision_adr.md` và `report/team/research_card.md`: hai file được `check_submission` đọc bằng máy; giữ nguyên tên và các dòng nhãn.
- Mỗi thành viên **copy** `report/team/MSSV_HoTen.md` thành file riêng đặt tên theo MSSV và họ tên không dấu, ví dụ `report/team/20241234_NguyenVanAn.md`. Giữ nguyên file mẫu để người khác còn copy.
- `TEAM.md`: điền thông tin nhóm và bảng đóng góp.

Chi tiết: [SUBMISSION.md](SUBMISSION.md).
