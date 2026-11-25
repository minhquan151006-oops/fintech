# Ứng Dụng Tính Lãi Suất Tiết Kiệm

Ứng dụng Streamlit giúp ước tính số tiền nhận được khi gửi tiết kiệm theo **lãi đơn** và **lãi kép**. Người dùng chọn ngân hàng, nhập số tiền và kỳ hạn theo tháng; ứng dụng có thể tra cứu lãi suất qua API nếu được cấu hình.

> **Lưu ý:** Ứng dụng không tích hợp sẵn API lãi suất của ngân hàng nào. Muốn tra cứu tự động, bạn cần có một API mà bạn được phép sử dụng và cấu hình URL của API. Nếu chưa cấu hình hoặc API gặp lỗi, ứng dụng cho phép nhập lãi suất thủ công. Lãi suất thủ công mặc định 5%/năm chỉ là giá trị khởi đầu, không phải lãi suất hiện hành của ngân hàng.

## Yêu cầu

- Python 3.9 trở lên
- Một API lãi suất (tùy chọn; cần thiết nếu muốn tra cứu tự động)

## Cài đặt và chạy

Tại thư mục chứa `app.py`, cài Streamlit và khởi động ứng dụng:

```bash
python -m pip install streamlit
streamlit run app.py
```

Streamlit sẽ in địa chỉ ứng dụng vào terminal và thường mở nó trong trình duyệt.

## Cấu hình tra cứu lãi suất tự động

Ứng dụng đọc các khóa cấu hình Streamlit `RATE_API_URL` và `RATE_API_TOKEN` từ `st.secrets`. Tạo file `.streamlit/secrets.toml` trong thư mục dự án:

```toml
RATE_API_URL = "https://your-provider.example/api/rates"
RATE_API_TOKEN = "your-api-token"
```

Nếu API không yêu cầu xác thực, có thể bỏ dòng `RATE_API_TOKEN`. **Không đưa token thật lên GitHub.** Giữ file secrets khỏi Git bằng cách thêm `.streamlit/secrets.toml` vào `.gitignore`; trên Streamlit Community Cloud, khai báo các khóa trong mục **App settings → Secrets**.

Ứng dụng gửi yêu cầu GET đến URL đã cấu hình, kèm các tham số truy vấn:

- `bank`: mã ngân hàng, ví dụ `VCB`, `BIDV`, `CTG`, `AGRIBANK`, `TCB`, `MB` hoặc `ACB`.
- `term_months`: kỳ hạn người dùng chọn, tính theo tháng.
- `currency`: luôn là `VND`.

Ví dụ URL yêu cầu sau khi thêm tham số:

```text
https://your-provider.example/api/rates?bank=VCB&term_months=3&currency=VND
```

Nếu có `RATE_API_TOKEN`, ứng dụng gửi token trong header `Authorization: Bearer <token>`.

API cần trả về JSON object có trường `rate`, là số phần trăm **mỗi năm**. Ví dụ:

```json
{
  "rate": 5.0,
  "effective_date": "2026-01-01"
}
```

`effective_date` là tùy chọn và sẽ được hiển thị nếu API cung cấp. Các ngân hàng trong danh sách hiện được ánh xạ sang mã cố định trong `app.py`; hãy điều chỉnh `BANKS` nếu API của bạn dùng mã khác. Cấu trúc request/response cũng cần được điều chỉnh trong `app.py` nếu nhà cung cấp có định dạng khác.

## Cách tính

Lãi suất API hoặc lãi suất nhập tay được hiểu là lãi suất năm theo phần trăm. Ứng dụng quy đổi sang lãi suất tháng bằng cách chia cho 12, rồi tính:

- **Lãi đơn:** `tiền gốc × (1 + số tháng × lãi suất tháng)`
- **Lãi kép:** `tiền gốc × (1 + lãi suất tháng) ^ số tháng`

Đây là ước tính. Cách tính thực tế có thể khác theo sản phẩm, ngày gửi/rút và quy định của ngân hàng.

## Xử lý lỗi API

Nếu chưa cấu hình URL, API không phản hồi, phản hồi không hợp lệ hoặc thiếu trường `rate`, ứng dụng sẽ báo chưa lấy được lãi suất tự động và cho phép nhập lãi suất thủ công. Hãy xác minh URL, quyền truy cập, mã ngân hàng và định dạng JSON với tài liệu của nhà cung cấp API.
