import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
from datetime import datetime

USER_ACCOUNTS = {
    "admin": "admin123",
    "staff1": "staff123",
    "staff2": "staff2026"
}
ADMIN_PASSWORD = "admin123" 

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = ""
if 'total_electric' not in st.session_state:
    st.session_state['total_electric'] = 0
if 'total_water' not in st.session_state:
    st.session_state['total_water'] = 0

if 'elec_old_val' not in st.session_state:
    st.session_state['elec_old_val'] = 0
if 'water_old_val' not in st.session_state:
    st.session_state['water_old_val'] = 0

if 'widget_key_trigger' not in st.session_state:
    st.session_state['widget_key_trigger'] = 0

if 'input_key_suffix' not in st.session_state:
    st.session_state['input_key_suffix'] = 0

CUSTOMER_FILE = "customers.csv"
LOG_FILE = "invoice_logs.csv"
EXPENSE_FILE = "expenses.csv"

# --- អនុគមន៍ជំនួយគណនាតម្លៃតាមជណ្តើរ ---
def calculate_utility_fee(used_units):
    if used_units <= 0:
        return 0
    elif used_units <= 100:
        return int(used_units * 650)
    elif used_units <= 1000:
        return int(used_units * 800)
    else:
        return int(used_units * 1000)

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

def delete_single_customer(user_id):
    if os.path.exists(CUSTOMER_FILE):
        try:
            df = pd.read_csv(CUSTOMER_FILE, dtype={'User ID': str})
            df = df[df['User ID'] != str(user_id)]
            df.to_csv(CUSTOMER_FILE, index=False, encoding='utf-8-sig')
            return True
        except Exception:
            pass
    return False

def get_last_utility_readings(user_id):
    last_electric_new = 0
    last_water_new = 0
    if os.path.exists(LOG_FILE):
        try:
            df = pd.read_csv(LOG_FILE, dtype=str, on_bad_lines='skip')
            df.columns = df.columns.str.strip()
            id_col = 'User ID' if 'User ID' in df.columns else (df.columns[1] if len(df.columns) > 1 else None)
            if id_col:
                user_logs = df[df[id_col].str.strip() == str(user_id).strip()]
                if not user_logs.empty:
                    latest_row = user_logs.iloc[-1]
                    if 'Electric New' in latest_row and pd.notna(latest_row['Electric New']):
                        last_electric_new = int(float(latest_row['Electric New']))
                    if 'Water New' in latest_row and pd.notna(latest_row['Water New']):
                        last_water_new = int(float(latest_row['Water New']))
        except Exception:
            pass
    return last_electric_new, last_water_new

def log_data(user_id, user_name, date_line, elec_old, elec_new, elec_total, water_old, water_new, water_total, room_fee, parking_fee, grand_total, created_by):
    new_data = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Month": datetime.now().strftime("%Y-%m"),
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
            df_new.to_csv(LOG_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
        except Exception:
            df_new.to_csv(LOG_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(LOG_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')

def log_expense(title, amount, created_by):
    new_expense = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Month": datetime.now().strftime("%Y-%m"),
        "Expense Title": title,
        "Amount (៛)": int(amount),
        "Recorded By": created_by
    }
    df_new = pd.DataFrame([new_expense])
    if os.path.exists(EXPENSE_FILE):
        df_new.to_csv(EXPENSE_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(EXPENSE_FILE, mode='w', header=True, index=False, encoding='utf-8-sig')

def delete_single_log(timestamp):
    if os.path.exists(LOG_FILE):
        try:
            df = pd.read_csv(LOG_FILE, dtype=str)
            df = df[df['Timestamp'] != timestamp]
            df.to_csv(LOG_FILE, index=False, encoding='utf-8-sig')
            return True
        except Exception:
            pass
    return False

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
if st.sidebar.button("🚪 ចាកចេញ (Logout)"):
    st.session_state['logged_in'] = False
    st.session_state['current_user'] = ""
    st.rerun()

# ម៉ឺនុយសម្រាប់ជ្រើសរើសផ្នែកការងារ
menu = st.sidebar.selectbox("📂 ជ្រើសរើសផ្នែកការងារ", ["🧮 គណនាវិក្កយបត្រ", "📉 កត់ត្រាការចំណាយ", "📊 របាយការណ៍ និងប្រាក់ចំណេញ"])

# =========================================================
# 🍏 ផ្នែកកម្មវិធីចម្បង៖ គណនាវិក្កយបត្រ
# =========================================================
if menu == "🧮 គណនាវិក្កយបត្រ":
    st.title("🍏 ⚡ ប្រព័ន្ធគណនាទិន្នន័យ ទឹក-អគ្គសនី")
    st.write("សូមបំពេញព័ត៌មានខាងក្រោមដើម្បីគណនាថ្លៃប្រាក់")
    st.divider()

    suffix = st.session_state['input_key_suffix']
    trigger = st.session_state['widget_key_trigger']

    id_user = st.text_input("បញ្ចូល ID របស់អ្នក:", key=f"id_{suffix}").strip()
    customer_name = ""

    if id_user:
        existing_name = get_customer_name(id_user)
        if existing_name:
            st.success(f"👤 ឈ្មោះអតិថិជន៖ {existing_name}")
            customer_name = existing_name
            
            if 'last_checked_id' not in st.session_state or st.session_state['last_checked_id'] != id_user:
                e_old, w_old = get_last_utility_readings(id_user)
                st.session_state['elec_old_val'] = e_old
                st.session_state['water_old_val'] = w_old
                st.session_state['last_checked_id'] = id_user
                st.session_state['widget_key_trigger'] += 1
                st.rerun()
        else:
            st.warning(f"⚠️ មិនទាន់មាន ID [{id_user}] នេះក្នុងប្រព័ន្ធទេ។")
            with st.form("customer_registration_form"):
                new_name = st.text_input("បញ្ចូល ឈ្មោះអតិថិជនថ្មី:")
                if st.form_submit_button("💾 ចុះឈ្មោះអតិថិជនថ្មី") and new_name.strip():
                    save_new_customer(id_user, new_name.strip())
                    st.rerun()

    date_line = st.text_input("កាលបរិច្ឆេទ (Date Line):", key=f"date_{suffix}", value=datetime.now().strftime("%d-%m-%Y"))
    st.divider()

    # --- ⚡ ផ្នែកគណនាថ្លៃអគ្គសនី ---
    st.header("⚡ គណនាថ្លៃអគ្គសនី")
    old_num_electric = st.number_input("លេខថាមពលចាស់ (ភ្លើង) =", value=int(st.session_state['elec_old_val']), step=1, format="%d", key=f"old_elec_{suffix}_{trigger}")
    new_num_electric = st.number_input("លេខថាមពលថ្មី (ភ្លើង) =", value=0, step=1, format="%d", key=f"new_elec_{suffix}_{trigger}")

    used_electric = new_num_electric - old_num_electric
    if st.button("គណនាថ្លៃអគ្គសនី"):
        st.session_state['total_electric'] = calculate_utility_fee(used_electric)
        st.info(f"💵 ប្រើប្រាស់អស់: {used_electric} kWh | ទឹកប្រាក់ថ្លៃភ្លើងសរុប៖ {int(st.session_state['total_electric']):,} ៛")

    st.divider()

    # --- 💧 ផ្នែកគណនាថ្លៃទឹក ---
    st.header("💧 គណនាថ្លៃទឹកស្អាត")
    old_num_water = st.number_input("លេខនាឡិកាចាស់ (ទឹក) =", value=int(st.session_state['water_old_val']), step=1, format="%d", key=f"old_water_{suffix}_{trigger}")
    new_num_water = st.number_input("លេខនាឡិកាថ្មី (ទឹក) =", value=0, step=1, format="%d", key=f"new_water_{suffix}_{trigger}")

    used_water = new_num_water - old_num_water
    if st.button("គណនាថ្លៃទឹក"):
        st.session_state['total_water'] = calculate_utility_fee(used_water)
        st.info(f"💵 ប្រើប្រាស់អស់: {used_water} m³ | ទឹកប្រាក់ថ្លៃទឹកសរុប៖ {int(st.session_state['total_water']):,} ៛")

    st.divider()

    # --- 💰 ផ្នែកទូទាត់ប្រាក់រួមបញ្ចូល ---
    st.header("💰 ផ្នែកទូទាត់ប្រាក់សរុប")
    room_fee = st.number_input("ថ្លៃបន្ទប់/ផ្ទះ (រៀល) =", value=0, step=1, format="%d", key=f"room_{suffix}")
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
            
            st.session_state['total_electric'] = 0
            st.session_state['total_water'] = 0
            st.session_state['elec_old_val'] = 0
            st.session_state['water_old_val'] = 0
            if 'last_checked_id' in st.session_state:
                del st.session_state['last_checked_id']
            st.session_state['input_key_suffix'] += 1 
            st.rerun()
        else:
            st.error("❌ សូមប្រាកដថាបានបញ្ចូល ID និងមានឈ្មោះអតិថិជនត្រឹមត្រូវ។")

    st.divider()

    # --- 🖨️ ផ្នែកទម្រង់បង្ហាញសម្រាប់ព្រីនវិក្កយបត្រ (Invoice Print Layout) ---
    st.subheader("🖨️ ទម្រង់សម្រាប់បោះពុម្ពវិក្កយបត្រ")
    
    invoice_template = f"""
    <div style="font-family: 'Khmer OS Battambang', Arial, sans-serif; padding: 20px; border: 1px solid #ccc; max-width: 450px; background-color: #fff; color: #000; line-height: 1.8;">
        <h3 style="text-align: center; margin-top: 0;">វិក្កយបត្រប្រចាំខែ</h3>
        <hr style="border: 0.5px solid #000;">
        <div><strong>ជួរទី១៖</strong> {id_user} &nbsp;&nbsp;&nbsp;&nbsp; {customer_name if customer_name else '......................'}</div>
        <div><strong>ជួរទី២៖</strong> លេខភ្លើងចាស់: {old_num_electric} &nbsp;&nbsp; លេខភ្លើងថ្មី: {new_num_electric} &nbsp;&nbsp; ប្រើប្រាស់សរុប: {used_electric} kWh</div>
        <div><strong>ជួរទីបី៖</strong> ប្រាក់ថ្លៃភ្លើងសរុប: {int(st.session_state['total_electric']):,} ៛</div>
        <div><strong>ជួរទីបួន៖</strong> លេខទឹកចាស់: {old_num_water} &nbsp;&nbsp; លេខទឹកថ្មី: {new_num_water} &nbsp;&nbsp; ប្រើប្រាស់សរុប: {used_water} m³</div>
        <div><strong>ជួរទីប្រាំ៖</strong> ប្រាក់ថ្លៃទឹកសរុប: {int(st.session_state['total_water']):,} ៛</div>
        <div><strong>ជួរបន្ទាប់៖</strong> ថ្លៃផ្ទះ: {int(room_fee):,} ៛ &nbsp;&nbsp; ថ្លៃចំណត: {int(parking_fee):,} ៛ &nbsp;&nbsp; ប្រាក់សរុបរួម: <span style="font-weight: bold; font-size: 1.1em;">{total_money:,} ៛</span></div>
        <hr style="border: 0.5px dashed #000;">
        <div style="text-align: center; font-size: 12px;">កាលបរិច្ឆេទបញ្ចេញវិក្កយបត្រ៖ {date_line}</div>
    </div>
    """
    
    st.components.v1.html(invoice_template, height=320)

    print_btn = """
    <button onclick="window.parent.print()" style="
        background-color: #4CAF50; border: none; color: white; padding: 10px 24px;
        text-align: center; text-decoration: none; display: inline-block;
        font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px;
    ">🖨️ ចុចព្រីន (Print វិក្កយបត្រ)</button>
    """
    components.html(print_btn, height=60)

    # ផ្នែកគ្រប់គ្រងទិន្នន័យ (លាក់ពេលព្រីន)
    no_print_area = st.container()
    with no_print_area:
        st.html("<style>@media print { div[data-testid='stVerticalBlock'] > div:last-child, button, header, footer { display: none !important; } }</style>")
        st.divider()
        st.subheader("📋 ប្រវត្តិនៃការកត់ត្រាទិន្នន័យកន្លងមក")
        
        if os.path.exists(LOG_FILE):
            try:
                df_logs = pd.read_csv(LOG_FILE, dtype=str, on_bad_lines='skip')
                st.dataframe(df_logs)
                
                st.write("🔧 **ជ្រើសរើសលុបទិន្នន័យកត់ត្រាណាមួយចោល៖**")
                log_timestamps = df_logs['Timestamp'].tolist() if 'Timestamp' in df_logs.columns else []
                selected_log = st.selectbox("ជ្រើសរើស ថ្ងៃខែខ្សែកត់ត្រា ដែលចង់លុប៖", ["--- សូមជ្រើសរើស ---"] + log_timestamps)
                
                if selected_log != "--- សូមជ្រើសរើស ---":
                    log_password = st.text_input("បញ្ចូលពាក្យសម្ងាត់ Admin ដើម្បីលុបប្រវត្តិនេះ៖", type="password", key="p_log")
                    if st.button("🗑️ លុបប្រវត្តិនេះចោល"):
                        if log_password == ADMIN_PASSWORD:
                            if delete_single_log(selected_log):
                                st.success(f"✅ បានលុបប្រវត្តិកត់ត្រារួចរាល់!")
                                st.rerun()
                        else:
                            st.error("❌ ពាក្យសម្ងាត់មិនត្រឹមត្រូវទេ!")
            except Exception:
                st.error("⚠️ ឯកសារប្រវត្តិកត់ត្រាចាស់មានទម្រង់ខូចខាតខ្លាំង។")

# =========================================================
# 📉 ផ្នែកកម្មវិធី៖ កត់ត្រាការចំណាយ (Expense)
# =========================================================
elif menu == "📉 កត់ត្រាការចំណាយ":
    st.title("📉 ផ្នែកកត់ត្រាការចំណាយផ្សេងៗ")
    st.write("បំពេញទិន្នន័យចំណាយរបស់អគារ ឬផ្ទះជួលនៅទីនេះ")
    st.divider()

    with st.form("expense_form"):
        expense_title = st.text_input("ពិពណ៌នាការចំណាយ (ឧទាហរណ៍៖ ថ្លៃជួសជុលអំពូល, ថ្លៃទិញសម្ភារៈ...):")
        expense_amount = st.number_input("ចំនួនទឹកប្រាក់ចំណាយ (រៀល) =", value=0, step=100, format="%d")
        
        if st.form_submit_button("💾 រក្សាទុកការចំណាយ"):
            if expense_title.strip() and expense_amount > 0:
                log_expense(expense_title.strip(), expense_amount, st.session_state['current_user'])
                st.success("✅ បានកត់ត្រាការចំណាយរួចរាល់!")
            else:
                st.error("❌ សូមបំពេញព័ត៌មានចំណាយឱ្យបានត្រឹមត្រូវ។")

    st.subheader("📋 បញ្ជីប្រវត្តិចំណាយកន្លងមក")
    if os.path.exists(EXPENSE_FILE):
        df_exp = pd.read_csv(EXPENSE_FILE)
        st.dataframe(df_exp)
    else:
        st.info("មិនទាន់មានប្រវត្តិចំណាយនៅឡើយទេ។")

# =========================================================
# 📊 ផ្នែកកម្មវិធី៖ របាយការណ៍ និងប្រាក់ចំណេញ (Report Dashboard)
# =========================================================
elif menu == "📊 របាយការណ៍ និងប្រាក់ចំណេញ":
    st.title("📊 របាយការណ៍ហិរញ្ញវត្ថុ និងប្រាក់ចំណេញប្រចាំខែ")
    st.write("ទិន្នន័យគណនាដោយស្វ័យប្រវត្តិចេញពីប្រព័ន្ធលក់ និងការចំណាយ")
    st.divider()

    # ទាញយកទិន្នន័យចំណូល
    total_income_dict = {}
    if os.path.exists(LOG_FILE):
        df_logs = pd.read_csv(LOG_FILE)
        if 'Month' in df_logs.columns and 'Grand Total (៛)' in df_logs.columns:
            df_income_grouped = df_logs.groupby('Month')['Grand Total (៛)'].sum().reset_index()
            for idx, row in df_income_grouped.iterrows():
                total_income_dict[row['Month']] = row['Grand Total (៛)']

    # ទាញយកទិន្នន័យចំណាយ
    total_expense_dict = {}
    if os.path.exists(EXPENSE_FILE):
        df_exp = pd.read_csv(EXPENSE_FILE)
        if 'Month' in df_exp.columns and 'Amount (៛)' in df_exp.columns:
            df_exp_grouped = df_exp.groupby('Month')['Amount (៛)'].sum().reset_index()
            for idx, row in df_exp_grouped.iterrows():
                total_expense_dict[row['Month']] = row['Amount (៛)']

    # រៀបចំបង្កើតតារាងរបាយការណ៍រួមសរុប (Merged Months)
    all_months = sorted(list(set(list(total_income_dict.keys()) + list(total_expense_dict.keys()))))
    
    report_data = []
    for m in all_months:
        income = total_income_dict.get(m, 0)
        expense = total_expense_dict.get(m, 0)
        profit = income - expense
        report_data.append({
            "ខែ-ឆ្នាំ (Month)": m,
            "ចំណូលសរុប (៛)": income,
            "ចំណាយសរុប (៛)": expense,
            "ប្រាក់ចំណេញដាច់ (៛)": profit
        })

    if report_data:
        df_report = pd.DataFrame(report_data)
        
        # បង្ហាញជាផ្ទាំងលេចធ្លោ (Metrics Layout)
        latest_row = df_report.iloc[-1]
        st.subheader(f"📈 សង្ខេបស្ថានភាពហិរញ្ញវត្ថុក្នុងខែចុងក្រោយ ({latest_row['ខែ-ឆ្នាំ (Month)']})")
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 ចំណូលសរុប", f"{latest_row['ចំណូលសរុប (៛)']:,} ៛")
        col2.metric("📉 ចំណាយសរុប", f"- {latest_row['ចំណាយសរុប (៛)']:,} ៛")
        col3.metric("🍏 ប្រាក់ចំណេញ", f"{latest_row['ប្រាក់ចំណេញដាច់ (៛)']:,} ៛")
        
        st.divider()
        st.subheader("📋 តារាងប្រៀបធៀបប្រចាំខែទាំងអស់")
        st.dataframe(df_report.style.format({
            "ចំណូលសរុប (៛)": "{:,.0f} ៛",
            "ចំណាយសរុប (៛)": "{:,.0f} ៛",
            "ប្រាក់ចំណេញដាច់ (៛)": "{:,.0f} ៛"
        }))
    else:
        st.info("មិនទាន់មានទិន្នន័យគ្រប់គ្រាន់ដើម្បីបង្កើតរបាយការណ៍ហិរញ្ញវត្ថុនៅឡើយទេ។")
