import hmac
import json
import uuid
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st

st.set_page_config(page_title="Cơm Tấm Nhà Mình", page_icon="🍚", layout="wide")
st.title("🍚 Cơm Tấm Nhà Mình")
st.write("Chọn món, xem giá và tải hóa đơn. Chủ quán có thể quản lý menu trong mục dành cho quản trị.")

MENU_FILE = Path(__file__).with_name("menu.json")
DEFAULT_MENU = [
    {"id": "com-tam-suon", "name": "Cơm tấm sườn nướng", "category": "Món ăn", "price": 45000, "image_query": "cơm tấm sườn nướng"},
    {"id": "com-tam-suon-bi-cha", "name": "Cơm tấm sườn bì chả", "category": "Món ăn", "price": 55000, "image_query": "cơm tấm sườn bì chả"},
    {"id": "com-tam-dac-biet", "name": "Cơm tấm đặc biệt", "category": "Món ăn", "price": 65000, "image_query": "cơm tấm đặc biệt"},
    {"id": "bi-them", "name": "Bì thêm", "category": "Món ăn", "price": 10000, "image_query": "bì cơm tấm"},
    {"id": "cha-trung", "name": "Chả trứng", "category": "Món ăn", "price": 12000, "image_query": "chả trứng cơm tấm"},
    {"id": "tra-da", "name": "Trà đá", "category": "Đồ uống", "price": 5000, "image_query": "trà đá Việt Nam"},
    {"id": "nuoc-ngot", "name": "Nước ngọt", "category": "Đồ uống", "price": 15000, "image_query": "nước ngọt lon"},
    {"id": "sua-dau-nanh", "name": "Sữa đậu nành", "category": "Đồ uống", "price": 12000, "image_query": "sữa đậu nành"},
]


def load_menu():
    if not MENU_FILE.exists():
        save_menu(DEFAULT_MENU)
        return DEFAULT_MENU.copy()
    try:
        with MENU_FILE.open("r", encoding="utf-8") as menu_file:
            data = json.load(menu_file)
        if isinstance(data, list) and all(
            isinstance(item, dict)
            and all(key in item for key in ("id", "name", "category", "price", "image_query"))
            for item in data
        ):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    st.error("Không đọc được menu.json. Hãy kiểm tra định dạng hoặc khôi phục tệp menu.")
    return DEFAULT_MENU.copy()


def save_menu(menu):
    with MENU_FILE.open("w", encoding="utf-8") as menu_file:
        json.dump(menu, menu_file, ensure_ascii=False, indent=2)


def get_secret(name, default=""):
    try:
        return str(st.secrets.get(name, default)).strip()
    except Exception:
        return default


# Dùng Bing Image Search API. Thiết lập khóa trong .streamlit/secrets.toml;
# có thể đổi endpoint nếu tài khoản/nhà cung cấp của bạn dùng endpoint khác.
BING_ENDPOINT = get_secret("BING_IMAGE_API_ENDPOINT", "https://api.bing.microsoft.com/v7.0/images/search")
BING_API_KEY = get_secret("BING_IMAGE_API_KEY")


@st.cache_data(ttl=30 * 24 * 60 * 60, show_spinner=False)
def bing_image_url(query, endpoint, api_key):
    """Lấy thumbnail từ Bing và lưu cache tối đa 30 ngày cho mỗi truy vấn."""
    if not api_key or not query:
        return None
    separator = "&" if "?" in endpoint else "?"
    url = f"{endpoint}{separator}{urlencode({'q': query, 'count': 1, 'safeSearch': 'Moderate'})}"
    request = Request(
        url,
        headers={"Accept": "application/json", "Ocp-Apim-Subscription-Key": api_key},
    )
    try:
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        results = payload.get("value", [])
        return results[0].get("thumbnailUrl") if results else None
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


menu = load_menu()

with st.expander("🔐 Quản lý menu (chủ quán)", expanded=False):
    admin_password = get_secret("ADMIN_PASSWORD")
    if not admin_password:
        st.warning("Để chỉnh sửa menu an toàn, hãy cấu hình ADMIN_PASSWORD trong .streamlit/secrets.toml.")
    elif not st.session_state.get("is_admin", False):
        with st.form("admin_login"):
            password_input = st.text_input("Mật khẩu quản trị", type="password")
            login_clicked = st.form_submit_button("Đăng nhập")
        if login_clicked:
            if hmac.compare_digest(password_input, admin_password):
                st.session_state["is_admin"] = True
                st.rerun()
            st.error("Mật khẩu không đúng.")
    else:
        if st.button("Đăng xuất quản trị"):
            st.session_state["is_admin"] = False
            st.rerun()

        st.caption("Sửa thông tin/giá hoặc đánh dấu món cần xóa, sau đó lưu thay đổi.")
        with st.form("edit_menu"):
            edited_items = []
            for item in menu:
                st.markdown(f"**{item['name']}**")
                col_name, col_category, col_price, col_query, col_delete = st.columns([2, 1, 1, 2, 0.8])
                name = col_name.text_input("Tên món", value=item["name"], key=f"name_{item['id']}")
                category = col_category.selectbox(
                    "Loại", ["Món ăn", "Đồ uống"],
                    index=0 if item["category"] == "Món ăn" else 1,
                    key=f"category_{item['id']}",
                )
                price = col_price.number_input(
                    "Giá (VND)", min_value=0, value=int(item["price"]), step=1000,
                    key=f"price_{item['id']}",
                )
                image_query = col_query.text_input(
                    "Từ khóa ảnh Bing", value=item["image_query"], key=f"query_{item['id']}"
                )
                delete_item = col_delete.checkbox("Xóa", key=f"delete_{item['id']}")
                edited_items.append({
                    "id": item["id"], "name": name.strip(), "category": category,
                    "price": int(price), "image_query": image_query.strip(), "delete": delete_item,
                })
            save_edits = st.form_submit_button("Lưu thay đổi menu")

        if save_edits:
            updated_menu = [
                {key: value for key, value in item.items() if key != "delete"}
                for item in edited_items
                if not item["delete"] and item["name"]
            ]
            try:
                save_menu(updated_menu)
                st.success("Đã lưu menu.")
                st.rerun()
            except OSError as exc:
                st.error(f"Không thể lưu menu: {exc}")

        with st.form("add_menu_item"):
            st.markdown("**Thêm món mới**")
            new_name = st.text_input("Tên món mới")
            new_category = st.selectbox("Loại món mới", ["Món ăn", "Đồ uống"])
            new_price = st.number_input("Giá món mới (VND)", min_value=0, value=10000, step=1000)
            new_query = st.text_input("Từ khóa tìm ảnh Bing", value=new_name)
            add_clicked = st.form_submit_button("Thêm món")
        if add_clicked:
            if not new_name.strip():
                st.error("Vui lòng nhập tên món.")
            else:
                menu.append({
                    "id": uuid.uuid4().hex,
                    "name": new_name.strip(),
                    "category": new_category,
                    "price": int(new_price),
                    "image_query": new_query.strip() or new_name.strip(),
                })
                try:
                    save_menu(menu)
                    st.success("Đã thêm món vào menu.")
                    st.rerun()
                except OSError as exc:
                    st.error(f"Không thể lưu menu: {exc}")

st.subheader("Thực đơn")
if not menu:
    st.info("Menu hiện chưa có món nào. Chủ quán có thể thêm món trong mục quản lý menu.")

quantities = {}
for category in ("Món ăn", "Đồ uống"):
    category_items = [item for item in menu if item["category"] == category]
    if not category_items:
        continue
    st.markdown(f"### {category}")
    cards = st.columns(3)
    for index, item in enumerate(category_items):
        with cards[index % len(cards)]:
            image_url = bing_image_url(item["image_query"], BING_ENDPOINT, BING_API_KEY)
            if image_url:
                st.image(image_url, use_container_width=True)
            else:
                bing_search_url = "https://www.bing.com/images/search?" + urlencode({"q": item["image_query"]})
                st.markdown(f"[🔎 Xem ảnh minh họa trên Bing]({bing_search_url})")
            st.markdown(f"**{item['name']}**")
            st.write(f"Giá: **{int(item['price']):,} VND**")
            quantities[item["id"]] = st.number_input(
                "Số lượng", min_value=0, value=0, step=1, key=f"quantity_{item['id']}"
            )

ordered_items = [
    (item, int(quantities.get(item["id"], 0)))
    for item in menu
    if int(quantities.get(item["id"], 0)) > 0
]
total = sum(int(item["price"]) * quantity for item, quantity in ordered_items)

st.subheader("Hóa đơn")
if not ordered_items:
    st.info("Chưa có món nào được chọn.")
else:
    customer_name = st.text_input("Tên khách hàng (không bắt buộc)")
    receipt_lines = [
        "CƠM TẤM NHÀ MÌNH",
        f"Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"Khách hàng: {customer_name.strip() or 'Khách lẻ'}",
        "-" * 44,
        f"{'Món':24} {'SL':>4} {'Đơn giá':>10} {'Thành tiền':>12}",
        "-" * 44,
    ]
    for item, quantity in ordered_items:
        line_total = int(item["price"]) * quantity
        st.write(f"{item['name']} × {quantity} — {line_total:,} VND")
        receipt_lines.append(
            f"{item['name'][:24]:24} {quantity:>4} {int(item['price']):>10,} {line_total:>12,}"
        )
    receipt_lines.extend(["-" * 44, f"TỔNG CỘNG: {total:,} VND", "Cảm ơn quý khách!"])
    st.success(f"Tổng cộng: {total:,} VND")
    st.download_button(
        "⬇️ Tải hóa đơn (.txt)",
        data="\n".join(receipt_lines),
        file_name=f"hoa-don-com-tam-{datetime.now():%Y%m%d-%H%M%S}.txt",
        mime="text/plain; charset=utf-8",
    )

st.caption(
    "Ảnh dùng thumbnail từ Bing Image Search và được cache tối đa 30 ngày. "
    "Menu được lưu trong menu.json; môi trường triển khai cần cho phép ghi tệp và lưu trữ bền vững."
)
