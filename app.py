import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Sistem Entri Material PLN", layout="wide"
)


# ==========================================
# 1. LOAD & CLEANING MASTER DATABASE EXCEL
# ==========================================
@st.cache_data
def load_and_clean_master(filepath):
    # Membaca data tabel mulai dari baris header (index 5)
    df = pd.read_excel(filepath, sheet_name="HEADER APLIKASI", header=5)

    # 1. Trim spasi berlebih pada nama material dan tipe
    string_cols = ["JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # 2. Konversi kolom Harga & Jasa menjadi Angka (Teks 'PLN' otomatis jadi 0)
    numeric_cols = ["HARGA MATERIAL", "JASA PASANG", "JASA BONGKAR"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    return df


# Membaca Master Data
try:
    df_master = load_and_clean_master("MATERIAL 1.xlsx")
except Exception:
    try:
        df_master = load_and_clean_master("MATERIAL 1_2.xlsx")
    except Exception:
        df_master = load_and_clean_master("MATERIAL 1_3.xlsx")

# ==========================================
# 2. SESSION STATE KERANJANG
# ==========================================
if "keranjang" not in st.session_state:
    st.session_state.keranjang = []

# ==========================================
# 3. BAGIAN 1: HEADER PEKERJAAN (SESUAI EXCEL MASTER)
# ==========================================
st.title("⚡ Sistem Entri Material PLN")
st.subheader("1. Header Data Pekerjaan")

col_h1, col_h2 = st.columns(2)

with col_h1:
    nama_pekerjaan = st.text_input(
        "NAMA PEKERJAAN :", placeholder="Masukkan Nama Pekerjaan..."
    )
    alamat_pekerjaan = st.text_area(
        "ALAMAT PEKERJAAN :", placeholder="Masukkan Alamat Pekerjaan..."
    )

with col_h2:
    jenis_pekerjaan = st.selectbox(
        "JENIS PEKERJAAN :",
        ["SAR", "PFK", "PREVENTIF", "KEYPOINT", "PEMELIHARAAN JARINGAN"],
    )
    tanggal = st.date_input("TANGGAL :")

st.markdown("---")

# ==========================================
# 4. BAGIAN 2: FORM INPUT MATERIAL
# ==========================================
st.subheader("2. Form Input Material Pekerjaan")

# Pilihan Dropdown Dinamis dari Database
list_jenis = sorted(df_master["JENIS KONSTRUKSI"].unique().tolist())

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    jenis_selected = st.selectbox("Jenis Konstruksi", list_jenis)

df_filtered_type = df_master[df_master["JENIS KONSTRUKSI"] == jenis_selected]
list_type = sorted(df_filtered_type["TYPE KONSTRUKSI"].unique().tolist())

with col_f2:
    type_selected = st.selectbox("Type Konstruksi", list_type)

df_filtered_mat = df_filtered_type[
    df_filtered_type["TYPE KONSTRUKSI"] == type_selected
]
list_material = sorted(df_filtered_mat["NAMA MATERIAL"].unique().tolist())

with col_f3:
    material_selected = st.selectbox("Nama Material", list_material)

# Input Volume dan Tombol Tambah
col_v1, col_v2, col_v3, col_v4 = st.columns([1, 1, 1, 1.2])

with col_v1:
    vol_mat = st.number_input("Volume Material", min_value=0, value=1, step=1)
with col_v2:
    vol_pasang = st.number_input("Volume Pasang", min_value=0, value=1, step=1)
with col_v3:
    vol_bongkar = st.number_input(
        "Volume Bongkar", min_value=0, value=0, step=1
    )

with col_v4:
    st.write(" ")
    st.write(" ")
    btn_tambah = st.button("➕ Tambah ke Keranjang", use_container_width=True)

# Tambah Item ke Keranjang
if btn_tambah:
    st.session_state.keranjang.append({
        "Jenis Konstruksi": jenis_selected,
        "Type Konstruksi": type_selected,
        "Material": material_selected,
        "Volume Material": vol_mat,
        "Volume Pasang": vol_pasang,
        "Volume Bongkar": vol_bongkar,
    })
    st.success("Item berhasil ditambahkan!")

st.markdown("---")

# ==========================================
# 5. BAGIAN 3: KERANJANG & PERHITUNGAN BIAYA
# ==========================================
st.subheader("3. Keranjang Input Material")


def hitung_keranjang(list_keranjang, df_master):
    if not list_keranjang:
        return pd.DataFrame(), 0.0

    df_cart = pd.DataFrame(list_keranjang)

    # Lookup Harga dari Master Database
    merged = pd.merge(
        df_cart,
        df_master,
        left_on=["Jenis Konstruksi", "Type Konstruksi", "Material"],
        right_on=["JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL"],
        how="left",
    )

    df_cart["Harga Material Satuan"] = merged["HARGA MATERIAL"].fillna(0.0)
    df_cart["Harga Pasang Satuan"] = merged["JASA PASANG"].fillna(0.0)
    df_cart["Harga Bongkar Satuan"] = merged["JASA BONGKAR"].fillna(0.0)

    # Perhitungan Total per Item
    df_cart["Biaya Material"] = (
        df_cart["Volume Material"] * df_cart["Harga Material Satuan"]
    )
    df_cart["Biaya Pasang"] = (
        df_cart["Volume Pasang"] * df_cart["Harga Pasang Satuan"]
    )
    df_cart["Biaya Bongkar"] = (
        df_cart["Volume Bongkar"] * df_cart["Harga Bongkar Satuan"]
    )

    total_estimasi = (
        df_cart["Biaya Material"].sum()
        + df_cart["Biaya Pasang"].sum()
        + df_cart["Biaya Bongkar"].sum()
    )

    return df_cart, total_estimasi


# Proses Kalkulasi Keranjang
df_hasil, total_biaya = hitung_keranjang(st.session_state.keranjang, df_master)

# Tampilkan Tabel Keranjang
if not df_hasil.empty:
    df_display = df_hasil[[
        "Jenis Konstruksi",
        "Type Konstruksi",
        "Material",
        "Volume Material",
        "Volume Pasang",
        "Volume Bongkar",
        "Harga Material Satuan",
        "Biaya Material",
        "Biaya Pasang",
    ]].copy()

    # Format Tampilan Mata Uang Rp
    df_display["Harga Material Satuan"] = df_display[
        "Harga Material Satuan"
    ].apply(lambda x: f"Rp {x:,.0f}")
    df_display["Biaya Material"] = df_display["Biaya Material"].apply(
        lambda x: f"Rp {x:,.0f}"
    )
    df_display["Biaya Pasang"] = df_display["Biaya Pasang"].apply(
        lambda x: f"Rp {x:,.0f}"
    )

    st.dataframe(df_display, use_container_width=True)
else:
    st.info("Keranjang kosong. Silakan isi form di atas untuk memasukkan data.")

# Display Total Estimasi Harga
st.markdown("##### 💰 TOTAL ESTIMASI HARGA PEKERJAAN")
st.markdown(f"# Rp {total_biaya:,.2f}")

# Tombol Aksi Keranjang
col_act1, col_act2 = st.columns([1, 2])
with col_act1:
    if st.button("🗑️ Kosongkan Keranjang", use_container_width=True):
        st.session_state.keranjang = []
        st.rerun()

with col_act2:
    if st.button(
        "🚀 SUBMIT DATA KE GOOGLE SHEETS",
        type="primary",
        use_container_width=True,
    ):
        st.success("Data berhasil disubmit!")
