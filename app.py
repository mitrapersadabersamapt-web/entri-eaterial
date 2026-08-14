import json
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Sistem Entri Material PLN", layout="wide")

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

if "v_mat" not in st.session_state:
    st.session_state.v_mat = 0
if "v_pasang" not in st.session_state:
    st.session_state.v_pasang = 0
if "v_bongkar" not in st.session_state:
    st.session_state.v_bongkar = 0

# ==========================================
# 3. BAGIAN 1: HEADER PEKERJAAN
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

st.markdown("---")

col_v1, col_v2, col_v3, col_v4 = st.columns([1, 1, 1, 1.2])

with col_v1:
    vol_mat = st.number_input(
        "Volume Material", min_value=0, key="v_mat", step=1
    )
with col_v2:
    vol_pasang = st.number_input(
        "Volume Pasang", min_value=0, key="v_pasang", step=1
    )
with col_v3:
    vol_bongkar = st.number_input(
        "Volume Bongkar", min_value=0, key="v_bongkar", step=1
    )


def tambah_ke_keranjang():
    if (
        st.session_state.v_mat == 0
        and st.session_state.v_pasang == 0
        and st.session_state.v_bongkar == 0
    ):
        st.toast("⚠️ Harap isi volume terlebih dahulu!")
        return

    item_baru = {
        "Jenis Konstruksi": jenis_selected,
        "Type Konstruksi": type_selected,
        "Material": material_selected,
        "Volume Material": st.session_state.v_mat,
        "Volume Pasang": st.session_state.v_pasang,
        "Volume Bongkar": st.session_state.v_bongkar,
    }
    st.session_state.keranjang.append(item_baru)

    st.session_state.v_mat = 0
    st.session_state.v_pasang = 0
    st.session_state.v_bongkar = 0

    st.toast("✅ Item berhasil ditambahkan ke keranjang!")


with col_v4:
    st.write(" ")
    st.write(" ")
    st.button(
        "➕ Tambah ke Keranjang",
        use_container_width=True,
        on_click=tambah_ke_keranjang,
    )

st.markdown("---")

# ==========================================
# 5. BAGIAN 3: KERANJANG & LOGIKA PERHITUNGAN
# ==========================================
st.subheader("3. Keranjang Input Material")


def hitung_keranjang(list_keranjang, df_master):
    if not list_keranjang:
        return pd.DataFrame(), 0.0

    df_cart = pd.DataFrame(list_keranjang)

    merged = pd.merge(
        df_cart,
        df_master,
        left_on=["Jenis Konstruksi", "Type Konstruksi", "Material"],
        right_on=["JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL"],
        how="left",
    )

    df_cart["Harga Material Satuan"] = merged["HARGA MATERIAL"].fillna(0.0)
    df_cart["Jasa Pasang Satuan"] = merged["JASA PASANG"].fillna(0.0)
    df_cart["Jasa Bongkar Satuan"] = merged["JASA BONGKAR"].fillna(0.0)

    # 1. Biaya Pasang = Jasa Pasang Satuan x Volume Pasang
    df_cart["Biaya Pasang"] = (
        df_cart["Volume Pasang"] * df_cart["Jasa Pasang Satuan"]
    )

    # 2. Biaya Bongkar = Jasa Bongkar Satuan x Volume Bongkar
    df_cart["Biaya Bongkar"] = (
        df_cart["Volume Bongkar"] * df_cart["Jasa Bongkar Satuan"]
    )

    # 3. Harga Material = Harga Material Satuan x Volume Material
    # ATURAN: Jika nama material mengandung kata "PLN", harganya 0
    def hitung_biaya_material(row):
        nama_mat = str(row["Material"]).upper()
        if "PLN" in nama_mat:
            return 0.0
        return row["Volume Material"] * row["Harga Material Satuan"]

    df_cart["Harga Material"] = df_cart.apply(hitung_biaya_material, axis=1)

    # Subtotal per baris
    df_cart["Total Subtotal"] = (
        df_cart["Harga Material"]
        + df_cart["Biaya Pasang"]
        + df_cart["Biaya Bongkar"]
    )

    total_estimasi = df_cart["Total Subtotal"].sum()

    return df_cart, total_estimasi


df_hasil, total_biaya = hitung_keranjang(st.session_state.keranjang, df_master)

if not df_hasil.empty:
    df_display = df_hasil[[
        "Jenis Konstruksi",
        "Type Konstruksi",
        "Material",
        "Volume Material",
        "Volume Pasang",
        "Volume Bongkar",
        "Harga Material",
        "Biaya Pasang",
        "Biaya Bongkar",
    ]].copy()

    # Tampilan di Streamlit berformat Rupiah
    df_display["Harga Material"] = df_display["Harga Material"].apply(
        lambda x: f"Rp {x:,.0f}"
    )
    df_display["Biaya Pasang"] = df_display["Biaya Pasang"].apply(
        lambda x: f"Rp {x:,.0f}"
    )
    df_display["Biaya Bongkar"] = df_display["Biaya Bongkar"].apply(
        lambda x: f"Rp {x:,.0f}"
    )

    st.dataframe(df_display, use_container_width=True)
else:
    st.info("Keranjang kosong. Silakan isi form di atas untuk memasukkan data.")

st.markdown("##### 💰 TOTAL ESTIMASI HARGA PEKERJAAN")
st.markdown(f"# Rp {total_biaya:,.2f}")

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
                    # MENGIRIM ANGKA MURNI KE GOOGLE SHEETS AGAR TIDAK EROR DESIMAL
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

                response = requests.post(WEBHOOK_URL, json=payload, timeout=15)

                if response.status_code == 200:
                    st.success("🎉 Data BERHASIL dikirim dan tersimpan di Google Sheet!")
                    st.session_state.keranjang = []
                    st.rerun()
                else:
                    st.error(f"⚠️ Gagal mengirim data. Status Code: {response.status_code}")
            except Exception as e:
                st.error(f"⚠️ Terjadi kesalahan saat mengirim data: {e}")
