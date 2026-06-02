import streamlit as st
import streamlit.components.v1 as components

if 'total_electric' not in st.session_state:
    st.session_state['total_electric'] = 0.0
if 'total_water' not in st.session_state:
    st.session_state['total_water'] = 0.0

st.title("🍏 ⚡ ប្រព័ន្ធគណនាទិន្នន័យ ទឹក-អគ្គសនី")
st.write("សូមបំពេញព័ត៌មានខាងក្រោមដើម្បីគណនាថ្លៃប្រាក់")
st.divider()

id_user = st.text_input("បញ្ចូល ID របស់អ្នក")
if id_user == "e20251016":
    st.success("👤 ឈ្មោះអតិថិជន៖ Sok San")

date_line = st.text_input("កាលបរិច្ឆេទ (Date Line):")
st.divider()

# --- ផ្នែកទី ១៖ គណនាថ្លៃអគ្គសនី ---
st.header("⚡ គណនាថ្លៃអគ្គសនី")
old_num_electric = st.number_input("លេខថាមពលចាស់ (ភ្លើង) =", value=0.0, key="old_elec")
new_num_electric = st.number_input("លេខថាមពលថ្មី (ភ្លើង) =", value=0.0, key="new_elec")

used_electric = new_num_electric - old_num_electric

if st.button("គណនាថ្លៃអគ្គសនី"):
    st.subheader(f"📊 ថាមពលប្រើប្រាស់សរុប = {used_electric} kWh")
    if used_electric <= 0:
        st.session_state['total_electric'] = 500.0
    else:
        st.session_state['total_electric'] = used_electric * 1000
    st.info(f"💵 ទឹកប្រាក់ថ្លៃភ្លើងសរុប៖ {st.session_state['total_electric']} ៛")

st.divider()

# --- ផ្នែកទី ២៖ គណនាថ្លៃទឹក ---
st.header("💧 គណនាថ្លៃទឹកស្អាត")
old_num_water = st.number_input("លេខនាឡិកាចាស់ (ទឹក) =", value=0.0, key="old_water")
new_num_water = st.number_input("លេខនាឡិកាថ្មី (ទឹក) =", value=0.0, key="new_water")
debt_electric = st.number_input("បំណុលចាស់ (រៀល) =", value=0.0, key="debt_elec")

used_water = new_num_water - old_num_water

if st.button("គណនាថ្លៃទឹក"):
    st.subheader(f"📊 ចំនួនទឹកប្រើប្រាស់សរុប = {used_water} ម៉ែត្រគូប (m³)")
    st.session_state['total_water'] = used_water * 2000
    st.info(f"💵 ទឹកប្រាក់ថ្លៃទឹកសរុប៖ {st.session_state['total_water']} ៛")

st.divider()

# --- ផ្នែកសរុបប្រាក់ និងប៊ូតុងព្រីន ---
total_money = st.session_state['total_electric'] + st.session_state['total_water'] + debt_electric

st.success(f"💵 Total ទឹកប្រាក់សរុបនៅថ្ងៃនេះ (រួមទាំងបំណុល)៖ {total_money} ៛")

print_btn = """
<button onclick="window.parent.print()" style="
    background-color: #4CAF50; /* ពណ៌បៃតង */
    border: none;
    color: white;
    padding: 10px 24px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 8px;
">Print វិក្កយបត្រ</button>
"""

components.html(print_btn, height=60)
