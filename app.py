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
# 3. BAGIAN 1: HEADER PEKERJAAN (OPSIONAL)
# ==========================================
st.markdown('<div class="section-title">1. Header Data Pekerjaan (Opsional)</div>', unsafe_allow_html=True)

col_h1, col_h2 = st.columns(2)

with col_h1:
    nama_pekerjaan = st.text_input(
        "NAMA PEKERJAAN (Opsional) :", placeholder="Masukkan Nama Pekerjaan (Boleh Dikosongkan)"
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
# 4. BAGIAN 2: PILIH KONSTRUKSI & CHECKBOX MATERIAL
# ==========================================
st.markdown('<div class="section-title">2. Pilih Material Per Konstruksi</div>', unsafe_allow_html=True)

col_k1, col_k2, col_k3 = st.columns([1.2, 1.2, 1])

with col_k1:
    list_jenis = sorted(df_master["JENIS KONSTRUKSI"].unique().tolist())
    jenis_selected = st.selectbox("1. Pilih Jenis Konstruksi:", list_jenis)

df_filtered_jenis = df_master[df_master["JENIS KONSTRUKSI"] == jenis_selected]

with col_k2:
    list_type = sorted(df_filtered_jenis["TYPE KONSTRUKSI"].unique().tolist())
    type_selected = st.selectbox("2. Pilih Type Konstruksi:", list_type)

with col_k3:
    jumlah_pemakaian = st.number_input(
        "3. Jumlah Pemakaian Konstruksi (Set/Unit):",
        min_value=1,
        value=1,
        step=1,
        help="Jumlah unit/set konstruksi ini (mengisi nilai awal jumlah material).",
    )

df_filtered = df_filtered_jenis[df_filtered_jenis["TYPE KONSTRUKSI"] == type_selected].copy()

st.caption("☑️ **Tandai / Centang material yang akan dipakai di bawah ini, lalu klik tombol tambah ke keranjang:**")

# Siapkan data untuk Data Editor (Checkbox)
df_filtered["Pilih"] = False
df_pilihan_display = df_filtered[["Pilih", "NAMA MATERIAL"]].rename(columns={"NAMA MATERIAL": "Nama Material"})

# Tabel Checkbox Material
selected_materials_editor = st.data_editor(
    df_pilihan_display,
    column_config={
        "Pilih": st.column_config.CheckboxColumn("Pilih", default=False),
        "Nama Material": st.column_config.TextColumn("Nama Material", disabled=True),
    },
    use_container_width=True,
    hide_index=True,
    key=f"editor_pilih_{jenis_selected}_{type_selected}"
)

# Tombol Tambah yang Tercentang
if st.button("➕ Masukkan Material Terpilih ke Keranjang", type="primary"):
    mat_terpilih = selected_materials_editor[selected_materials_editor["Pilih"] == True]["Nama Material"].tolist()
    
    if not mat_terpilih:
        st.warning("⚠️ Harap centang minimal satu material terlebih dahulu!")
    else:
        jumlah_ditambah = 0
        for mat in mat_terpilih:
            # Mengisi volume sesuai dengan jumlah pemakaian yang diinputkan tanpa perkalian berulang
            vol_mat_calc = int(jumlah_pemakaian)
            vol_pasang_calc = int(jumlah_pemakaian)
            vol_bongkar_calc = 0
            
            item_baru = {
                "Jenis Konstruksi": jenis_selected,
                "Type Konstruksi": type_selected,
                "Material": mat,
                "Volume Material": vol_mat_calc,
                "Volume Pasang": vol_pasang_calc,
                "Volume Bongkar": vol_bongkar_calc,
            }
            st.session_state.keranjang.append(item_baru)
            jumlah_ditambah += 1
            
        st.toast(f"✅ Berhasil menambahkan {jumlah_ditambah} material ke keranjang dengan jumlah {jumlah_pemakaian}!")
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. BAGIAN 3: KERANJANG WITH REAL-TIME PRICES & EDITABLE VOLUME
# ==========================================
st.markdown('<div class="section-title">3. Keranjang Input Material (Isi & Edit Volume di Sini)</div>', unsafe_allow_html=True)

if st.session_state.keranjang:
    df_cart_raw = pd.DataFrame(st.session_state.keranjang)

    # 1. Hitung ulang Rincian Harga secara Real-Time berdasarkan Master Data
    merged = pd.merge(
        df_cart_raw,
        df_master,
        left_on=["Jenis Konstruksi", "Type Konstruksi", "Material"],
        right_on=["JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL"],
        how="left",
    )

    df_cart_raw["Harga Satuan"] = merged["HARGA MATERIAL"].fillna(0.0)
    df_cart_raw["Jasa Pasang Satuan"] = merged["JASA PASANG"].fillna(0.0)
    df_cart_raw["Jasa Bongkar Satuan"] = merged["JASA BONGKAR"].fillna(0.0)

    # Biaya Pasang & Bongkar
    df_cart_raw["Biaya Pasang"] = df_cart_raw["Volume Pasang"] * df_cart_raw["Jasa Pasang Satuan"]
    df_cart_raw["Biaya Bongkar"] = df_cart_raw["Volume Bongkar"] * df_cart_raw["Jasa Bongkar Satuan"]

    # Biaya Material (0 jika material bertuliskan PLN)
    def hitung_biaya_material(row):
        nama_mat = str(row["Material"]).upper()
        if "PLN" in nama_mat:
            return 0.0
        return row["Volume Material"] * row["Harga Satuan"]

    df_cart_raw["Harga Material"] = df_cart_raw.apply(hitung_biaya_material, axis=1)
    df_cart_raw["Subtotal"] = df_cart_raw["Harga Material"] + df_cart_raw["Biaya Pasang"] + df_cart_raw["Biaya Bongkar"]

    st.caption("💡 **Petunjuk:** Ubah angka volume jika diperlukan. Harga Material, Biaya Pasang/Bongkar, dan Subtotal akan otomatis menyesuaikan.")

    # 2. Tampilkan Tabel Interaktif dengan Rincian Harga
    edited_df = st.data_editor(
        df_cart_raw[[
            "Jenis Konstruksi",
            "Type Konstruksi",
            "Material",
            "Volume Material",
            "Volume Pasang",
            "Volume Bongkar",
            "Harga Material",
            "Biaya Pasang",
            "Biaya Bongkar",
            "Subtotal"
        ]],
        column_config={
            "Jenis Konstruksi": st.column_config.TextColumn("Jenis Konstruksi", disabled=True),
            "Type Konstruksi": st.column_config.TextColumn("Type Konstruksi", disabled=True),
            "Material": st.column_config.TextColumn("Material", disabled=True),
            "Volume Material": st.column_config.NumberColumn("Vol Material", min_value=0, step=1, required=True),
            "Volume Pasang": st.column_config.NumberColumn("Vol Pasang", min_value=0, step=1, required=True),
            "Volume Bongkar": st.column_config.NumberColumn("Vol Bongkar", min_value=0, step=1, required=True),
            "Harga Material": st.column_config.NumberColumn("Harga Material", format="Rp %d", disabled=True),
            "Biaya Pasang": st.column_config.NumberColumn("Biaya Pasang", format="Rp %d", disabled=True),
            "Biaya Bongkar": st.column_config.NumberColumn("Biaya Bongkar", format="Rp %d", disabled=True),
            "Subtotal": st.column_config.NumberColumn("Subtotal", format="Rp %d", disabled=True),
        },
        use_container_width=True,
        hide_index=True,
        key="editor_keranjang",
    )

    # Update state volume jika pengguna mengubah volume di tabel
    st.session_state.keranjang = edited_df[[
        "Jenis Konstruksi", "Type Konstruksi", "Material", 
        "Volume Material", "Volume Pasang", "Volume Bongkar"
    ]].to_dict("records")

    total_biaya = edited_df["Subtotal"].sum()
    df_hasil = edited_df

else:
    st.info("💡 Keranjang masih kosong. Silakan centang material pada daftar di atas lalu klik **➕ Masukkan Material Terpilih ke Keranjang**.")
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
        else:
            try:
                # Jika nama pekerjaan tidak diisi, berikan tanda strip (-)
                nama_pekerjaan_kirim = nama_pekerjaan.strip() if nama_pekerjaan.strip() else "-"
                
                payload = []
                for item in df_hasil.to_dict("records"):
                    payload.append({
                        "NAMA PEKERJAAN": nama_pekerjaan_kirim,
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
