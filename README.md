# Ứng dụng tính tiền quán trà sữa (Streamlit)

Ứng dụng Streamlit hỗ trợ chọn loại nước, size, topping, phần trăm đường/đá và số lượng; tự tính thành tiền, quản lý các món trong hóa đơn và tải hóa đơn HTML để in.

## Tính năng
- Menu minh họa có ảnh cho từng loại nước.
- Giá món theo size và giá topping được cấu hình trực tiếp trong `app.py`.
- Tùy chỉnh đường, đá (0–100%) và số lượng.
- Thêm nhiều món, xóa món hoặc làm mới hóa đơn.
- Tính tổng tiền bằng VND.
- Xuất hóa đơn HTML có định dạng phù hợp giấy in nhiệt khoảng 80 mm. Tải file, mở bằng trình duyệt rồi dùng `Ctrl+P`/`Cmd+P` để chọn máy in.

## Chạy ứng dụng
Yêu cầu Python 3.9 trở lên. Tại thư mục dự án, cài dependencies và chạy:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Mở URL được Streamlit hiển thị, thường là `http://localhost:8501`.

## Cập nhật menu và hình ảnh
Chỉnh giá trong `DRINKS` (giá theo size) và `TOPPINGS` trong `app.py`. Mỗi thức uống có URL ảnh ở thuộc tính `image`. Bạn có thể tìm ảnh bằng Bing Images, mở nguồn ảnh gốc, kiểm tra giấy phép/điều kiện sử dụng rồi sao chép URL trực tiếp của ảnh vào đây. Không dùng URL trang tìm kiếm thay cho URL tệp ảnh. Các URL ảnh mẫu cần Internet và có thể được thay bằng ảnh do quán sở hữu.

Xem `instruction.txt` để biết hướng dẫn cài đặt và sử dụng chi tiết.

## Giới hạn
Ứng dụng chỉ tạo file HTML có thể mở để in; trình duyệt không cho ứng dụng web tự kết nối trực tiếp với máy in cục bộ. Việc in phụ thuộc vào trình duyệt, driver và cấu hình máy in. Giá hiện tại chỉ là giá mẫu.
