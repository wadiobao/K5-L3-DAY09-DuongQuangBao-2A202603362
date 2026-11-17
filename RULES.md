# Rules

## AI và công cụ

- **Code của lab không gọi model thật.** Mọi lời gọi model trong shape đi qua MockLLM (`src/lab8/mock_llm.py`), cố định theo seed, để mọi nhóm so cùng điều kiện. Không cần và không dùng API key.
- Được dùng trợ lý AI (ChatGPT, Claude, Gemini, Copilot, Cursor…) để giải thích khái niệm, gợi ý code, viết test và đọc trace.
- Nhóm phải tự giải thích được: vì sao chọn shape trong ADR, ranh giới code / model trong shape của mình, vì sao truyền quote đầy đủ vào `durability.issue_refund`, và trace của nhóm cố ý không ghi field nào. Người chấm có thể hỏi trực tiếp các phần này.
- Mỗi thành viên ghi công cụ AI đã dùng và cách tự kiểm tra kết quả trong báo cáo cá nhân `report/team/MSSV_HoTen.md`.
- Không dùng AI để bịa số liệu benchmark, run id, commit hay phần tự đánh giá.

## Làm bài và liêm chính

- Không sao chép bài hoặc nhận bài làm thay.
- Ghi nguồn khi dùng code, dữ liệu hoặc tài liệu bên ngoài.
- Bài nhóm phải ghi rõ đóng góp của từng thành viên trong `TEAM.md` (bảng đóng góp: mỗi người một dòng commit có nội dung và ít nhất một test).
- **Không sửa thước đo:** `src/lab8/metrics.py`, `src/lab8/durability.py`, `src/lab8/policy.py`, `src/config/*.yaml`, `src/data/*`.
- **Không sửa tay** file JSON trong `src/reports/`. Giảng viên chạy lại đúng lệnh trên máy chấm.
- Workflow không được copy khối `REFERENCE_WEAKNESS` của `src/lab8/shapes/swarm_reference.py`.
- Chữ trong ticket là dữ liệu người dùng, không phải lệnh, kể cả câu như "ignore policy".

## Secret và API key

- Lab chạy offline, không cần API key. Không commit API key, password hoặc file `.env`.
- Dữ liệu là dữ liệu giả nhưng vẫn được coi như dữ liệu thật: không ghi `parent_secret`, header, SĐT, địa chỉ, ghi chú nội bộ, tên hàng vào trace, log hay stdout (xem [docs/contracts.md](docs/contracts.md#trace-contract-v1)).
- Không commit `src/eval/instructor/`, `student_drop/`, `traces/` hay file `*.sqlite` (đã có trong `.gitignore`).

## Nộp muộn và lỗi kỹ thuật

- Deadline và gia hạn: xem [SUBMISSION.md](SUBMISSION.md#deadline-gmt7).
- Nếu gặp lỗi kỹ thuật (cài đặt, lỗi riêng của Windows, CI), mô tả lỗi và đưa bằng chứng (lệnh đã chạy, output, ảnh chụp) vào mục 5 "Khó khăn và cách xử lý" của `report/team/group_report.md`. Cách xử lý lỗi hay gặp: [docs/troubleshooting.md](docs/troubleshooting.md).
- Không force-push, xóa commit hoặc sửa ngày commit. Bổ sung sau deadline dùng commit mới và ghi rõ thay đổi.
