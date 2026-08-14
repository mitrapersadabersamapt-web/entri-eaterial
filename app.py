import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import requests
import re

# --- URL WEB APP GOOGLE APPS SCRIPT ANDA ---
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbz-ryJ47OM-ZwV7h-7G5eRgjBGo3IY96xrTC7VR2c5oATUkd6yLgnmYCRsItS6-C8g/exec"

# URL Spreadsheet untuk membaca/menampilkan rekap data
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1DUnC28hWJPXVKAamJSHv2t3LR2wdVCq-jegYJKIPAQY/edit?usp=sharing"

EXCEL_FILE = "MATERIAL 1.xlsx"
SHEET_NAME = "HEADER APLIKASI"

st.set_page_config(page_title="Sistem Entri Material PLN", layout="wide", page_icon="⚡")

st.title("⚡ Sistem Entri Material PLN")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- INITIALIZE SESSION STATE ---
if "keranjang_material" not in st.session_state:
    st.session_state.keranjang_material = []

def clean_string(val):
    if pd.isna(val):
        return ""
    # Normalisasi spasi ganda/berlebih menjadi 1 spasi tunggal
    return re.sub(r'\s+', ' ', str(val)).strip()

# MENGAMBIL MASTER DATA MATERIAL DARI EXCEL LOKAL REPO
@st.cache_data(ttl=60)
def load_master_data():
    try:
        df_raw = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, header=None)
        
        # Mengambil baris data mulai indeks ke-6
        df_mat = df_raw.iloc[6:, :].copy()
        
        df_selected = pd.DataFrame()
        df_selected["JENIS_KONSTRUKSI"] = df_mat.iloc[:, 1].apply(clean_string)
        df_selected["NAMA_MATERIAL"] = df_mat.iloc[:, 2].apply(clean_string)
        df_selected["TYPE_KONSTRUKSI"] = df_mat.iloc[:, 3].apply(clean_string)
        
        # Mengambil HARGA MATERIAL (Index 4), JASA PASANG (Index 5), JASA BONGKAR (Index 6)
        df_selected["HARGA_MATERIAL"] = pd.to_numeric(df_mat.iloc[:, 4], errors='coerce').fillna(0.0)
        df_selected["JASA_PASANG"] = pd.to_numeric(df_mat.iloc[:, 5], errors='coerce').fillna(0.0)
        df_selected["JASA_BONGKAR"] = pd.to_numeric(df_mat.iloc[:, 6], errors='coerce').fillna(0.0)

        # Simpan nilai string mentah untuk keperluan tampilan label (misal: memunculkan tulisan "PLN")
        df_selected["HARGA_MATERIAL_RAW"] = df_mat.iloc[:, 4].fillna("0").apply(clean_string)

        df_selected = df_selected[df_selected["NAMA_MATERIAL"] != ""]
        return df_selected
    except Exception as e:
        st.error(f"Gagal membaca master file '{EXCEL_FILE}'. Detail: {e}")
        return pd.DataFrame(columns=["JENIS_KONSTRUKSI", "NAMA_MATERIAL", "TYPE_KONSTRUKSI", "HARGA_MATERIAL", "JASA_PASANG", "JASA_BONGKAR", "HARGA_MATERIAL_RAW"])

df_master = load_master_data()

# --- 1. INFORMASI PEKERJAAN ---
st.subheader("1. Informasi Pekerjaan")
col1, col2 = st.columns(2)

with col1:
    nama_pekerjaan = st.text_input("Nama Pekerjaan", placeholder="Masukkan nama pekerjaan...")
    alamat_pekerjaan = st.text_input("Alamat Pekerjaan", placeholder="Masukkan lokasi/alamat pekerjaan...")

with col2:
    jenis_pekerjaan = st.selectbox("Jenis Pekerjaan", ["SAR", "PFK", "PREVENTIF", "KEYPOINT"])
    tanggal = st.date_input("Tanggal Pekerjaan", datetime.date.today())

st.divider()

# --- 2. FILTER & PENCARIAN MATERIAL ---
st.subheader("2. Cari & Tambah Material")

if not df_master.empty:
    list_jenis_konstruksi = sorted(df_master["JENIS_KONSTRUKSI"].unique().tolist())
else:
    list_jenis_konstruksi = []

col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    selected_jenis_konstruksi = st.selectbox("📌 Pilih Jenis Konstruksi", options=list_jenis_konstruksi, index=0 if list_jenis_konstruksi else None)

if selected_jenis_konstruksi:
    df_filtered_type = df_master[df_master["JENIS_KONSTRUKSI"] == selected_jenis_konstruksi]
    list_type_konstruksi = sorted(df_filtered_type["TYPE_KONSTRUKSI"].unique().tolist())
else:
    df_filtered_type = df_master
    list_type_konstruksi = []

with col_filter2:
    selected_type_konstruksi = st.selectbox(
        "🏷️ Filter Type Konstruksi (Opsional)", 
        options=["-- Semua Type --"] + list_type_konstruksi,
        index=0
    )

df_final_mat = df_filtered_type.copy()
if selected_type_konstruksi and selected_type_konstruksi != "-- Semua Type --":
    df_final_mat = df_final_mat[df_final_mat["TYPE_KONSTRUKSI"] == selected_type_konstruksi]

list_material_filtered = sorted(df_final_mat["NAMA_MATERIAL"].unique().tolist())

st.write("---")

with st.form(key="form_tambah_material", clear_on_submit=True):
    selected_material = st.selectbox(
        f"🔍 Cari Nama Material ({len(list_material_filtered)} item ditemukan)",
        options=list_material_filtered,
        index=None,
        placeholder="Ketik untuk mencari nama material..."
    )

    col_vol_mat, col_vol_pasang, col_vol_bongkar = st.columns(3)

    with col_vol_mat:
        volume_material = st.number_input("Volume Material", min_value=0, value=0, step=1)

    with col_vol_pasang:
        volume_pasang = st.number_input("Volume Pasang", min_value=0, value=0, step=1)

    with col_vol_bongkar:
        volume_bongkar = st.number_input("Volume Bongkar", min_value=0, value=0, step=1)

    st.write("")
    tambah_btn = st.form_submit_button("➕ Tambahkan ke Keranjang", type="secondary", use_container_width=True)

if tambah_btn:
    if not selected_material:
        st.warning("Pilih material terlebih dahulu!")
    else:
        if volume_material == 0 and volume_pasang == 0 and volume_bongkar == 0:
            st.warning("Minimal salah satu volume (Material / Pasang / Bongkar) harus diisi > 0!")
        else:
            row_match = df_final_mat[df_final_mat["NAMA_MATERIAL"] == selected_material]
            
            if not row_match.empty:
                type_konstruksi_val = row_match["TYPE_KONSTRUKSI"].values[0]
                harga_mat = float(row_match["HARGA_MATERIAL"].values[0])
                harga_pasang = float(row_match["JASA_PASANG"].values[0])
                harga_bongkar = float(row_match["JASA_BONGKAR"].values[0])
                harga_mat_raw = str(row_match["HARGA_MATERIAL_RAW"].values[0])
            else:
                type_konstruksi_val = selected_type_konstruksi if selected_type_konstruksi != "-- Semua Type --" else "-"
                harga_mat, harga_pasang, harga_bongkar = 0.0, 0.0, 0.0
                harga_mat_raw = "0"

            # Hitung biaya perkalian (Jika PLN -> harga_mat = 0, sehingga total_biaya_mat = 0)
            total_biaya_mat = volume_material * harga_mat
            total_biaya_pasang = volume_pasang * harga_pasang
            total_biaya_bongkar = volume_bongkar * harga_bongkar
            
            # Estimasi Harga = Jumlah Total Biaya Material + Pasang + Bongkar
            estimasi_harga = total_biaya_mat + total_biaya_pasang + total_biaya_bongkar

            # Format label harga satuan (aman dari error tipe data)
            harga_satuan_label = "PLN" if "PLN" in harga_mat_raw.upper() else f"Rp {harga_mat:,.0f}"

            st.session_state.keranjang_material.append({
                "Jenis Konstruksi": selected_jenis_konstruksi,
                "Type Konstruksi": type_konstruksi_val,
                "Material": selected_material,
                "Volume Material": volume_material,
                "Volume Pasang": volume_pasang,
                "Volume Bongkar": volume_bongkar,
                "Harga Material Satuan": harga_satuan_label,
                "Biaya Material": total_biaya_mat,
                "Biaya Pasang": total_biaya_pasang,
                "Biaya Bongkar": total_biaya_bongkar,
                "Estimasi Harga": estimasi_harga
            })
            st.success(f"'{selected_material}' ({type_konstruksi_val}) berhasil ditambahkan ke keranjang!")
            st.rerun()

st.divider()

# --- 3. KERANJANG INPUT & SUBMIT TO GOOGLE SHEETS ---
st.subheader("3. Keranjang Input Material")

if len(st.session_state.keranjang_material) > 0:
    df_keranjang = pd.DataFrame(st.session_state.keranjang_material)
    
    # Format Tampilan Tabel Keranjang
    st.dataframe(df_keranjang, use_container_width=True)

    # Hitung total estimasi harga seluruh keranjang
    total_estimasi_semua = df_keranjang["Estimasi Harga"].sum()
    st.metric(label="💰 TOTAL ESTIMASI HARGA PEKERJAAN", value=f"Rp {total_estimasi_semua:,.2f}")

    col_clear, col_submit = st.columns([2, 8])
    with col_clear:
        if st.button("🗑️ Kosongkan Keranjang", use_container_width=True):
            st.session_state.keranjang_material = []
            st.rerun()

    with col_submit:
        if st.button("🚀 SUBMIT DATA KE GOOGLE SHEETS", type="primary", use_container_width=True):
            if not nama_pekerjaan:
                st.error("Isi Nama Pekerjaan terlebih dahulu!")
            else:
                try:
                    payload = []
                    for item in st.session_state.keranjang_material:
                        payload.append({
                            "Nama Pekerjaan": nama_pekerjaan,
                            "Alamat Pekerjaan": alamat_pekerjaan,
                            "Jenis Pekerjaan": jenis_pekerjaan,
                            "Tanggal": str(tanggal),
                            "Jenis Konstruksi": item["Jenis Konstruksi"],
                            "Type Konstruksi": item["Type Konstruksi"],
                            "Material": item["Material"],
                            "Volume Material": item["Volume Material"],
                            "Volume Pasang": item["Volume Pasang"],
                            "Volume Bongkar": item["Volume Bongkar"],
                            "Harga Material Satuan": item["Harga Material Satuan"],
                            "Biaya Material": item["Biaya Material"],
                            "Biaya Pasang": item["Biaya Pasang"],
                            "Biaya Bongkar": item["Biaya Bongkar"],
                            "Estimasi Harga": item["Estimasi Harga"]
                        })
                    
                    response = requests.post(WEB_APP_URL, json=payload)
                    
                    if response.status_code == 200:
                        st.balloons()
                        st.success("✅ Berhasil menyimpan transaksi dan estimasi harga ke Google Sheets!")
                        st.session_state.keranjang_material = []
                        st.rerun()
                    else:
                        st.error(f"Gagal mengirim data. Response Code: {response.status_code}")
                except Exception as err:
                    st.error(f"Gagal menyimpan data ke Google Sheets. Detail: {err}")
else:
    st.info("Belum ada material dalam keranjang.")

st.divider()

# --- 4. TAMPILKAN REKAP DATA REAL-TIME ---
st.subheader("📊 Rekap Data Masuk (Real-Time Google Sheets)")
try:
    df_rekap = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
    st.dataframe(df_rekap, use_container_width=True)
except Exception:
    st.write("Belum dapat memuat rekap data.")
