import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
from datetime import datetime

# បង្កើតសញ្ញា (Session State) សម្រាប់រក្សាទុកតម្លៃបណ្តោះអាសន្ន
if 'total_electric' not in st.session_state:
    st.session_state['total_electric'] = 0.0
if 'total_water' not in st.session_state:
    st.session_state['total_water'] = 0.0

# --- អនុគមន៍គ្រប់គ្រងអតិថិជន និងការកត់ត្រា ---
CUSTOMER_FILE = "customers.csv"

def get_customer_name(user_id):
    if os.path.exists(CUSTOMER_FILE):
        df = pd.read_csv(CUSTOMER_FILE, dtype={'User ID': str})
        result = df[df['User ID'] == str(user_id)]
        if not result.empty:
            return result.iloc[0]['Customer Name']
    return None

def save_new_customer(user_id, user_name):
    new_cust = pd.DataFrame([{"User ID": str(user_id), "Customer Name": user_name}])
    if os.path.exists(CUSTOMER_FILE):
        df = pd.read_csv(CUSTOMER_FILE, dtype={'User ID': str})
        if str(user_id) not in df['User ID'].values:
            new_cust.to_csv(CUSTOMER_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
            return True
    else:
        new_cust.to_csv(CUSTOMER_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')
        return True
    return False

def log_data(user_id, user_name, date_line, elec_old, elec_new, elec_total, water_old, water_new, water_total, debt, grand_total):
    log_file = "invoice_logs.csv"
    new_data = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "User ID": user_id,
        "Customer Name": user_name,
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
    df_new = pd.DataFrame([new_data])
    if os.path.exists(log_file):
        df_new.to_csv(log_file, mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(log_file, mode='w', header=True, index=False, encoding='utf-8-sig')


st.title("🍏 ⚡ ប្រព័ន្ធគណនាទិន្នន័យ ទឹក-អគ្គសនី")
st.write("សូមបំពេញព័ត៌មានខាងក្រោមដើម្បីគណនាថ្លៃប្រាក់")
st.divider()

# --- 🛠️ ផ្នែកកែសម្រួល៖ ប្រើប្រាស់ Form សម្រាប់គ្រប់គ្រងព័ត៌មានអតិថិជន ---
st.subheader("👤 ព័ត៌មានអតិថិជន")
id_user = st.text_input("បញ្ចូល ID របស់អ្នក:").strip()

customer_name = ""
if id_user:
    existing_name = get_customer_name(id_user)
    if existing_name:
        st.success(f"👤 ឈ្មោះអតិថិជន៖ {existing_name}")
        customer_name = existing_name
    else:
        st.warning(f"⚠️ មិនទាន់មាន ID [{id_user}] នេះក្នុងប្រព័ន្ធទេ។ សូមបំពេញទម្រង់ខាងក្រោមដើម្បីចុះឈ្មោះ៖")
        # ប្រើប្រាស់ st.form ដើម្បីកុំឱ្យវា Rerun ពេលកំពុងវាយឈ្មោះ
        with st.form("customer_registration_form"):
            new_name = st.text_input("បញ្ចូល ឈ្មោះអតិថិជនថ្មី:")
            submit_reg = st.form_submit_button("💾 ចុះឈ្មោះអតិថិជនថ្មី")
            
            if submit_reg:
                if new_name.strip():
                    save_new_customer(id_user, new_name.strip())
                    st.success(f"🎉 បានចុះឈ្មោះ {new_name} រួចរាល់! សូមចុចបញ្ចូល ID ម្តងទៀតដើម្បីទាញទិន្នន័យ។")
                    st.rerun()
                else:
                    st.error("❌ សូមបញ្ចូលឈ្មោះអតិថិជន!")

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

used_water = new_num_water - old_num_water

if st.button("គណនាថ្លៃទឹក"):
    st.subheader(f"📊 ចំនួនទឹកប្រើប្រាស់សរុប = {used_water} ម៉ែត្រគូប (m³)")
    st.session_state['total_water'] = used_water * 2000
    st.info(f"💵 ទឹកប្រាក់ថ្លៃទឹកសរុប៖ {st.session_state['total_water']} ៛")

st.divider()

# --- ផ្នែកទូទាត់ប្រាក់សរុប និង បំណុល ---
st.header("💰 ផ្នែកទូទាត់ប្រាក់សរុប")
debt_electric = st.number_input("បំណុលចាស់ (រៀល) =", value=0.0, key="debt_elec")

total_money = st.session_state['total_electric'] + st.session_state['total_water'] + debt_electric

st.success(f"💵 Total ទឹកប្រាក់សរុបនៅថ្ងៃនេះ (រួមទាំងបំណុល)៖ {total_money} ៛")

if st.button("💾 រក្សាទុកការកត់ត្រានេះ"):
    if id_user and customer_name:
        log_data(
            id_user, customer_name, date_line, 
            old_num_electric, new_num_electric, st.session_state['total_electric'],
            old_num_water, new_num_water, st.session_state['total_water'],
            debt_electric, total_money
        )
        st.toast("✅ បានកត់ត្រាទិន្នន័យចូលក្នុងប្រព័ន្ធជោគជ័យ!")
    else:
        st.error("❌ មិនអាចកត់ត្រាបានទេ! សូមប្រាកដថាបានបំពេញ ID និងចុះឈ្មោះអតិថិជនត្រឹមត្រូវ។")

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

# --- ផ្នែកបង្ហាញទិន្នន័យលាក់មិនឱ្យព្រីន ---
no_print_area = st.container()
with no_print_area:
    st.html("<style>@media print { div[data-testid='stVerticalBlock'] > div:last-child { display: none !important; } }</style>")
    st.subheader("📋 ប្រវត្តិនៃការកត់ត្រាទិន្នន័យកន្លងមក (បង្ហាញតែលើអេក្រង់ មិនព្រីនទេ)")
    if os.path.exists("invoice_logs.csv"):
        df_logs = pd.read_csv("invoice_logs.csv")
        st.dataframe(df_logs)
    else:
        st.info("មិនទាន់មានទិន្នន័យកត់ត្រានៅឡើយទេ។")
