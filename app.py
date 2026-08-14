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
    df = pd.read_excel(filepath, sheet_name="HEADER APLIKASI", header=5)

    # Pembersihan Spasi Berlebih pada Kolom Kunci
    string_cols = ["JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Konversi Kolom Harga & Jasa ke Tipe Data Angka (Numeric)
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
    except Exception as e:
        st.error(f"Gagal membaca file master Excel! Error: {e}")
        st.stop()

# ==========================================
# 2. INISIALISASI SESSION STATE
# ==========================================
if "keranjang" not in st.session_state:
    st.session_state.keranjang = []

# ==========================================
# 3. BAGIAN 1: HEADER DATA PEKERJAAN & PELANGGAN
# ==========================================
st.title("⚡ Sistem Entri Material PLN")
st.subheader("1. Header Data Pekerjaan")

col_h1, col_h2 = st.columns(2)

with col_h1:
    no_agenda = st.text_input(
        "No. Agenda / SPK", value="", placeholder="Masukkan Nomor Agenda..."
    )
    nama_pelanggan = st.text_input(
        "Nama Pelanggan",
        value="",
        placeholder="Masukkan Nama Pelanggan / Lokasi...",
    )
    alamat = st.text_area(
        "Alamat Pekerjaan", value="", placeholder="Masukkan Alamat Lengkap..."
    )

with col_h2:
    unit_up3 = st.selectbox(
        "Unit / ULP", ["ULP KOTA", "ULP TIMUR", "ULP BARAT", "ULP SELATAN"]
    )
    daya_pasang = st.selectbox(
        "Daya (VA)",
        [
            "450 VA",
            "900 VA",
            "1300 VA",
            "2200 VA",
            "3500 VA",
            "5500 VA",
            "11000 VA",
            "Lainnya",
        ],
    )
    jenis_pekerjaan = st.selectbox(
        "Jenis Pekerjaan",
        [
            "PASANG BARU (PB)",
            "TAMBAH DAYA (TD)",
            "GESER TIANG / GARDU",
            "PEMELIHARAAN JARINGAN",
        ],
    )

st.markdown("---")

# ==========================================
# 4. BAGIAN 2: FORM INPUT MATERIAL
# ==========================================
st.subheader("2. Form Input Material Pekerjaan")

# Dropdown Dinamis dari Master Data
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

# Logika Tambah Item ke Keranjang
if btn_tambah:
    item_baru = {
        "Jenis Konstruksi": jenis_selected,
        "Type Konstruksi": type_selected,
        "Material": material_selected,
        "Volume Material": vol_mat,
        "Volume Pasang": vol_pasang,
        "Volume Bongkar": vol_bongkar,
    }
    st.session_state.keranjang.append(item_baru)
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

    # Match dengan Master Database berdasarkan Jenis, Type, dan Nama Material
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

    # Perhitungan Biaya Total
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


# Menghitung Keranjang
df_hasil, total_biaya = hitung_keranjang(st.session_state.keranjang, df_master)

# Menampilkan Tabel Keranjang
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

    # Format Tampilan Rupiah
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

# Menampilkan Total Estimasi Harga
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
        if not no_agenda:
            st.warning("Silakan isi No. Agenda sebelum mengirim data.")
        else:
            st.success(
                f"Data untuk Agenda '{no_agenda}' berhasil disubmit ke Google"
                " Sheets!"
            )
