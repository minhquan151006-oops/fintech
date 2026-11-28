import streamlit as st
import pandas as pd

st.set_page_config(page_title="Quản lý tài chính sinh viên", page_icon="🎓", layout="wide")
st.title("🎓 Quản lý thu chi dành cho sinh viên")
st.caption("Theo dõi ngân sách theo danh mục, kiểm soát chi tiêu và lập kế hoạch tiết kiệm.")

CATEGORIES = ["Ăn uống", "Đi lại", "Nhà ở", "Học tập", "Giải trí", "Sức khỏe", "Khác"]

with st.sidebar:
    st.header("Thiết lập ngân sách")
    monthly_income = st.number_input("Thu nhập hàng tháng (VND)", min_value=0, value=5_000_000, step=100_000)
    st.subheader("Hạn mức từng danh mục")
    default_caps = [1_500_000, 500_000, 1_500_000, 700_000, 500_000, 300_000, 300_000]
    caps = {}
    for category, default in zip(CATEGORIES, default_caps):
        caps[category] = st.number_input(category, min_value=0, value=default, step=50_000)

st.subheader("Nhập chi tiêu")
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Danh mục", "Số tiền", "Ghi chú"])

col1, col2, col3 = st.columns(3)
with col1:
    expense_category = st.selectbox("Danh mục", CATEGORIES)
with col2:
    expense_amount = st.number_input("Số tiền (VND)", min_value=0, value=100_000, step=50_000)
with col3:
    expense_note = st.text_input("Ghi chú", placeholder="Ví dụ: tiền ăn trưa")

if st.button("➕ Thêm chi tiêu", use_container_width=True):
    if expense_amount > 0:
        new_row = pd.DataFrame([{
            "Danh mục": expense_category,
            "Số tiền": expense_amount,
            "Ghi chú": expense_note,
        }])
        st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
        st.success("Đã thêm chi tiêu.")
    else:
        st.warning("Số tiền chi tiêu phải lớn hơn 0.")

expenses = st.session_state.expenses
if not expenses.empty:
    expenses["Số tiền"] = pd.to_numeric(expenses["Số tiền"])

st.subheader("Tổng quan tháng")
if expenses.empty:
    spent_by_category = pd.Series({category: 0 for category in CATEGORIES}, dtype=float)
else:
    spent_by_category = expenses.groupby("Danh mục")["Số tiền"].sum().reindex(CATEGORIES, fill_value=0)

total_spending = float(spent_by_category.sum())
remaining = monthly_income - total_spending
savings = max(remaining, 0)
saving_rate = savings / monthly_income * 100 if monthly_income > 0 else 0

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Thu nhập", f"{monthly_income:,.0f} VND")
metric2.metric("Đã chi", f"{total_spending:,.0f} VND")
metric3.metric("Còn lại", f"{remaining:,.0f} VND", "Vượt ngân sách" if remaining < 0 else None)
metric4.metric("Có thể tiết kiệm", f"{savings:,.0f} VND", f"{saving_rate:.1f}% thu nhập")

st.subheader("Chi tiêu theo danh mục")
summary = pd.DataFrame({
    "Đã chi": spent_by_category,
    "Hạn mức": pd.Series(caps),
})
summary["Còn lại"] = summary["Hạn mức"] - summary["Đã chi"]
st.dataframe(summary, use_container_width=True)

warnings = []
suggestions = []
for category in CATEGORIES:
    spent = float(spent_by_category[category])
    cap = float(caps[category])
    if spent > cap:
        excess = spent - cap
        warnings.append(f"**{category}:** đã vượt hạn mức **{excess:,.0f} VND**.")
        suggestions.append(f"Giảm chi {category.lower()} xuống còn tối đa **{cap:,.0f} VND** hoặc điều chỉnh hạn mức trước tháng kế tiếp.")
    elif cap - spent < cap * 0.1:
        suggestions.append(f"{category} đang gần giới hạn; nên giới hạn thêm chi tiêu còn khoảng **{max(cap - spent, 0):,.0f} VND**.")

if remaining < 0:
    warnings.append(f"**Tổng chi tiêu:** vượt thu nhập **{abs(remaining):,.0f} VND**.")

st.subheader("⚠️ Cảnh báo")
if warnings:
    for warning in warnings:
        st.error(warning)
else:
    st.success("Bạn chưa vượt hạn mức ở danh mục nào.")

st.subheader("💡 Gợi ý điều chỉnh chi tiêu")
if suggestions:
    for suggestion in suggestions:
        st.write("• " + suggestion)
else:
    st.info("Hiện chưa có gợi ý điều chỉnh. Hãy duy trì mức chi hiện tại và chuyển phần còn lại vào tiết kiệm.")

if not expenses.empty:
    st.subheader("Danh sách chi tiêu")
    edited = st.data_editor(expenses, num_rows="dynamic", use_container_width=True, key="expense_editor")
    st.session_state.expenses = edited

st.subheader("🌱 Kế hoạch tiết kiệm và đầu tư đơn giản")
plan_col1, plan_col2 = st.columns(2)
with plan_col1:
    saving_goal = st.number_input("Mục tiêu tài chính (VND)", min_value=0, value=12_000_000, step=500_000)
    months = st.number_input("Thời gian dự kiến (tháng)", min_value=1, value=12, step=1)
with plan_col2:
    monthly_target = saving_goal / months
    st.metric("Cần tiết kiệm mỗi tháng", f"{monthly_target:,.0f} VND")
    st.metric("Khả năng tiết kiệm hiện tại", f"{savings:,.0f} VND/tháng")

if savings > 0 and saving_goal > 0:
    gap = monthly_target - savings
    if gap <= 0:
        st.success("Khả năng tiết kiệm hiện tại đủ để đạt mục tiêu. Ưu tiên: 70% quỹ khẩn cấp, 20% mục tiêu tài chính và 10% quỹ đầu tư an toàn; tổng hợp rủi ro trước khi đầu tư.")
    else:
        st.warning(f"Cần tăng tiết kiệm thêm **{gap:,.0f} VND/tháng** để đúng kế hoạch.")
        st.write("Gợi ý: ưu tiên cắt giảm các danh mục có nguy cơ vượt hạn mức, sau đó tự động chuyển tiền tiết kiệm ngay sau khi nhận thu nhập.")
else:
    st.info("Hãy tạo thặng dư từ thu nhập trước khi lập kế hoạch đầu tư. Ưu tiên tích lũy quỹ khẩn cấp tương đương 3–6 tháng chi phí.")

st.caption("Ứng dụng chỉ mang tính hỗ trợ lập kế hoạch tài chính cá nhân, không phải tư vấn tài chính chuyên nghiệp.")
