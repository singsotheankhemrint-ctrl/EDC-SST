import streamlit as st
import streamlit.components.v1 as components
import pandas as pd # បន្ថែម library នេះសម្រាប់គ្រប់គ្រងទិន្នន័យ CSV
import os
from datetime import datetime

# បង្កើតសញ្ញា (Session State) សម្រាប់រក្សាទុកតម្លៃបណ្តោះអាសន្ន
if 'total_electric' not in st.session_state:
    st.session_state['total_electric'] = 0.0
if 'total_water' not in st.session_state:
    st.session_state['total_water'] = 0.0

# ---------------------------------------------------------
# អនុគមន៍សម្រាប់កត់ត្រាទិន្នន័យចូលក្នុងហ្វាយ CSV (Data Logging Function)
# ---------------------------------------------------------
def log_data(user_id, date_line, elec_old, elec_new, elec_total, water_old, water_new, water_total, debt, grand_total):
    log_file = "invoice_logs.csv"
    
    # បង្កើតទិន្នន័យថ្មីមួយជួរ (Row)
    new_data = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "User ID": user_id,
        "Date Line": date_line,
        "Electric Old": elec_old,
        "Electric New": elec_new,
        "Electric Total (៛)": elec_total,
        "Water Old": water_old,
        "Water New": water_new,
        "Water Total (៛)": water_total,
        "Debt (៛)": debt,
        "Grand Total (៛)": grand_total
    }
    
    # បំប្លែងទៅជា DataFrame
    df_new = pd.DataFrame([new_data])
    
    # បើសិនជាមានហ្វាយស្រាប់ វានឹងថែមបន្តកន្ទុយ បើមិនទាន់មានវាបង្កើតហ្វាយថ្មី
    if os.path.exists(log_file):
        df_new.to_csv(log_file, mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(log_file, mode='w', header=True, index=False, encoding='utf-8-sig')


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
debt_electric = st.number_input("បំណុលចាស់ (រៀល) =", value=0.0, key="debt_elec")

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

used_water = new_num_water - old_num_water

if st.button("គណនាថ្លៃទឹក"):
    st.subheader(f"📊 ចំនួនទឹកប្រើប្រាស់សរុប = {used_water} ម៉ែត្រគូប (m³)")
    st.session_state['total_water'] = used_water * 2000
    st.info(f"💵 ទឹកប្រាក់ថ្លៃទឹកសរុប៖ {st.session_state['total_water']} ៛")

st.divider()

# --- ផ្នែកសរុបប្រាក់ និងរក្សាទុកទិន្នន័យ ---
total_money = st.session_state['total_electric'] + st.session_state['total_water'] + debt_electric

st.success(f"💵 Total ទឹកប្រាក់សរុបនៅថ្ងៃនេះ (រួមទាំងបំណុល)៖ {total_money} ៛")

# ប៊ូតុងសម្រាប់រក្សាទុកទិន្នន័យចូលក្នុងប្រព័ន្ធ (Data Logging Button)
if st.button("💾 រក្សាទុកការកត់ត្រានេះ"):
    log_data(
        id_user, date_line, 
        old_num_electric, new_num_electric, st.session_state['total_electric'],
        old_num_water, new_num_water, st.session_state['total_water'],
        debt_electric, total_money
    )
    st.toast("✅ បានកត់ត្រាទិន្នន័យចូលក្នុងប្រព័ន្ធជោគជ័យ!")

st.divider()

# --- ប៊ូតុងព្រីន ---
print_btn = """
<button onclick="window.parent.print()" style="
    background-color: #4CAF50;
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

# --- ផ្នែកបង្ហាញទិន្នន័យដែលបានកត់ត្រាទុក (View Logs) ---
st.divider()
st.subheader("📋 ប្រវត្តិនៃការកត់ត្រាទិន្នន័យកន្លងមក")
if os.path.exists("invoice_logs.csv"):
    df_logs = pd.read_csv("invoice_logs.csv")
    st.dataframe(df_logs) # បង្ហាញជាតារាងនៅលើ Streamlit App តែម្តង
else:
    st.info("មិនទាន់មានទិន្នន័យកត់ត្រានៅឡើយទេ។")
