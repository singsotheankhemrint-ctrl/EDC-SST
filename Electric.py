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
ADMIN_PASSWORD = "admin123" 

# --- បង្កើត Session State សម្រាប់រក្សាទុកតម្លៃបណ្តោះអាសន្ន ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = ""
if 'total_electric' not in st.session_state:
    st.session_state['total_electric'] = 0
if 'total_water' not in st.session_state:
    st.session_state['total_water'] = 0

# បង្កើតតម្លៃសម្រាប់ចាប់ទិន្នន័យលេខចាស់កុំឱ្យបាត់បង់
if 'elec_old_val' not in st.session_state:
    st.session_state['elec_old_val'] = 0
if 'water_old_val' not in st.session_state:
    st.session_state['water_old_val'] = 0
if 'last_checked_id' not in st.session_state:
    st.session_state['last_checked_id'] = ""

# បង្កើត key សម្រាប់គ្រប់គ្រងការ Reset ប្រអប់បញ្ចូលទិន្នន័យ
if 'input_key_suffix' not in st.session_state:
    st.session_state['input_key_suffix'] = 0

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

# --- 🛠️ មុខងារទាញយកលេខថ្មីពីរបាយការណ៍ចាស់ (អានតាមឈ្មោះជួរឈរ ឬតាមលំដាប់លំដាប់លំដោយកូដ) ---
def get_last_utility_readings(user_id):
    last_electric_new = 0
    last_water_new = 0
    if os.path.exists(LOG_FILE):
        try:
            df = pd.read_csv(LOG_FILE, dtype=str, on_bad_lines='skip')
            df.columns = df.columns.str.strip()
            
            id_col = 'User ID' if 'User ID' in df.columns else (df.columns[1] if len(df.columns) > 1 else None)
            
            if id_col:
                user_logs = df[df[id_col] == str(user_id)]
                if not user_logs.empty:
                    latest_row = user_logs.iloc[-1]
                    
                    # ស្វែងរកលេខភ្លើងថ្មីចុងក្រោយ
                    if 'Electric New' in latest_row and pd.notna(latest_row['Electric New']):
                        last_electric_new = int(float(latest_row['Electric New']))
                    elif len(df.columns) > 5:
                        last_electric_new = int(float(latest_row.iloc[5]))
                        
                    # ស្វែងរកលេខទឹកថ្មីចុងក្រោយ
                    if 'Water New' in latest_row and pd.notna(latest_row['Water New']):
                        last_water_new = int(float(latest_row['Water New']))
                    elif len(df.columns) > 8:
                        last_water_new = int(float(latest_row.iloc[8]))
        except Exception:
            pass
    return last_electric_new, last_water_new

# --- អនុគមន៍កត់ត្រាទិន្នន័យ ---
def log_data(user_id, user_name, date_line, elec_old, elec_new, elec_total, water_old, water_new, water_total, room_fee, parking_fee, grand_total, created_by):
    new_data = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "User ID": str(user_id),
        "Customer Name": user_name,
        "Date Line": date_line,
        "Electric Old": int(elec_old),
        "Electric New": int(elec_new),
        "Electric Total (៛)": int(elec_total),
        "Water Old": int(water_old),
        "Water New": int(water_new),
        "Water Total (៛)": int(water_total),
        "Room Fee (៛)": int(room_fee),
        "Parking Fee (៛)": int(parking_fee),
        "Grand Total (៛)": int(grand_total),
        "Recorded By": created_by
    }
    df_new = pd.DataFrame([new_data])
    if os.path.exists(LOG_FILE):
        try:
            df_existing = pd.read_csv(LOG_FILE, nrows=0)
            if len(df_existing.columns) != len(df_new.columns):
                df_new.to_csv(LOG_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')
            else:
                df_new.to_csv(LOG_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
        except Exception:
            df_new.to_csv(LOG_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(LOG_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')


# =========================================================
# 🔐 ផ្នែកប្រព័ន្ធ LOGIN
# =========================================================
if not st.session_state['logged_in']:
    st.subheader("🔐 សូមចូលប្រើប្រាស់ប្រព័ន្ធ (Login)")
    username_input = st.text_input("ឈ្មោះគណនី (Username):")
    password_input = st.text_input("ពាក្យសម្ងាត់ (Password):", type="password")
    if st.button("🔑 ចូលប្រើប្រាស់"):
        if username_input in USER_ACCOUNTS and USER_ACCOUNTS[username_input] == password_input:
            st.session_state['logged_in'] = True
            st.session_state['current_user'] = username_input
            st.rerun()
        else:
            st.error("❌ ឈ្មោះគណនី ឬពាក្យសម្ងាត់មិនត្រឹមត្រូវទេ!")
    st.stop()

st.sidebar.write(f"👤 គណនី៖ **{st.session_state['current_user']}**")


# =========================================================
# 🍏 ផ្នែកកម្មវិធីចម្បង
# =========================================================
st.title("🍏 ⚡ ប្រព័ន្ធគណនាទិន្នន័យ ទឹក-អគ្គសនី")
st.write("សូមបំពេញព័ត៌មានខាងក្រោមដើម្បីគណនាថ្លៃប្រាក់")
st.divider()

suffix = st.session_state['input_key_suffix']

# --- ផ្នែកព័ត៌មានអតិថិជន ---
id_user = st.text_input("បញ្ចូល ID របស់អ្នក:", key=f"id_{suffix}").strip()
customer_name = ""

# 🔥 យុទ្ធសាស្ត្រថ្មី៖ បើ ID មានការប្រែប្រួល ឱ្យទៅអូសទាញទិន្នន័យពីឯកសារចាស់ភ្លាមៗ
if id_user and id_user != st.session_state['last_checked_id']:
    existing_name = get_customer_name(id_user)
    if existing_name:
        e_old, w_old = get_last_utility_readings(id_user)
        st.session_state['elec_old_val'] = e_old
        st.session_state['water_old_val'] = w_old
        st.session_state['last_checked_id'] = id_user
        st.rerun() # បង្ខំឱ្យកម្មវិធី Refresh ទំព័រដើម្បីចាប់តម្លៃចូល Number Input ភ្លាម

if id_user:
    existing_name = get_customer_name(id_user)
    if existing_name:
        st.success(f"👤 ឈ្មោះអតិថិជន៖ {existing_name}")
        customer_name = existing_name
    else:
        st.warning(f"⚠️ មិនទាន់មាន ID [{id_user}] នេះក្នុងប្រព័ន្ធទេ។")
        with st.form("customer_registration_form"):
            new_name = st.text_input("បញ្ចូល ឈ្មោះអតិថិជនថ្មី:")
            if st.form_submit_button("💾 ចុះឈ្មោះអតិថិជនថ្មី") and new_name.strip():
                save_new_customer(id_user, new_name.strip())
                st.rerun()

date_line = st.text_input("កាលបរិច្ឆេទ (Date Line):", key=f"date_{suffix}")
st.divider()

# --- ⚡ ផ្នែកគណនាថ្លៃអគ្គសនី ---
st.header("⚡ គណនាថ្លៃអគ្គសនី")
# តម្លៃចាស់ នឹងទាញចេញពី state ដែលយើងបានទាញពី file មករុញបញ្ចូលផ្ទាល់តែម្តង
old_num_electric = st.number_input("លេខថាមពលចាស់ (ភ្លើង) =", value=int(st.session_state['elec_old_val']), step=1, format="%d", key=f"old_elec_{suffix}")
new_num_electric = st.number_input("លេខថាមពលថ្មី (ភ្លើង) =", value=0, step=1, format="%d", key=f"new_elec_{suffix}")

used_electric = new_num_electric - old_num_electric
if st.button("គណនាថ្លៃអគ្គសនី"):
    st.session_state['total_electric'] = 500 if used_electric <= 0 else int(used_electric * 1000)
    st.info(f"💵 ទឹកប្រាក់ថ្លៃភ្លើងសរុប៖ {int(st.session_state['total_electric']):,} ៛")

st.divider()

# --- 💧 ផ្នែកគណនាថ្លៃទឹក ---
st.header("💧 គណនាថ្លៃទឹកស្អាត")
# តម្លៃចាស់ ទឹកក៏ទាញចេញពី state ដូចគ្នា
old_num_water = st.number_input("លេខនាឡិកាចាស់ (ទឹក) =", value=int(st.session_state['water_old_val']), step=1, format="%d", key=f"old_water_{suffix}")
new_num_water = st.number_input("លេខនាឡិកាថ្មី (ទឹក) =", value=0, step=1, format="%d", key=f"new_water_{suffix}")

used_water = new_num_water - old_num_water
if st.button("គណនាថ្លៃទឹក"):
    st.session_state['total_water'] = int(used_water * 2000)
    st.info(f"💵 ទឹកប្រាក់ថ្លៃទឹកសរុប៖ {int(st.session_state['total_water']):,} ៛")

st.divider()

# --- 💰 ផ្នែកទូទាត់ប្រាក់រួមបញ្ចូល ---
st.header("💰 ផ្នែកទូទាត់ប្រាក់សរុប")
room_fee = st.number_input("ថ្លៃបន្ទប់ (រៀល) =", value=0, step=1, format="%d", key=f"room_{suffix}")
parking_fee = st.number_input("ថ្លៃចំណត (រៀល) =", value=0, step=1, format="%d", key=f"parking_{suffix}")

total_money = int(st.session_state['total_electric']) + int(st.session_state['total_water']) + int(room_fee) + int(parking_fee)
st.success(f"💵 Total ទឹកប្រាក់សរុបនៅថ្ងៃនេះ៖ {total_money:,} ៛")

if st.button("💾 រក្សាទុកការកត់ត្រានេះ"):
    if id_user and customer_name:
        log_data(
            id_user, customer_name, date_line, 
            old_num_electric, new_num_electric, st.session_state['total_electric'], 
            old_num_water, new_num_water, st.session_state['total_water'], 
            room_fee, parking_fee, total_money, st.session_state['current_user']
        )
        st.success("✅ បានកត់ត្រាទិន្នន័យរួចរាល់!")
        
        # សំអាតតម្លៃចាស់ចោលដើម្បីរង់ចាំបញ្ចូល ID បន្ទាប់
        st.session_state['total_electric'] = 0
        st.session_state['total_water'] = 0
        st.session_state['elec_old_val'] = 0
        st.session_state['water_old_val'] = 0
        st.session_state['last_checked_id'] = ""
        st.session_state['input_key_suffix'] += 1 
        st.rerun()
