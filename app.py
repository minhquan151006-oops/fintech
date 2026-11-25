import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st

st.set_page_config(page_title="Tính lãi tiết kiệm", page_icon="💰")
st.title("Ứng Dụng Tính Lãi Suất Tiết Kiệm")
st.write(
    "Chọn ngân hàng và kỳ hạn để tra cứu lãi suất từ API đã cấu hình, "
    "sau đó tính số tiền nhận được theo lãi đơn và lãi kép."
)

# Các mã ngân hàng gửi cho API. Hãy sửa theo quy ước của nhà cung cấp API.
BANKS = {
    "Vietcombank": "VCB",
    "BIDV": "BIDV",
    "VietinBank": "CTG",
    "Agribank": "AGRIBANK",
    "Techcombank": "TCB",
    "MB Bank": "MB",
    "ACB": "ACB",
}

bank_name = st.selectbox("Chọn ngân hàng:", list(BANKS))
vnd = st.number_input(
    "Nhập số tiền gửi của bạn (VND):",
    min_value=0,
    value=10_000_000,
    step=100_000,
)
months = st.number_input(
    "Nhập số tháng gửi (tháng):", min_value=1, value=3, step=1
)
withdraw_early = st.checkbox(\"Bạn có muốn rút tiền trước hạn không?\")
# Không có API công khai chung cho mọi ngân hàng. Cấu hình URL API mà bạn
# được phép sử dụng trong .streamlit/secrets.toml (xem hướng dẫn bên dưới).
api_url = st.secrets.get("RATE_API_URL", "").strip()
api_token = st.secrets.get("RATE_API_TOKEN", "").strip()
live_rate = None
rate_date = None
lookup_error = None

if api_url:
    query = urlencode(
        {
            "bank": BANKS[bank_name],
            "term_months": int(months),
            "currency": "VND",
        }
    )
    separator = "&" if "?" in api_url else "?"
    request = Request(f"{api_url}{separator}{query}", headers={"Accept": "application/json"})
    if api_token:
        request.add_header("Authorization", f"Bearer {api_token}")

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))

        # API cần trả về JSON dạng {"rate": 5.0, "effective_date": "2026-01-01"}.
        # Lãi suất `rate` được hiểu là phần trăm mỗi năm (%/năm).
        if not isinstance(payload, dict) or "rate" not in payload:
            raise ValueError("Phản hồi API không có trường 'rate'.")
        live_rate = float(payload["rate"])
        if live_rate < 0:
            raise ValueError("Lãi suất API trả về không hợp lệ.")
        rate_date = payload.get("effective_date")
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        lookup_error = str(exc)
else:
    lookup_error = "Chưa cấu hình RATE_API_URL."

if live_rate is not None:
    st.success(f"Lãi suất {bank_name}, kỳ hạn {int(months)} tháng: {live_rate:g}%/năm")
    if rate_date:
        st.caption(f"Ngày hiệu lực do API cung cấp: {rate_date}")
    default_rate = live_rate
else:
    st.warning(
        "Chưa lấy được lãi suất tự động. Nhập lãi suất thủ công bên dưới. "
        "Giá trị thủ công không phải dữ liệu cập nhật từ ngân hàng."
    )
    if lookup_error:
        st.caption(f"Chi tiết: {lookup_error}")
    default_rate = 5.0

annual_rate_percent = st.number_input(
    "Lãi suất (%/năm):",
    min_value=0.0,
    value=float(default_rate),
    step=0.1,
    format="%.4f",
    help="Khi API hoạt động, trường này được điền bằng lãi suất tra cứu; bạn vẫn có thể chỉnh sửa.",
)

# Quy đổi lãi suất năm sang lãi suất tháng để tính với kỳ hạn nhập theo tháng.
monthly_rate = annual_rate_percent / 100 / 12
simple_total = vnd * (1 + months * monthly_rate)
compound_total = vnd * (1 + monthly_rate) ** months

st.subheader("Kết quả tính toán:")
st.success(f"Số tiền nhận được theo lãi đơn: {simple_total:,.2f} VND")
st.info(f"Số tiền nhận được theo lãi kép: {compound_total:,.2f} VND")
st.caption(
    "Kết quả là ước tính theo lãi suất năm chia đều theo tháng; cách tính thực tế "
    "có thể khác tùy sản phẩm, ngày gửi/rút và quy định của ngân hàng."
)
