import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import datetime

EXCEL_FILE = "MATERIAL 1.xlsx"

st.set_page_config(page_title="Entri Data Material Pekerjaan", layout="wide")

st.title("⚡ Form Entri Data Material Pekerjaan")
st.markdown("Aplikasi entri data dengan **fitur pencarian material instan**.")

# --- INITIALIZE SESSION STATE (Keranjang Sementara) ---
if "keranjang_material" not in st.session_state:
    st.session_state.keranjang_material = []

# --- 1. INFORMASI PEKERJAAN ---
st.subheader("1. Informasi Pekerjaan")
col1, col2 = st.columns(2)

with col1:
    nama_pekerjaan = st.text_input("Nama Pekerjaan", placeholder="Masukkan nama pekerjaan...")
    type_pekerjaan = st.selectbox(
        "Type Pekerjaan",
        ["SAR", "PFK", "PREVENTIF", "KEYPOINT"]
    )

with col2:
    jenis_konstruksi = st.selectbox(
        "Jenis Konstruksi",
        ["SKTR", "SKSR", "SUTR", "SUTM"]
    )
    tanggal = st.date_input("Tanggal Pekerjaan", datetime.date.today())

st.divider()

# --- READ DAFTAR MATERIAL DARI EXCEL ---
try:
    df_raw = pd.read_excel(EXCEL_FILE, sheet_name='Sheet1', header=None)
    # Ambil daftar nama material dari kolom indeks 1 mulai baris ke-6
    daftar_material = df_raw.iloc[6:, 1].dropna().drop_duplicates().tolist()
except Exception as e:
    st.error(f"Gagal membaca file Excel '{EXCEL_FILE}'. Pastikan file berada di folder yang sama. Error: {e}")
    daftar_material = []

# --- 2. CARI & TAMBAH MATERIAL (KERANJANG) ---
st.subheader("2. Cari & Tambah Material")

col_mat, col_pasang, col_bongkar, col_btn = st.columns([5, 2, 2, 2])

with col_mat:
    selected_material = st.selectbox(
        "🔍 Cari Nama Material (Ketik kata kunci nama material di sini)",
        options=daftar_material,
        index=None,
        placeholder="Ketik untuk mencari, contoh: Kabel, Pipa, Bolt..."
    )

with col_pasang:
    jumlah_pasang = st.number_input("Jumlah Pasang", min_value=0, value=0, step=1)

with col_bongkar:
    jumlah_bongkar = st.number_input("Jumlah Bongkar", min_value=0, value=0, step=1)

with col_btn:
    st.write(" ") # Alignment
    st.write(" ")
    tambah_btn = st.button("➕ Tambah ke Daftar", use_container_width=True)

# Proses Tambah ke Session State
if tambah_btn:
    if not selected_material:
        st.warning("Pilih atau ketik nama material terlebih dahulu!")
    else:
        total = jumlah_pasang + jumlah_bongkar
        if total == 0:
            st.warning("Jumlah pasang atau bongkar minimal harus lebih dari 0!")
        else:
            # Cek apakah material sudah ada di keranjang
            ada = False
            for item in st.session_state.keranjang_material:
                if item["Material"] == selected_material:
                    item["Jumlah Pasang"] += jumlah_pasang
                    item["Jumlah Bongkar"] += jumlah_bongkar
                    item["Jumlah Material"] += total
                    ada = True
                    break
            
            if not ada:
                st.session_state.keranjang_material.append({
                    "Material": selected_material,
                    "Jumlah Pasang": jumlah_pasang,
                    "Jumlah Bongkar": jumlah_bongkar,
                    "Jumlah Material": total
                })
            st.success(f"'{selected_material}' berhasil ditambahkan ke daftar!")

st.divider()

# --- 3. DAFTAR MATERIAL TERPILIH & SUBMIT ---
st.subheader("3. Daftar Material Terpilih (Keranjang)")

if len(st.session_state.keranjang_material) > 0:
    df_keranjang = pd.DataFrame(st.session_state.keranjang_material)
    st.dataframe(df_keranjang, use_container_width=True)

    col_clear, col_submit = st.columns([2, 8])
    
    with col_clear:
        if st.button("🗑️ Kosongkan Daftar", type="secondary", use_container_width=True):
            st.session_state.keranjang_material = []
            st.rerun()

    with col_submit:
        if st.button("🚀 SUBMIT SEMUA DATA KE EXCEL", type="primary", use_container_width=True):
            if not nama_pekerjaan:
                st.error("Mohon isi Nama Pekerjaan terlebih dahulu di bagian atas!")
            else:
                try:
                    wb = load_workbook(EXCEL_FILE)
                    
                    # Buat/buka sheet REKAP_INPUT
                    if "REKAP_INPUT" not in wb.sheetnames:
                        ws = wb.create_sheet("REKAP_INPUT")
                        ws.append(["Nama Pekerjaan", "Type Pekerjaan", "Jenis Konstruksi", "Tanggal", "Material", "Jumlah Pasang", "Jumlah Bongkar", "Jumlah Material"])
                    else:
                        ws = wb["REKAP_INPUT"]
                    
                    # Simpan seluruh isi keranjang
                    for item in st.session_state.keranjang_material:
                        ws.append([
                            nama_pekerjaan,
                            type_pekerjaan,
                            jenis_konstruksi,
                            str(tanggal),
                            item["Material"],
                            item["Jumlah Pasang"],
                            item["Jumlah Bongkar"],
                            item["Jumlah Material"]
                        ])
                    
                    wb.save(EXCEL_FILE)
                    st.balloons()
                    st.success("✅ Semua data material berhasil disimpan ke sheet 'REKAP_INPUT' di Excel!")
                    
                    # Reset keranjang setelah berhasil submit
                    st.session_state.keranjang_material = []
                    
                except Exception as err:
                    st.error(f"Gagal menyimpan ke Excel. Pastikan file Excel tidak sedang dibuka. Detail: {err}")
else:
    st.info("Belum ada material yang ditambahkan ke daftar.")