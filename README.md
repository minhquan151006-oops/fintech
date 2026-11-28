# Quản lý thu chi dành cho sinh viên

Ứng dụng **Streamlit** giúp sinh viên theo dõi thu nhập, quản lý chi tiêu theo từng danh mục, nhận cảnh báo khi vượt hạn mức và lập kế hoạch tiết kiệm đơn giản.

## Tính năng

- Nhập thu nhập hàng tháng và thiết lập hạn mức cho từng danh mục.
- Thêm, sửa hoặc xóa các khoản chi tiêu.
- Xem tổng thu nhập, tổng chi, số tiền còn lại và tỷ lệ có thể tiết kiệm.
- Nhận cảnh báo khi chi tiêu theo danh mục hoặc tổng chi vượt ngân sách.
- Nhận gợi ý điều chỉnh hạn mức và mức chi tiêu.
- Tính số tiền cần tiết kiệm theo tháng để đạt mục tiêu tài chính.

## Yêu cầu

- Python 3.9 trở lên
- Streamlit
- Pandas

## Cài đặt

```bash
python -m pip install streamlit pandas
```

## Chạy ứng dụng

Từ thư mục chứa `app.py`, chạy:

```bash
streamlit run app.py
```

Sau đó m��� địa chỉ Streamlit được hiển thị trong terminal, thường là `http://localhost:8501`.

## Cách sử dụng

1. Nhập thu nhập hàng tháng ở thanh bên.
2. Thiết lập hạn mức chi cho từng danh mục.
3. Thêm khoản chi tiêu gồm danh mục, số tiền và ghi chú.
4. Xem bảng tổng quan, cảnh báo và gợi ý điều chỉnh.
5. Nhập mục tiêu tài chính và thời gian mong muốn để nhận kế hoạch tiết kiệm hàng tháng.

Dữ liệu được lưu trong phiên Streamlit hiện tại; tải lại trang sẽ xóa dữ liệu chưa lưu.

> Công cụ chỉ mang tính hỗ trợ lập kế hoạch cá nhân và không thay thế tư vấn tài chính chuyên nghiệp.
