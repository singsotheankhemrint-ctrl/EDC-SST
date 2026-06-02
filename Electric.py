import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
from datetime import datetime

# --- កំណត់ទិន្នន័យគណនីសម្រាប់ Login (Username: Password) ---
USER_ACCOUNTS = {
    "admin": "admin123",
    "staff1": "staff123",
    "staff2": "staff2026"
}
ADMIN_PASSWORD = "admin123" # ពាក្យសម្ងាត់ចម្បងសម្រាប់អនុញ្ញាតឱ្យលុបទិន្នន័យ

# --- បង្កើត Session State សម្រាប់រក្សាទុកស្ថានភាព Login ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = ""
if 'total_electric' not in st.session_state:
    st.session_state['total_electric'] = 0.0
if 'total_water' not in st.session_state:
    st.session_state['total_water'] = 0.0

# --- ឈ្មោះឯកសារទិន្នន័យ ---
CUSTOMER_FILE = "customers.csv"
LOG_FILE = "invoice_logs.csv"

# --- អនុគមន៍គ្រប់គ្រងអតិថិជន ---
def get_customer_name(user_id):
    if os.path.exists(CUSTOMER_FILE):
        try:
            df = pd.read_csv(CUSTOMER_FILE, dtype={'User ID': str})
            result = df[df['User ID'] == str(user_id)]
            if not result.empty:
                return result.iloc[0]['Customer Name']
        except Exception:
            pass
    return None

def save_new_customer(user_id, user_name):
    new_cust = pd.DataFrame([{"User ID": str(user_id), "Customer Name": user_name}])
    if os.path.exists(CUSTOMER_FILE):
        try:
            df = pd.read_csv(CUSTOMER_FILE, dtype={'User ID': str})
            if str(user_id) not in df['User ID'].values:
                new_cust.to_csv(CUSTOMER_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
        except Exception:
            new_cust.to_csv(CUSTOMER_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')
    else:
        new_cust.to_csv(CUSTOMER_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')

# --- អនុគមន៍កត់ត្រាទិន្នន័យ ---
def log_data(user_id, user_name, date_line, elec_old, elec_new, elec_total, water_old, water_new, water_total, room_fee, debt, grand_total, created_by):
    new_data = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "User ID": str(user_id),
        "Customer Name": user_name,
        "Date Line": date_line,
        "Electric Old": elec_old,
        "Electric New": elec_new,
        "Electric Total (៛)": elec_total,
        "Water Old": water_old,
        "Water New": water_new,
        "Water Total (៛)": water_total,
        "Room Fee (៛)": room_fee,
        "ប្រាក់ជំពាក់ (៛)": debt,
        "Grand Total (៛)": grand_total,
        "Recorded By": created_by # កត់ត្រាទុកថាអ្នកណាជាអ្នកបញ្ចូល
    }
    df_new = pd.DataFrame([new_data])
    
    if os.path.exists(LOG_FILE):
        try:
            pd.read_csv(LOG_FILE, nrows=1)
            df_new.to_csv(LOG_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
        except Exception:
            df_new.to_csv(LOG_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(LOG_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')


# =========================================================
# 🔐 ផ្នែកទី ១៖ ប្រព័ន្ធ LOGIN (Multi-Account)
# =========================================================
if not st.session_state['logged_in']:
    st.subheader("🔐 សូមចូលប្រើប្រាស់ប្រព័ន្ធ (Login)")
    username_input = st.text_input("ឈ្មោះគណនី (Username):")
    password_input = st.text_input("ពាក្យសម្ងាត់ (Password):", type="password")
    
    if st.button("🔑 ចូលប្រើប្រាស់"):
        if username_input in USER_ACCOUNTS and USER_ACCOUNTS[username_input] == password_input:
            st.session_state['logged_in'] = True
            st.session_state['current_user'] = username_input
            st.success(f"🎉 ស្វាគមន៍ការចូលមកកាន់ប្រព័ន្ធ, {username_input}!")
            st.rerun()
        else:
            st.error("❌ ឈ្មោះគណនី ឬពាក្យសម្ងាត់មិនត្រឹមត្រូវទេ!")
    st.stop() # ឃាត់មិនឱ្យកូដខាងក្រោមដំណើរការ បើមិនទាន់ Login

# --- ប៊ូតុង Logout នៅផ្នែកខាងលើ ---
st.sidebar.write(f"👤 គណនីកំពុងប្រើប្រាស់៖ **{st.session_state['current_user']}**")
if st.sidebar.button("🚪 ចាកចេញ (Logout)"):
    st.session_state['logged_in'] = False
    st.session_state['current_user'] = ""
    st.rerun()


# =========================================================
# 🍏 ផ្នែកទី ២៖ កម្មវិធីគណនាធម្មតា (ដំណើរការក្រោយ Login រួច)
# =========================================================
st.title("🍏 ⚡ ប្រព័ន្ធគណនាទិន្នន័យ ទឹក-អគ្គសនី")
st.write("សូមបំពេញព័ត៌មានខាងក្រោមដើម្បីគណនាថ្លៃប្រាក់")
st.divider()

# --- ផ្នែកគ្រប់គ្រងព័ត៌មានអតិថិជន ---
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
        with st.form("customer_registration_form"):
            new_name = st.text_input("បញ្ចូល ឈ្មោះអតិថិជនថ្មី:")
            submit_reg = st.form_submit_button("💾 ចុះឈ្មោះអតិថិជនថ្មី")
            
            if submit_reg:
                if new_name.strip():
                    save_new_customer(id_user, new_name.strip())
                    st.success(f"🎉 បានចុះឈ្មោះ {new_name} រួចរាល់! កម្មវិធីនឹងរៀបចំទិន្នន័យឡើងវិញ...")
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

# --- ផ្នែកទូទាត់ប្រាក់សរុប ---
st.header("💰 ផ្នែកទូទាត់ប្រាក់សរុប")
room_fee = st.number_input("ថ្លៃបន្ទប់ (រៀល) =", value=0.0, key="room_fee")
debt_electric = st.number_input("ប្រាក់ជំពាក់ (រៀល) =", value=0.0, key="debt_elec")

total_money = st.session_state['total_electric'] + st.session_state['total_water'] + room_fee + debt_electric

st.success(f"💵 Total ទឹកប្រាក់សរុបនៅថ្ងៃនេះ (រួមទាំងថ្លៃបន្ទប់ និងប្រាក់ជំពាក់)៖ {total_money} ៛")

if st.button("💾 រក្សាទុកការកត់ត្រានេះ"):
    if id_user and customer_name:
        log_data(
            id_user, customer_name, date_line, 
            old_num_electric, new_num_electric, st.session_state['total_electric'],
            old_num_water, new_num_water, st.session_state['total_water'],
            room_fee, debt_electric, total_money,
            st.session_state['current_user'] # បញ្ជូនឈ្មោះអ្នកកត់ត្រាទុក
        )
        st.toast("✅ បានកត់ត្រាទិន្នន័យចូលក្នុងប្រព័ន្ធជោគជ័យ!")
    else:
        st.error("❌ មិនអាចកត់ត្រាបានទេ! សូមប្រាកដថាបានបំពេញ ID និងចុះឈ្មោះអតិថិជនរួចរាល់។")

st.divider()

# --- ប៊ូតុងព្រីន ---
print_btn = """
<button onclick="window.parent.print()" style="
    background-color: #4CAF50; border: none; color: white; padding: 10px 24px;
    text-align: center; text-decoration: none; display: inline-block;
    font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px;
">Print វិក្កយបត្រ</button>
"""
components.html(print_btn, height=60)


# =========================================================
# 🛠️ ផ្នែកទី ៣៖ ការបង្ហាញទិន្នន័យ និងប្រព័ន្ធលុបទិន្នន័យដោយប្រើ Password
# =========================================================
no_print_area = st.container()
with no_print_area:
    st.html("<style>@media print { div[data-testid='stVerticalBlock'] > div:last-child { display: none !important; } }</style>")
    
    st.divider()
    st.subheader("📋 ប្រវត្តិនៃការកត់ត្រាទិន្នន័យកន្លងមក")
    if os.path.exists(LOG_FILE):
        try:
            df_logs = pd.read_csv(LOG_FILE)
            st.dataframe(df_logs)
        except Exception:
            st.error("⚠️ ឯកសារប្រវត្តិកត់ត្រាចាស់មានទម្រង់ខូចខាត។")
    else:
        st.info("មិនទាន់មានទិន្នន័យកត់ត្រានៅឡើយទេ។")
        
    # --- ⚙️ ផ្ទាំងបញ្ជាលុបទិន្នន័យ (Admin Control) ---
    st.sidebar.divider()
    st.sidebar.subheader("⚙️ ផ្នែកលុបទិន្នន័យ (Admin)")
    
    del_password = st.sidebar.text_input("បញ្ចូលពាក្យសម្ងាត់ Admin ដើម្បីលុប៖", type="password")
    
    if st.sidebar.button("🗑️ លុបប្រវត្តិនៃការកត់ត្រាទាំងអស់"):
        if del_password == ADMIN_PASSWORD:
            if os.path.exists(LOG_FILE):
                os.remove(LOG_FILE)
                st.sidebar.success("🗑️ បានលុបប្រវត្តិកត់ត្រាទាំងអស់ដោយជោគជ័យ!")
                st.rerun()
            else:
                st.sidebar.info("គ្មានប្រវត្តិកត់ត្រាដែលត្រូវលុបទេ។")
        else:
            st.sidebar.error("❌ ពាក្យសម្ងាត់មិនត្រឹមត្រូវទេ!")

    if st.sidebar.button("👥 លុបទិន្នន័យអតិថិជនទាំងអស់"):
        if del_password == ADMIN_PASSWORD:
            if os.path.exists(CUSTOMER_FILE):
                os.remove(CUSTOMER_FILE)
                st.sidebar.success("🗑️ បានលុបទិន្នន័យអតិថិជនទាំងអស់ជោគជ័យ!")
                st.rerun()
            else:
                st.sidebar.info("គ្មានទិន្នន័យអតិថិជនដែលត្រូវលុបទេ។")
        else:
            st.sidebar.error("❌ ពាក្យសម្ងាត់មិនត្រឹមត្រូវទេ!")
