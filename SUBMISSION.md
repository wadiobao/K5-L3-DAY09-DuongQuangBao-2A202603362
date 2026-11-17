# Submission

## Loại bài

**Nhóm.** Nhóm push bài lên GitHub; mỗi thành viên tự nộp cùng link repo nhóm trên LMS bằng tài khoản cá nhân. Ai không nộp link thì không có điểm, dù nhóm đã nộp.

## Tên repo và biến tên

- `Kn`: số khóa. Khóa này dùng `K5`.
- Level/lớp: `L3A`.

### Repo bài nộp nhóm

```text
K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents
```

`TenNhom` viết không dấu, không khoảng trắng. Repo phải public, hoặc đã mời giảng viên vào.

### Tạo repo nhóm

Nhóm trưởng Fork repo đề bài rồi đổi tên theo mẫu trên. Nếu không Fork được, clone repo đề bài, đổi `origin` sang repo nhóm rỗng và push `main`:

```bash
git clone https://github.com/VinUni-AI20k/K5-Day8-From-Workflows-to-Agents.git <TEN_REPO_NHOM>
cd <TEN_REPO_NHOM>
git remote rename origin upstream
git remote add origin <URL_REPO_NHOM>
git push -u origin main
```

## Cấu trúc và deliverable phải nộp (đặt tên và cấu trúc)

### Báo cáo và thông tin nhóm (ở gốc repo)

| File | Nội dung |
|---|---|
| `TEAM.md` | Thông tin nhóm, thành viên, phân công và **bảng đóng góp** (mỗi người một dòng) |
| `report/team/group_report.md` | Báo cáo nhóm, tối đa 5 trang ngoài phụ lục |
| `report/team/decision_adr.md` | Shape chọn, commit hash, run id, số liệu. Giữ nguyên các dòng nhãn |
| `report/team/research_card.md` | Phiếu nghiên cứu R1–R4 và kết quả ablation. Cột "Nhóm điền" không để trống |
| `report/team/MSSV_HoTen.md` | Mỗi thành viên một file, copy từ mẫu và đổi tên, ví dụ `report/team/20241234_NguyenVanAn.md` |
| `report/team/bonus_report.md` | Chỉ khi làm bonus. Tiêu đề `# Bonus report: B1` … `B6` |

### Code và bằng chứng (trong `src/`)

| Phần | File |
|---|---|
| Ba shape | `src/lab8/shapes/workflow.py`, `single.py`, `orchestrator.py` |
| Test nhóm thêm | `src/tests/` |
| Benchmark | `src/reports/benchmark.json` do `lab8.benchmark` tạo: đủ 4 shape, seed `11,22,33,44,55`, ≥ 10 claim |
| Crash suite | `src/reports/crash.json`: `crash_safety` = `20/20` |
| Tự kiểm hidden (tùy chọn) | `src/reports/hidden_selfcheck.json` |
| Bonus (nếu làm) | `src/bonus/`, `src/tests/test_bonus_*.py`, `src/reports/bonus_*.json` |

Không sửa tay file JSON trong `src/reports/`. Không commit `traces/`, `*.sqlite`, `student_drop/`, `src/eval/instructor/`, `.venv/` hay `.env`.

### Thứ tự nộp

Chạy trong `src/`:

1. `python -m pytest -q` xanh.
2. Chạy benchmark và crash test ([src/reports/README.md](src/reports/README.md)) để tạo `reports/benchmark.json`, `reports/crash.json`.
3. Commit, rồi chạy `git rev-parse --short HEAD`. Ghi hash và run id vào `report/team/decision_adr.md`, rồi commit tiếp.
4. `python -m lab8.check_submission` ra `0 FAIL`, rồi push.

## Deadline (GMT+7)

- Lab **sáng**: nộp trước **23h59 GMT+7** ngày lab.
- Lab **chiều** (lịch mẫu 13:30–17:30) hoặc **tối**: nộp trước **11h59 GMT+7** ngày hôm sau.
- Coach có thể gia hạn ≤ 48h nếu có lý do chính đáng; nếu gia hạn thì theo thông báo của coach.
- Các mốc giờ trong [CHECKPOINTS.md](CHECKPOINTS.md) là checkpoint tại lớp, không phải deadline.
- Sửa sau deadline phải tạo commit mới; xem [RULES.md](RULES.md).

## Checklist

- [ ] Đổi tên repo theo đúng quy ước `K5-L3A-DAY08-…`.
- [ ] Điền `TEAM.md` ở root: thông tin nhóm, thành viên, bảng đóng góp.
- [ ] Mỗi thành viên có file báo cáo đã đổi tên đúng định dạng `report/team/MSSV_HoTen.md`.
- [ ] `report/team/group_report.md`, `decision_adr.md`, `research_card.md` đã điền đủ.
- [ ] Mỗi thành viên có commit kỹ thuật và ít nhất một test trong lịch sử branch nộp bài.
- [ ] Trong `src/`: `python -m pytest -q` xanh; có `reports/benchmark.json` và `reports/crash.json` do công cụ sinh ra.
- [ ] Trong `src/`: `python -m lab8.check_submission` ra `0 FAIL`.
- [ ] Không commit secret, password, file `.env`, trace hay file `.sqlite`.
- [ ] Đã push lên GitHub; repo mở được cho người chấm.
- [ ] Mọi thành viên đã nộp cùng link repo trên LMS trước deadline.
