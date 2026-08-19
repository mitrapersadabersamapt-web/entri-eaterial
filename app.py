import json
import pandas as pd
import requests
import streamlit as st

# Config Halaman
st.set_page_config(
    page_title="Sistem Entri Material PLN",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# CUSTOM CSS UNTUK TAMPILAN CERAH & KONTRAS
# ==========================================
st.markdown(
    """
    <style>
    /* Background Utama Bersih & Cerah */
    .stApp {
        background-color: #f4f7fa;
    }
    
    /* Header Banner PLN */
    .pln-header {
        background: linear-gradient(135deg, #005691 0%, #0080ff 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 25px;
    }
    .pln-header h1 {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        margin: 0;
        font-size: 32px;
    }
    .pln-header p {
        color: #FFE600 !important;
        margin: 4px 0 0 0;
        font-weight: 600;
    }

    /* Label Input Lebih Jelas & Bold */
    label, .stSelectbox label, .stTextInput label, .stNumberInput label {
        color: #1e293b !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }

    /* Style Input Box (Border & BG) */
    .stTextInput input, .stTextArea textarea, .stSelectbox > div > div, .stNumberInput input {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    /* Subheader Styling */
    .section-title {
        color: #0f172a;
        font-weight: 700;
        font-size: 20px;
        margin-bottom: 15px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
    }

    /* Card Total Estimasi */
    .total-box {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 2px solid #f59e0b;
        padding: 18px 24px;
        border-radius: 12px;
        text-align: left;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    .total-title {
        color: #b45309;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .total-amount {
        color: #78350f;
        font-size: 32px;
        font-weight: 800;
        margin-top: 4px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# URL GOOGLE APPS SCRIPT WEBHOOK ANDA
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyyDW104My3hp0fnW-KLQOWyIkVBSZ4iQu1wXA9fH6Kw8P942IF1f5Hi-Tjf5lTYL-U/exec"


# ==========================================
# 1. LOAD & CLEANING MASTER DATABASE EXCEL
# ==========================================
@st.cache_data
def load_and_clean_master(filepath):
    df = pd.read_excel(filepath, sheet_name="HEADER APLIKASI", header=5)

    string_cols = ["JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    numeric_cols = ["HARGA MATERIAL", "JASA PASANG", "JASA BONGKAR"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    return df


try:
    df_master = load_and_clean_master("MATERIAL 1.xlsx")
except Exception:
    try:
        df_master = load_and_clean_master("MATERIAL 1_2.xlsx")
    except Exception:
        df_master = load_and_clean_master("MATERIAL 1_3.xlsx")

# ==========================================
# 2. SESSION STATE MANAGEMENT
# ==========================================
if "keranjang" not in st.session_state:
    st.session_state.keranjang = []

if "pesan_sukses" not in st.session_state:
    st.session_state.pesan_sukses = False

# BANNER HEADER
st.markdown(
    """
    <div class="pln-header">
        <h1>⚡ SISTEM ENTRI MATERIAL PLN</h1>
        <p>Aplikasi Input Rekap Material & Estimasi Biaya Pekerjaan</p>
    </div>
""",
    unsafe_allow_html=True,
)

if st.session_state.pesan_sukses:
    st.success("🎉 **SELAMAT! DATA BERHASIL DIKIRIM KE GOOGLE SHEET**")
    st.balloons()
    st.session_state.pesan_sukses = False

# ==========================================
# 3. BAGIAN 1: HEADER PEKERJAAN
# ==========================================
st.markdown('<div class="section-title">1. Header Data Pekerjaan</div>', unsafe_allow_html=True)

col_h1, col_h2 = st.columns(2)

with col_h1:
    nama_pekerjaan = st.text_input(
        "NAMA PEKERJAAN :", placeholder="Masukkan Nama Pekerjaan (misal: PERUBAHAN DAYA)"
    )
    alamat_pekerjaan = st.text_area(
        "ALAMAT PEKERJAAN :", placeholder="Masukkan Alamat Lengkap Pekerjaan..."
    )

with col_h2:
    jenis_pekerjaan = st.selectbox(
        "JENIS PEKERJAAN :",
        ["SAR", "PFK", "PREVENTIF", "KEYPOINT", "PEMELIHARAAN JARINGAN"],
    )
    tanggal = st.date_input("TANGGAL :")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 4. BAGIAN 2: FORM INPUT MATERIAL
# ==========================================
st.markdown('<div class="section-title">2. Form Input Material Pekerjaan</div>', unsafe_allow_html=True)

list_jenis = sorted(df_master["JENIS KONSTRUKSI"].unique().tolist())
jenis_selected = st.selectbox("1. Pilih Jenis Konstruksi:", list_jenis)

df_filtered_jenis = df_master[df_master["JENIS KONSTRUKSI"] == jenis_selected]

col_f1, col_f2 = st.columns(2)

with col_f1:
    list_type = sorted(df_filtered_jenis["TYPE KONSTRUKSI"].unique().tolist())
    type_selected = st.selectbox("2. Pilih Type Konstruksi:", list_type)

df_filtered_type = df_filtered_jenis[
    df_filtered_jenis["TYPE KONSTRUKSI"] == type_selected
]
list_mat_all = sorted(df_filtered_type["NAMA MATERIAL"].unique().tolist())

with col_f2:
    material_selected = st.selectbox(
        "3. Pilih / Cari Nama Material:",
        list_mat_all,
        help="Ketik langsung kata kunci material pada kotak untuk mencari.",
    )

col_v1, col_v2, col_v3, col_v4 = st.columns([1, 1, 1, 1.3])

with col_v1:
    vol_mat_default = st.number_input("Volume Material", min_value=0, value=1, step=1)
with col_v2:
    vol_pasang_default = st.number_input("Volume Pasang", min_value=0, value=1, step=1)
with col_v3:
    vol_bongkar_default = st.number_input("Volume Bongkar", min_value=0, value=0, step=1)


def tambah_ke_keranjang():
    item_baru = {
        "Jenis Konstruksi": jenis_selected,
        "Type Konstruksi": type_selected,
        "Material": material_selected,
        "Volume Material": int(vol_mat_default),
        "Volume Pasang": int(vol_pasang_default),
        "Volume Bongkar": int(vol_bongkar_default),
    }
    st.session_state.keranjang.append(item_baru)
    st.toast("✅ Material berhasil masuk ke keranjang!")


with col_v4:
    st.write(" ")
    st.write(" ")
    st.button(
        "➕ Tambah ke Keranjang",
        use_container_width=True,
        on_click=tambah_ke_keranjang,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. BAGIAN 3: KERANJANG EDITABLE & PERHITUNGAN
# ==========================================
st.markdown('<div class="section-title">3. Keranjang Input Material (Bisa Edit Volume Langsung)</div>', unsafe_allow_html=True)

if st.session_state.keranjang:
    df_cart_raw = pd.DataFrame(st.session_state.keranjang)

    st.caption("💡 **Petunjuk:** Anda bisa langsung mengubah angka pada kolom **Volume Material**, **Volume Pasang**, dan **Volume Bongkar** di bawah ini!")

    # Menggunakan st.data_editor agar kolom Volume bisa diisi/edited langsung di tabel
    edited_df = st.data_editor(
        df_cart_raw,
        column_config={
            "Jenis Konstruksi": st.column_config.TextColumn(disabled=True),
            "Type Konstruksi": st.column_config.TextColumn(disabled=True),
            "Material": st.column_config.TextColumn(disabled=True),
            "Volume Material": st.column_config.NumberColumn("Volume Material", min_value=0, step=1, required=True),
            "Volume Pasang": st.column_config.NumberColumn("Volume Pasang", min_value=0, step=1, required=True),
            "Volume Bongkar": st.column_config.NumberColumn("Volume Bongkar", min_value=0, step=1, required=True),
        },
        use_container_width=True,
        hide_index=True,
        key="editor_keranjang",
    )

    # Simpan perubahan kembali ke session state
    st.session_state.keranjang = edited_df.to_dict("records")

    # Hitung Otomatis
    merged = pd.merge(
        edited_df,
        df_master,
        left_on=["Jenis Konstruksi", "Type Konstruksi", "Material"],
        right_on=["JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL"],
        how="left",
    )

    edited_df["Harga Material Satuan"] = merged["HARGA MATERIAL"].fillna(0.0)
    edited_df["Jasa Pasang Satuan"] = merged["JASA PASANG"].fillna(0.0)
    edited_df["Jasa Bongkar Satuan"] = merged["JASA BONGKAR"].fillna(0.0)

    # Biaya
    edited_df["Biaya Pasang"] = edited_df["Volume Pasang"] * edited_df["Jasa Pasang Satuan"]
    edited_df["Biaya Bongkar"] = edited_df["Volume Bongkar"] * edited_df["Jasa Bongkar Satuan"]

    def hitung_biaya_material(row):
        nama_mat = str(row["Material"]).upper()
        if "PLN" in nama_mat:
            return 0.0
        return row["Volume Material"] * row["Harga Material Satuan"]

    edited_df["Harga Material"] = edited_df.apply(hitung_biaya_material, axis=1)
    edited_df["Total Subtotal"] = edited_df["Harga Material"] + edited_df["Biaya Pasang"] + edited_df["Biaya Bongkar"]

    total_biaya = edited_df["Total Subtotal"].sum()
    df_hasil = edited_df

else:
    st.info("💡 Keranjang masih kosong. Silakan pilih material di atas lalu klik **➕ Tambah ke Keranjang**.")
    total_biaya = 0.0
    df_hasil = pd.DataFrame()

# KARTU TOTAL ESTIMASI HARGA
st.markdown(
    f"""
    <div class="total-box">
        <div class="total-title">💰 TOTAL ESTIMASI HARGA PEKERJAAN</div>
        <div class="total-amount">Rp {total_biaya:,.2f}</div>
    </div>
""",
    unsafe_allow_html=True,
)

col_act1, col_act2 = st.columns([1, 2])
with col_act1:
    if st.button("🗑️ Kosongkan Keranjang", use_container_width=True):
        st.session_state.keranjang = []
        st.rerun()

# ==========================================
# 6. SUBMIT DATA KE GOOGLE SHEETS
# ==========================================
with col_act2:
    if st.button(
        "🚀 SUBMIT DATA KE GOOGLE SHEETS",
        type="primary",
        use_container_width=True,
    ):
        if not st.session_state.keranjang:
            st.error("❌ Keranjang masih kosong! Tambahkan material terlebih dahulu.")
        elif not nama_pekerjaan:
            st.error("❌ Harap isi NAMA PEKERJAAN pada Header!")
        else:
            try:
                payload = []
                for item in df_hasil.to_dict("records"):
                    payload.append({
                        "NAMA PEKERJAAN": nama_pekerjaan,
                        "ALAMAT PEKERJAAN": alamat_pekerjaan,
                        "JENIS PEKERJAAN": jenis_pekerjaan,
                        "TANGGAL": str(tanggal),
                        "JENIS KONSTRUKSI": item["Jenis Konstruksi"],
                        "TYPE KONSTRUKSI": item["Type Konstruksi"],
                        "NAMA MATERIAL": item["Material"],
                        "VOL MATERIAL": int(item["Volume Material"]),
                        "VOL PASANG": int(item["Volume Pasang"]),
                        "VOL BONGKAR": int(item["Volume Bongkar"]),
                        "HARGA MATERIAL": round(float(item["Harga Material"]), 2),
                        "BIAYA PASANG": round(float(item["Biaya Pasang"]), 2),
                        "BIAYA BONGKAR": round(float(item["Biaya Bongkar"]), 2),
                        "TOTAL ESTIMASI": round(float(total_biaya), 2),
                    })

                with st.spinner("Sedang mengunggah data ke Google Sheets..."):
                    response = requests.post(WEBHOOK_URL, json=payload, timeout=15)

                if response.status_code == 200:
                    st.session_state.pesan_sukses = True
                    st.session_state.keranjang = []
                    st.rerun()
                else:
                    st.error(f"⚠️ Gagal mengirim data. Status Code: {response.status_code}")
            except Exception as e:
                st.error(f"⚠️ Terjadi kesalahan saat mengirim data: {e}")
