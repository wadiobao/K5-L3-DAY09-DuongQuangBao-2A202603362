# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Đạt (ma trận tp24 fp4 fn6 tn66) | dùng |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không đạt: κ < 0.6 và R < 0.7 (ma trận tp9 fp0 fn21 tn70) | loại |

## ≥5 case audit thủ công

Quy ước: nhãn người chấm theo guideline CS của LogiX được coi là chuẩn, trừ khi ghi chú trong CSV chỉ ra nhãn người sai (ca 8). Cột "Ai đúng?" là người hay judge.

### tone_ok: toàn bộ 10 ca bất đồng (`--audit 10`)
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / sửa rubric |
|---|---|---|---|---|---|
| 1 | H-008 "Em đã hoàn tiền cho anh rồi nha, anh check giúp em." | PASS | FAIL | Người | Xưng "em" và "nha" quá suồng sã. Rubric thêm: xưng hô chuẩn là "LogiX" và "anh/chị", không dùng "em/bạn/nha". |
| 2 | H-017 "Dạ, bạn ơi LogiX đã hoàn 25.000đ cho đơn O-606 rồi nha." | PASS | FAIL | Người | Gọi khách là "bạn" với khách lớn tuổi. Cùng sửa rubric như ca 1, thêm ví dụ FAIL có "bạn ơi". |
| 3 | H-029 "Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm." | PASS | FAIL | Người | Judge chỉ thấy "Dạ, vui lòng" nên bỏ qua câu mệnh lệnh. Rubric thêm: cấm câu ra lệnh hoặc ngăn khách liên hệ; chấm cả câu, không chỉ cụm mở đầu. |
| 4 | H-042 "Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ." | FAIL | PASS | Người | Ngắn nhưng đủ ý. Judge phạt vì "thiếu xin lỗi". Rubric sửa: chỉ yêu cầu xin lỗi khi khách phàn nàn hoặc lỗi thuộc LogiX. |
| 5 | H-051 "Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ." | FAIL | PASS | Người | CS LogiX cho phép từ "refund". Rubric thêm danh sách thuật ngữ được phép để không phạt tiếng Anh. |
| 6 | H-063 "Dạ, LogiX đã hoàn 20.000đ và sẽ hoàn thêm cho anh/chị ạ." | PASS | FAIL | Người | Hứa "sẽ hoàn thêm" ngoài kết quả hệ thống. Rubric thêm: không cam kết điều không có trong dữ liệu hệ thống. Đây cũng là rủi ro nghiệp vụ, nên bắt thêm bằng code (số tiền hoàn phải khớp ledger). |
| 7 | H-070 "Dạ, LogiX đã hoàn 90.000đ cho đơn O-909 ạ 😂😂" | PASS | FAIL | Người | Emoji cười không phù hợp ngữ cảnh khiếu nại. Rubric thêm: cấm emoji trong phản hồi khiếu nại và bồi thường. |
| 8 | H-081 "Dạ, đơn O-107 chưa đủ điều kiện hoàn theo chính sách hiện hành ạ." | FAIL | PASS | **Judge** | CSV ghi nhãn người sai (đọc nhầm ticket). Hành động: sửa nhãn người thành FAIL; đây là lỗi nhãn chứ không phải lỗi judge. |
| 9 | H-088 "Dạ, dạ, LogiX đã hoàn 40.000đ cho đơn O-233 ạ." | FAIL | PASS | Người (có lý do) | Lặp "Dạ" do lỗi gõ; người cho qua, judge phạt. Rubric thêm: lỗi gõ nhẹ không ảnh hưởng nội dung thì không phạt; chuẩn hoá lặp từ trước khi chấm. |
| 10 | H-094 "Da, LogiX da hoan 40.000đ cho don O-341, xin loi vi su bat tien." | PASS | FAIL | Người | Tiếng Việt mất dấu (dịch máy) nhưng có "xin lỗi" nên judge cho qua. Rubric thêm: phản hồi không dấu là FAIL dù nội dung lịch sự. |

### helpful: toàn bộ 21 ca bị bỏ sót (`--audit 21`)
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / sửa rubric |
|---|---|---|---|---|---|
| 11 | HL-015: báo hoàn 55.000đ cho O-112 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 55.000đ, ledger 40.000đ; reply ngắn nhưng judge vẫn không biết ledger. |
| 12 | HL-016: báo hoàn 55.000đ cho O-404 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 55.000đ, ledger 35.000đ; reply dài 236 ký tự, có lời xin lỗi/đồng cảm dài. |
| 13 | HL-020: báo hoàn 90.000đ cho O-303 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 90.000đ, ledger 120.000đ; reply ngắn nhưng judge vẫn không biết ledger. |
| 14 | HL-028: báo hoàn 50.000đ cho O-677 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 50.000đ, ledger 35.000đ; reply dài 232 ký tự, có lời xin lỗi/đồng cảm dài. |
| 15 | HL-035: báo hoàn 50.000đ cho O-303 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 50.000đ, ledger 35.000đ; reply dài 236 ký tự, có lời xin lỗi/đồng cảm dài. |
| 16 | HL-041: báo hoàn 60.000đ cho O-909 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 60.000đ, ledger 40.000đ; reply dài 236 ký tự, có lời xin lỗi/đồng cảm dài. |
| 17 | HL-043: báo hoàn 35.000đ cho O-202 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 35.000đ, ledger 20.000đ; reply dài 194 ký tự, có lời xin lỗi/đồng cảm dài. |
| 18 | HL-047: "Ok bạn, đơn O-515 xử lý rồi nhé." | PASS | FAIL (sai xưng hô) | Người | Sai xưng hô: "bạn", "nhé" quá suồng sã với khách; judge coi là ngắn gọn thân thiện. |
| 19 | HL-053: báo hoàn 110.000đ cho O-562 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 110.000đ, ledger 90.000đ; reply dài 218 ký tự, có lời xin lỗi/đồng cảm dài. |
| 20 | HL-058: báo hoàn 40.000đ cho O-107 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 40.000đ, ledger 25.000đ; reply dài 217 ký tự, có lời xin lỗi/đồng cảm dài. |
| 21 | HL-062: báo hoàn 55.000đ cho O-458 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 55.000đ, ledger 40.000đ; reply ngắn nhưng judge vẫn không biết ledger. |
| 22 | HL-070: báo hoàn 50.000đ cho O-781 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 50.000đ, ledger 30.000đ; reply dài 240 ký tự, có lời xin lỗi/đồng cảm dài. |
| 23 | HL-072: báo hoàn 50.000đ cho O-781 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 50.000đ, ledger 30.000đ; reply dài 232 ký tự, có lời xin lỗi/đồng cảm dài. |
| 24 | HL-074: báo hoàn 140.000đ cho O-458 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 140.000đ, ledger 120.000đ; reply dài 241 ký tự, có lời xin lỗi/đồng cảm dài. |
| 25 | HL-087: báo hoàn 60.000đ cho O-202 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 60.000đ, ledger 90.000đ; reply ngắn nhưng judge vẫn không biết ledger. |
| 26 | HL-090: báo hoàn 155.000đ cho O-233 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 155.000đ, ledger 120.000đ; reply dài 218 ký tự, có lời xin lỗi/đồng cảm dài. |
| 27 | HL-091: "Ok bạn, đơn O-233 xử lý rồi nhé." | PASS | FAIL (sai xưng hô) | Người | Sai xưng hô: "bạn", "nhé" quá suồng sã với khách; judge coi là ngắn gọn thân thiện. |
| 28 | HL-096: báo hoàn 50.000đ cho O-341 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 50.000đ, ledger 35.000đ; reply dài 232 ký tự, có lời xin lỗi/đồng cảm dài. |
| 29 | HL-097: "Ok bạn, đơn O-202 xử lý rồi nhé." | PASS | FAIL (sai xưng hô) | Người | Sai xưng hô: "bạn", "nhé" quá suồng sã với khách; judge coi là ngắn gọn thân thiện. |
| 30 | HL-098: báo hoàn 120.000đ cho O-808 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 120.000đ, ledger 90.000đ; reply dài 233 ký tự, có lời xin lỗi/đồng cảm dài. |
| 31 | HL-100: báo hoàn 55.000đ cho O-112 | PASS | FAIL (sai tiền) | Người | Sai tiền: reply 55.000đ, ledger 35.000đ; reply ngắn nhưng judge vẫn không biết ledger. |

Sửa rubric cho helpful không cứu được nhóm "sai tiền" (18 ca): judge không nhìn thấy ledger, nên rubric nào cũng không thể phát hiện. Hành động đúng là chuyển kiểm tra số tiền sang grader bằng code (xem kết luận). Nhóm "sai xưng hô" (3 ca) cùng loại lỗi với tone_ok nên để tone_ok xử lý.

## Kết luận
- **Loại `helpful` khỏi gate.** Recall chỉ 0.30 (ngưỡng 0.70) và κ = 0.375 (ngưỡng 0.60): judge bỏ sót 21 trong 30 reply mà người chấm FAIL. Precision 1.0 không có ý nghĩa vì judge chỉ gắn FAIL cho 9 ca. Phân tích 21 ca bị bỏ sót:
  - 18/21 là "sai tiền" (ledger khác số trong reply), 3/21 là "sai xưng hô". Judge không thấy ledger nên điểm mù này mang tính cấu trúc, không sửa được bằng prompt.
  - 13/21 là reply dài trên 150 ký tự (trung bình 156 ký tự, so với 31 ký tự ở nhóm judge bắt được), nhiều ca lặp lời xin lỗi. Judge thiên vị câu dài và lịch sự.
  - Sau hiệu chỉnh Rogan-Gladen, tỉ lệ lỗi thực là 0.30 trong khi judge chỉ thấy 0.09, tức thấp hơn khoảng 3 lần. Dùng làm gate thì regression về tiền sẽ lọt qua.
- **Hành động:** số tiền trong reply phải chấm bằng code (so reply với `snapshot.refund_vnd`), đó là metric FM-08 ở M3. Tiền và approval không bao giờ giao cho judge.
- **`tone_ok` dùng được** (qua cả ba ngưỡng) nhưng còn 10 ca bất đồng trên 100:
  - 6 ca bỏ sót (H-008, H-017, H-029, H-063, H-070, H-094): xưng hô suồng sã, câu ra lệnh, hứa ngoài hệ thống, emoji, không dấu.
  - 4 ca báo nhầm (H-042, H-051, H-081, H-088): trong đó H-081 là nhãn người sai. Nếu sửa nhãn này, ma trận thành tp25 fp3 fn6 tn66 (P ≈ 0.893, R ≈ 0.806, κ ≈ 0.784), tức tốt hơn một chút.
  - Áp dụng các sửa rubric ở ca 1–10 rồi hiệu chuẩn lại trên nhãn mới.
- **Rủi ro còn lại:** judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có held-out thật. Số liệu chính thức trong bảng đầu giữ nguyên theo CSV gốc (chưa sửa nhãn H-081), vì test của lab kiểm tra đúng các giá trị này.