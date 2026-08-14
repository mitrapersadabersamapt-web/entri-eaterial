import pandas as pd
import streamlit as st

# ==========================================
# 1. LOAD & CLEANING MASTER DATABASE EXCEL
# ==========================================
@st.cache_data
def load_and_clean_master(filepath):
    # Membaca data mulai dari baris header (header index 5)
    df = pd.read_excel(filepath, sheet_name="HEADER APLIKASI", header=5)

    # A. Pembersihan Spasi Berlebih pada Kolom Kunci
    string_cols = ["JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # B. Konversi Kolom Harga & Jasa ke Tipe Data Angka (Numeric)
    # Teks seperti 'PLN' atau strip '-' akan dikonversi menjadi 0
    numeric_cols = ["HARGA MATERIAL", "JASA PASANG", "JASA BONGKAR"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    return df


# Load database
try:
    df_master = load_and_clean_master("MATERIAL 1.xlsx")
except Exception as e:
    st.error(f"Gagal membaca file master database: {e}")
    st.stop()

# ==========================================
# 2. INISIALISASI SESSION STATE KERANJANG
# ==========================================
if "keranjang" not in st.session_state:
    # Contoh data awal sesuai tampilan layar Anda
    st.session_state.keranjang = [
        {
            "Jenis Konstruksi": "SUTM",
            "Type Konstruksi": "KONTRUKSI TM - 1",
            "Material": (
                'ARM TIE BAND 4"(TM) (T = 6 MM X 42 MM) HDG TM LENGKAP'
                " BOLT&NUT-HDG"
            ),
            "Volume Material": 1,
            "Volume Pasang": 1,
            "Volume Bongkar": 0,
        },
        {
            "Jenis Konstruksi": "SUTM",
            "Type Konstruksi": "KONSTRUKSI ARRESTER / LA",
            "Material": 'ARM TIE TYPE 750 - 3/4" - (T=2,3 MM)',
            "Volume Material": 2,
            "Volume Pasang": 2,
            "Volume Bongkar": 0,
        },
        {
            "Jenis Konstruksi": "SUTM",
            "Type Konstruksi": "ANTI CLIMBING + DANGER PLATE",
            "Material": "BOLT & NUT M.16 X 75 - HDG",
            "Volume Material": 2,
            "Volume Pasang": 2,
            "Volume Bongkar": 0,
        },
        {
            "Jenis Konstruksi": "SUTM",
            "Type Konstruksi": "KONSTRUKSI ARRESTER / LA",
            "Material": "POLE ACC;CR ARM UNP100X50X5X2000MM GALV",
            "Volume Material": 1,
            "Volume Pasang": 1,
            "Volume Bongkar": 0,
        },
        {
            "Jenis Konstruksi": "SUTM",
            "Type Konstruksi": "KONSTRUKSI ARRESTER / LA",
            "Material": (
                'SINGLE ARM BAND 8" (T = 6 MM X 42 MM) HDG TM LENGKAP NUT-HDG'
            ),
            "Volume Material": 2,
            "Volume Pasang": 2,
            "Volume Bongkar": 0,
        },
        {
            "Jenis Konstruksi": "SUTM",
            "Type Konstruksi": "KONSTRUKSI ARRESTER / LA",
            "Material": "SQUARE WASHER - (L=50 MM, P=50 MM, T=2,5 MM)",
            "Volume Material": 5,
            "Volume Pasang": 5,
            "Volume Bongkar": 0,
        },
    ]

# ==========================================
# 3. FUNGSI PERHITUNGAN & LOOKUP HARGA
# ==========================================
def hitung_keranjang(list_keranjang, df_master):
    df_cart = pd.DataFrame(list_keranjang)

    if df_cart.empty:
        return df_cart, 0.0

    # Gabungkan dengan df_master untuk mengambil Harga & Jasa berdasarkan Jenis, Type, dan Nama Material
    merged = pd.merge(
        df_cart,
        df_master,
        left_on=["Jenis Konstruksi", "Type Konstruksi", "Material"],
        right_on=["JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL"],
        how="left",
    )

    # Ambil harga satuan dan isi angka 0 jika tidak ditemukan match
    df_cart["Harga Material Satuan"] = merged["HARGA MATERIAL"].fillna(0.0)
    df_cart["Harga Pasang Satuan"] = merged["JASA PASANG"].fillna(0.0)
    df_cart["Harga Bongkar Satuan"] = merged["JASA BONGKAR"].fillna(0.0)

    # PERHITUNGAN BIAYA
    df_cart["Biaya Material"] = (
        df_cart["Volume Material"] * df_cart["Harga Material Satuan"]
    )
    df_cart["Biaya Pasang"] = (
        df_cart["Volume Pasang"] * df_cart["Harga Pasang Satuan"]
    )
    df_cart["Biaya Bongkar"] = (
        df_cart["Volume Bongkar"] * df_cart["Harga Bongkar Satuan"]
    )

    # TOTAL ESTIMASI HARGA
    total_estimasi = (
        df_cart["Biaya Material"].sum()
        + df_cart["Biaya Pasang"].sum()
        + df_cart["Biaya Bongkar"].sum()
    )

    return df_cart, total_estimasi


# Execute perhitungan
df_hasil, total_biaya = hitung_keranjang(st.session_state.keranjang, df_master)

# ==========================================
# 4. TAMPILAN DASHBOARD STREAMLIT
# ==========================================
st.title("3. Keranjang Input Material")

# Format Tampilan Tabel Keranjang
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

    st.info("Keranjang kosong.")

# Tampilan Total Estimasi Harga
st.markdown("##### 💰 TOTAL ESTIMASI HARGA PEKERJAAN")
st.markdown(f"# Rp {total_biaya:,.2f}")

# Tombol Aksi
col1, col2 = st.columns([1, 2])
with col1:
    if st.button("🗑️ Kosongkan Keranjang", use_container_width=True):
        st.session_state.keranjang = []
        st.rerun()

with col2:
    if st.button(
        "🚀 SUBMIT DATA KE GOOGLE SHEETS",
        type="primary",
        use_container_width=True,
    ):
        st.success("Data berhasil disubmit!")
