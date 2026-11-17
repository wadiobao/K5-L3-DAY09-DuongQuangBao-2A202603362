# Báo cáo cá nhân — Dương Quang Bảo

- Họ tên: **Dương Quang Bảo**
- MSSV: **2A202503362**
- Hình thức thực hiện: Cá nhân
- Repository: https://github.com/wadiobao/K5-L3-DAY09-DuongQuangBao-2A202603362

## 1. Phần việc thực hiện

Tôi thực hiện bài tập theo hướng tự triển khai, tích hợp và kiểm tra các nội dung Lab 8/Lab 9 trong repository. Các phần việc có bằng chứng trong repository gồm:

- Làm việc với evaluation set và baseline cho Lab 9.
- Theo dõi metric specification và các chỉ số đánh giá.
- Hoàn thiện failure taxonomy, eval card và judge audit.
- Thiết lập và kiểm tra workflow Eval Gate, cross-platform CI và baseline refresh.
- Tổng hợp kết quả và ghi nhận giới hạn trong báo cáo nhóm, research card và decision record.

## 2. Kết quả đánh giá đã xác nhận

Baseline v2: `E-swarm-20261117-f8df`.

- Eval set: 28 items × 5 seeds = 140 trials.
- Pass rate: 97.86%.
- Pass_hat_5: 89.29%.
- Approval bypass: 0/140.
- Secret leak: 0/140.
- Reply matches ledger: 140/140.
- Cost per success: 50.8077 đơn vị cost mô phỏng.

Các workflow CI đã xác nhận thành công:

- [Lab 9 Eval Gate](https://github.com/wadiobao/K5-L3-DAY09-DuongQuangBao-2A202603362/actions/runs/44128099288).
- [Cross-platform CI](https://github.com/wadiobao/K5-L3-DAY09-DuongQuangBao-2A202603362/actions/runs/44126846537).
- [Baseline refresh](https://github.com/wadiobao/K5-L3-DAY09-DuongQuangBao-2A202603362/actions/runs/44127091991).

## 3. Khó khăn và cách xử lý

Một lần chạy Eval Gate bị chặn do SHA của eval set không khớp với baseline. Tôi kiểm tra lại lịch sử thay đổi và provenance của eval set, sau đó chạy lại baseline trên cùng eval set và xác nhận Eval Gate thành công.

Trong quá trình đánh giá LLM judge, tiêu chí `helpful` có recall thấp nên không được giữ làm gate. Các tiêu chí nghiệp vụ quan trọng tiếp tục được đánh giá bằng code.

## 4. Hạn chế còn lại

- Ba shape `workflow`, `single` và `orchestrator` vẫn cần hoàn thiện implementation.
- Chưa có benchmark report so sánh đầy đủ bốn shape.
- Chưa có artifact crash suite để xác nhận crash safety 20/20.
- MockLLM và eval set mô phỏng chưa đại diện cho môi trường production.

## 5. Tự đánh giá

Tôi đã hoàn thành phần công việc có bằng chứng trong repository về Lab 9 evaluation, baseline và CI. Các nội dung còn thiếu được ghi rõ thay vì sử dụng số liệu chưa được xác minh. Phần triển khai ba shape còn lại, benchmark và crash suite cần tiếp tục hoàn thiện trước khi có thể xem toàn bộ Lab 8 là hoàn tất.
