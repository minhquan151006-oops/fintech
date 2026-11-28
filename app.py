from datetime import datetime
from html import escape
from uuid import uuid4

import streamlit as st

st.set_page_config(page_title="Trà Sữa Milktea | Tính tiền", page_icon="🧋", layout="wide")

# Giá tham khảo (VND). Bạn có thể chỉnh sửa menu và giá tại đây.
DRINKS = {
    "Trà sữa truyền thống": {
        "prices": {"S": 30_000, "M": 38_000, "L": 45_000},
        "image": "https://images.unsplash.com/photo-1558857563-b371033873b8?auto=format&fit=crop&w=900&q=80",
    },
    "Trà sữa matcha": {
        "prices": {"S": 35_000, "M": 42_000, "L": 49_000},
        "image": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?auto=format&fit=crop&w=900&q=80",
    },
    "Trà sữa socola": {
        "prices": {"S": 35_000, "M": 42_000, "L": 49_000},
        "image": "https://images.unsplash.com/photo-1525385133512-2f3fd5c50347?auto=format&fit=crop&w=900&q=80",
    },
    "Trà đào": {
        "prices": {"S": 28_000, "M": 35_000, "L": 42_000},
        "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?auto=format&fit=crop&w=900&q=80",
    },
    "Trà vải": {
        "prices": {"S": 28_000, "M": 35_000, "L": 42_000},
        "image": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?auto=format&fit=crop&w=900&q=80",
    },
    "Matcha latte": {
        "prices": {"S": 35_000, "M": 42_000, "L": 49_000},
        "image": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?auto=format&fit=crop&w=900&q=80",
    },
}
SIZES = {"S": 0, "M": 0, "L": 0}
TOPPINGS = {
    "Trân châu đen": 7_000,
    "Trân châu trắng": 8_000,
    "Pudding trứng": 8_000,
    "Thạch trái cây": 7_000,
    "Kem cheese": 12_000,
}
SUGAR_LEVELS = [0, 25, 50, 75, 100]
ICE_LEVELS = [0, 25, 50, 75, 100]


def vnd(amount: int) -> str:
    return f"{amount:,.0f}".replace(",", ".") + " ₫"


def make_receipt_html(items: list[dict], order_id: str, created_at: str, total: int) -> str:
    rows = "".join(
        "<tr>"
        f"<td>{escape(item['drink'])}<br><small>Size {escape(item['size'])} · Đường {item['sugar']}% · Đá {item['ice']}%</small>"
        f"<br><small>Topping: {escape(', '.join(item['toppings']) if item['toppings'] else 'Không')}</small></td>"
        f"<td class='num'>{item['quantity']}</td>"
        f"<td class='num'>{vnd(item['unit_price'])}</td>"
        f"<td class='num'>{vnd(item['line_total'])}</td>"
        "</tr>"
        for item in items
    )
    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><title>Hóa đơn {escape(order_id)}</title>
<style>
@page {{ size: 80mm auto; margin: 4mm; }}
body {{ font: 13px/1.45 Arial, sans-serif; color: #111; width: 72mm; margin: 0 auto; }}
h1 {{ text-align: center; font-size: 19px; margin: 5px 0; }}
p {{ margin: 4px 0; }} table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
th, td {{ border-bottom: 1px dashed #888; padding: 5px 2px; vertical-align: top; }}
th {{ text-align: left; }} .num {{ text-align: right; white-space: nowrap; }}
.total {{ text-align: right; font-size: 17px; font-weight: bold; margin-top: 10px; }}
.center {{ text-align: center; }} small {{ color: #444; }}
@media screen {{ body {{ margin: 20px auto; }} }}
</style></head><body>
<h1>🧋 MILK TEA</h1><p class="center">Cảm ơn quý khách!</p>
<p>Mã hóa đơn: {escape(order_id)}<br>Thời gian: {escape(created_at)}</p>
<table><thead><tr><th>Món</th><th class="num">SL</th><th class="num">ĐG</th><th class="num">T.Tiền</th></tr></thead>
<tbody>{rows}</tbody></table><p class="total">TỔNG: {vnd(total)}</p>
<p class="center">Hẹn gặp lại quý khách ❤️</p>
</body></html>"""


st.title("🧋 Trà Sữa Milktea")
st.write("Chọn món, tùy chỉnh đường/đá và topping, sau đó thêm vào hóa đơn.")

if "cart" not in st.session_state:
    st.session_state.cart = []
if "order_id" not in st.session_state:
    st.session_state.order_id = uuid4().hex[:8].upper()

with st.sidebar:
    st.header("🍹 Menu thức uống")
    drink_for_image = st.selectbox("Xem hình món:", list(DRINKS), key="preview_drink")
    st.image(DRINKS[drink_for_image]["image"], use_container_width=True)
    st.caption("Ảnh minh họa. Hãy thay URL trong DRINKS bằng ảnh bạn có quyền sử dụng.")

left, right = st.columns([1, 1])
with left:
    st.subheader("Tạo món")
    with st.form("order_item_form"):
        drink = st.selectbox("Loại nước:", list(DRINKS))
        size = st.radio("Size:", list(SIZES), horizontal=True)
        toppings = st.multiselect(
            "Topping (có thể chọn nhiều):",
            list(TOPPINGS),
            format_func=lambda item: f"{item} (+{vnd(TOPPINGS[item])})",
        )
        sugar = st.select_slider("Lượng đường:", options=SUGAR_LEVELS, value=50, format_func=lambda x: f"{x}%")
        ice = st.select_slider("Lượng đá:", options=ICE_LEVELS, value=50, format_func=lambda x: f"{x}%")
        quantity = st.number_input("Số lượng:", min_value=1, max_value=99, value=1, step=1)
        submitted = st.form_submit_button("➕ Thêm vào hóa đơn", type="primary", use_container_width=True)

    if submitted:
        unit_price = DRINKS[drink]["prices"][size] + sum(TOPPINGS[item] for item in toppings)
        st.session_state.cart.append({
            "drink": drink,
            "size": size,
            "toppings": list(toppings),
            "sugar": int(sugar),
            "ice": int(ice),
            "quantity": int(quantity),
            "unit_price": unit_price,
            "line_total": unit_price * int(quantity),
        })
        st.rerun()

with right:
    st.subheader("🧾 Hóa đơn hiện tại")
    if not st.session_state.cart:
        st.info("Chưa có món nào. Hãy chọn món và nhấn ‘Thêm vào hóa đơn’.")
    else:
        for index, item in enumerate(st.session_state.cart, start=1):
            topping_text = ", ".join(item["toppings"]) if item["toppings"] else "Không"
            st.write(
                f"**{index}. {item['drink']} – size {item['size']} × {item['quantity']}**  "
                f"\nĐường {item['sugar']}% · Đá {item['ice']}% · Topping: {topping_text}  "
                f"\n{vnd(item['line_total'])}"
            )
        total = sum(item["line_total"] for item in st.session_state.cart)
        st.divider()
        st.metric("TỔNG CỘNG", vnd(total))

        remove_options = list(range(len(st.session_state.cart)))
        remove_index = st.selectbox(
            "Chọn món cần xóa:",
            remove_options,
            format_func=lambda i: f"{i + 1}. {st.session_state.cart[i]['drink']} – size {st.session_state.cart[i]['size']}",
            key="remove_item_index",
        )
        remove_col, clear_col = st.columns(2)
        if remove_col.button("Xóa món đã chọn", use_container_width=True):
            st.session_state.cart.pop(remove_index)
            if not st.session_state.cart:
                st.session_state.order_id = uuid4().hex[:8].upper()
            st.rerun()
        if clear_col.button("Xóa toàn bộ", use_container_width=True):
            st.session_state.cart = []
            st.session_state.order_id = uuid4().hex[:8].upper()
            st.rerun()

if st.session_state.cart:
    total = sum(item["line_total"] for item in st.session_state.cart)
    created_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    receipt_html = make_receipt_html(st.session_state.cart, st.session_state.order_id, created_at, total)
    st.divider()
    st.subheader("Xuất hóa đơn / in")
    st.download_button(
        "⬇️ Tải hóa đơn HTML (mở file rồi nhấn Ctrl+P để in)",
        data=receipt_html.encode("utf-8"),
        file_name=f"hoa-don-{st.session_state.order_id}.html",
        mime="text/html",
        use_container_width=True,
    )
    st.caption("Hóa đơn được định dạng khổ giấy 80 mm; trong hộp thoại in, chọn máy in hóa đơn và khổ giấy phù hợp.")

st.caption("Giá trong ứng dụng là giá mẫu, có thể cập nhật ở phần DRINKS và TOPPINGS trong app.py.")
