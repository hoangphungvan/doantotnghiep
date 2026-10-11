# Các vòng kiểm chứng mù (chỉ chỉ số tổng hợp)

## Vòng 1 (39 cặp, rubric v1.1) — nhãn người đã xóa theo yêu cầu
- Khớp chính xác với Claude: 41%; trong ±1 mức: 95%.
- Kappa có trọng số bình phương 0,64 [0,48-0,76]; tuyến tính 0,44; không trọng số 0,21.
- Nhị phân (từ mức 2 trở lên hay không): khớp 79,5%, kappa 0,59.
- Chiều lệch: Claude cao hơn người ở 17 cặp, thấp hơn ở 6 cặp. Chỉ một người chấm.

## Vòng 2 (cùng 39 cặp, chấm lại sau khi chốt "nhãn đo năng lực")
(Các tệp phiếu và nhãn người của hai vòng này đã bị xóa; chỉ còn số liệu tổng hợp.)
- Khớp chính xác: 53,8% (21/39); trong ±1 mức: 97,4%.
- Kappa có trọng số bình phương 0,76 [0,57-0,89]; tuyến tính 0,61; không trọng số 0,39.
- Nhị phân: khớp 84,6%, kappa 0,69. Spearman 0,82 (trung bình trong từng CV: 0,88).
- Chiều lệch: người cao hơn Claude ở 16 cặp, thấp hơn ở 2 cặp. Người cho mức 3 ở 17 cặp (vòng 1: 2 cặp).

**Không dùng vòng 2 làm bằng chứng kiểm chứng trong báo cáo.** Người chấm cho biết đã đọc lướt CV và JD, chủ yếu dựa vào số năm kinh nghiệm và lĩnh vực, và tiếng Anh hạn chế (một cặp đã xác nhận có thể chấm sai). Cùng 39 cặp này cũng đã bị thảo luận nên không còn "mù". Lần kiểm chứng chính thức sẽ dùng mẫu mới, chấm nghiêm túc, sau khi gán nhãn xong.

## Vòng 3 — kiểm chứng chính thức (mẫu mới, rubric v1.2, chấm nghiêm túc)
Mẫu 40 cặp: 36 cặp khác nhau (9 cặp mỗi mức điểm của Claude, mỗi CV một lần) và 4 cặp lặp ẩn. Các cặp lặp **không** dùng để tính chỉ số nào (4 cặp quá ít để kết luận về độ nhất quán). Phân tích trên 36 cặp, một người chấm.
- Khớp chính xác: 86,1% (31/36), khoảng tin cậy 95% 75-97%; trong ±1 mức: 100%; không có cặp nào lệch từ 2 mức trở lên.
- Kappa có trọng số bình phương 0,94 [0,87-0,99]; tuyến tính 0,88; không trọng số 0,81.
- Nhị phân (từ mức 2 trở lên hay không): khớp 97,2%, kappa 0,94. Spearman 0,95.
- 5 cặp lệch, tất cả lệch 1 mức: người cao hơn Claude ở 3 cặp, thấp hơn ở 2 cặp (lệch trung bình +0,03).
- Chưa có người chấm thứ hai nên chưa có độ đồng thuận giữa người với người. Mẫu cân bằng theo mức điểm nên kappa cao hơn so với mẫu tự nhiên (nhãn 1 chiếm khoảng 49%).
