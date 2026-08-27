import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(
    page_title="Sistem Entri Material PLN",
    page_icon="⚡",
    layout="wide"
)

# URL Webhook Apps Script (Pastikan sesuai dengan milik Anda)
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbz_CONTOH_DEPLOYMENT_ID_ANDA/exec"

# Master Material Database / Sheet Simulasi
@st.cache_data
def load_master_material():
    # Mengembalikan dataframe master material
    return pd.DataFrame([
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "ACCESORIES", "NAMA MATERIAL": "U - STRAP - TM - (L=42 MM, T=6 MM)", "HARGA MATERIAL": 65413, "JASA PASANG": 14487, "JASA BONGKAR": 0},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "ACCESORIES", "NAMA MATERIAL": "SQUARE WASHER - (L=50 MM, P=50 MM, T=2.5 MM)", "HARGA MATERIAL": 1130137, "JASA PASANG": 104305, "JASA BONGKAR": 0},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "ACCESORIES", "NAMA MATERIAL": "LINE TAP CONNECTOR 150/150 MM2 TYPE G", "HARGA MATERIAL": 260037, "JASA PASANG": 33606, "JASA BONGKAR": 0},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "ARRESTER & CUT OUT", "NAMA MATERIAL": "LA:20-24KV;K:10KA;POLYMER;", "HARGA MATERIAL": 12707, "JASA PASANG": 12707, "JASA BONGKAR": 0},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "ARRESTER & CUT OUT", "NAMA MATERIAL": "POLYMER CUT OUT SWITCH 24 KV + FUSE", "HARGA MATERIAL": 25416, "JASA PASANG": 25416, "JASA BONGKAR": 0},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "ARRESTER & CUT OUT", "NAMA MATERIAL": "FUSE LINK LL / CO 3 - 6 A", "HARGA MATERIAL": 63537, "JASA PASANG": 63537, "JASA BONGKAR": 0},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "COVER", "NAMA MATERIAL": "UNIV ACC;COVER BUSHING TRAFO", "HARGA MATERIAL": 38122, "JASA PASANG": 38122, "JASA BONGKAR": 0},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "COVER", "NAMA MATERIAL": "CUT OUT ACC;COVER CUT OUT ATAS", "HARGA MATERIAL": 38122, "JASA PASANG": 38122, "JASA BONGKAR": 0},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "COVER", "NAMA MATERIAL": "UNIV ACC;COVER ARRESTER", "HARGA MATERIAL": 131731, "JASA PASANG": 20851, "JASA BONGKAR": 0},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "TRANSFORMATOR", "NAMA MATERIAL": "TRAFO DISTRIBUSI 20 KV 3 PH 100 KVA YZN5 (D3)", "HARGA MATERIAL": 0, "JASA PASANG": 2650, "JASA BONGKAR": 0},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "KONTRUKSI TM - 1", "NAMA MATERIAL": "POLE ACC;CR ARM UNP100X50X5X2000MM GALV", "HARGA MATERIAL": 0, "JASA PASANG": 118002, "JASA BONGKAR": 35681},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "KONTRUKSI TM - 1", "NAMA MATERIAL": "ARM TIE TYPE 1500 - 1 1/2\" - (T=2.3MM)", "HARGA MATERIAL": 379960, "JASA PASANG": 48676, "JASA BONGKAR": 0},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "KONTRUKSI TM - 1", "NAMA MATERIAL": "ARM TIE BAND 8\"(TM) (T = 6 MM X 42 MM) HDG TM LENGKAP BOLT&NUT-HDG", "HARGA MATERIAL": 16624, "JASA PASANG": 4346, "JASA BONGKAR": 0},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "KONTRUKSI TM - 1", "NAMA MATERIAL": "SINGLE ARM BAND 8\" (T = 6 MM X 42 MM) HDG TM LENGKAP NUT-HDG", "HARGA MATERIAL": 0, "JASA PASANG": 92248, "JASA BONGKAR": 0},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "KONTRUKSI TM - 1", "NAMA MATERIAL": "SINGLE GUY WIRE BAND 7\" - (T = 6 MM X 42 MM) HDG TM LENGKAP NUT-HDG", "HARGA MATERIAL": 17626, "JASA PASANG": 2650, "JASA BONGKAR": 0},
        {"JENIS KONSTRUKSI": "GTT 1 TIANG", "TYPE KONSTRUKSI": "KONTRUKSI TM - 1", "NAMA MATERIAL": "PREFORMED TERMINATION 35 MM (542/U/2009)", "HARGA MATERIAL": 73261, "JASA PASANG": 4635, "JASA BONGKAR": 0},
    ])

df_master = load_master_material()

# Header Tampilan
st.title("⚡ SISTEM ENTRI MATERIAL PLN")
st.caption("Aplikasi Input Rekap Material & Estimasi Biaya Pekerjaan")

tab1, tab2 = st.tabs(["📝 Entri Pekerjaan Baru", "🔍 Cari & Edit Pekerjaan Dientri"])

# ------------------------------------------------------------------------------
# TAB 1: ENTRI PEKERJAAN BARU
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("📌 Informasi Header Pekerjaan")
    col1, col2 = st.columns(2)
    with col1:
        nama_pekerjaan = st.text_input("Nama Pekerjaan:", value="-")
        alamat_pekerjaan = st.text_input("Alamat Pekerjaan:", value="")
    with col2:
        jenis_pekerjaan = st.selectbox("Jenis Pekerjaan:", ["SUTM", "SKTM", "GTT 1 TIANG", "GTT 2 TIANG", "PENGANGKUTAN"])
        tanggal_transaksi = st.date_input("Tanggal Transaksi:", datetime.today())

    st.subheader("📦 Pilih & Masukkan Volume Material")
    col_a, col_b = st.columns(2)
    with col_a:
        list_j = sorted(df_master["JENIS KONSTRUKSI"].unique().tolist())
        sel_j = st.selectbox("Pilih Jenis Konstruksi:", list_j)
        
        df_t = df_master[df_master["JENIS KONSTRUKSI"] == sel_j]
        list_t = sorted(df_t["TYPE KONSTRUKSI"].unique().tolist())
        sel_t = st.selectbox("Pilih Type Konstruksi:", list_t)

    df_m = df_t[df_t["TYPE KONSTRUKSI"] == sel_t]
    with col_b:
        list_m = sorted(df_m["NAMA MATERIAL"].unique().tolist())
        sel_m = st.selectbox("Pilih Nama Material:", list_m)
        
        col_v1, col_v2, col_v3 = st.columns(3)
        v_mat = col_v1.number_input("Vol Material", min_value=0, value=0)
        v_pas = col_v2.number_input("Vol Pasang", min_value=0, value=0)
        v_bon = col_v3.number_input("Vol Bongkar", min_value=0, value=0)

    if "cart" not in st.session_state:
        st.session_state.cart = []

    if st.button("➕ Tambahkan Item Material ke Daftar", use_container_width=True):
        match = df_master[
            (df_master["JENIS KONSTRUKSI"] == sel_j) &
            (df_master["TYPE KONSTRUKSI"] == sel_t) &
            (df_master["NAMA MATERIAL"] == sel_m)
        ].iloc[0]

        st.session_state.cart.append({
            "JENIS KONSTRUKSI": sel_j,
            "TYPE KONSTRUKSI": sel_t,
            "NAMA MATERIAL": sel_m,
            "VOL MATERIAL": v_mat,
            "VOL PASANG": v_pas,
            "VOL BONGKAR": v_bon,
            "Harga Satuan": match["HARGA MATERIAL"],
            "Jasa Pasang Satuan": match["JASA PASANG"],
            "Jasa Bongkar Satuan": match["JASA BONGKAR"],
        })
        st.success("Item berhasil ditambahkan!")

    if st.session_state.cart:
        df_cart = pd.DataFrame(st.session_state.cart)
        df_cart["BIAYA PASANG"] = df_cart["VOL PASANG"] * df_cart["Jasa Pasang Satuan"]
        df_cart["BIAYA BONGKAR"] = df_cart["VOL BONGKAR"] * df_cart["Jasa Bongkar Satuan"]
        
        def calc_mat(row):
            return 0.0 if "PLN" in str(row["NAMA MATERIAL"]).upper() else row["VOL MATERIAL"] * row["Harga Satuan"]
            
        df_cart["HARGA MATERIAL"] = df_cart.apply(calc_mat, axis=1)
        tot = (df_cart["HARGA MATERIAL"] + df_cart["BIAYA PASANG"] + df_cart["BIAYA BONGKAR"]).sum()

        st.dataframe(df_cart[[
            "JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL",
            "VOL MATERIAL", "VOL PASANG", "VOL BONGKAR",
            "HARGA MATERIAL", "BIAYA PASANG", "BIAYA BONGKAR"
        ]], use_container_width=True)

        st.metric("TOTAL ESTIMASI BIAYA", f"Rp {tot:,.2f}")

        if st.button("🚀 SUBMIT KE GOOGLE SHEETS", type="primary"):
            payload_data = []
            for i, r in enumerate(df_cart.to_dict("records")):
                payload_data.append({
                    "NAMA PEKERJAAN": nama_pekerjaan,
                    "ALAMAT PEKERJAAN": alamat_pekerjaan,
                    "JENIS PEKERJAAN": jenis_pekerjaan,
                    "TANGGAL": str(tanggal_transaksi),
                    "JENIS KONSTRUKSI": r["JENIS KONSTRUKSI"],
                    "TYPE KONSTRUKSI": r["TYPE KONSTRUKSI"],
                    "NAMA MATERIAL": r["NAMA MATERIAL"],
                    "VOL MATERIAL": r["VOL MATERIAL"],
                    "VOL PASANG": r["VOL PASANG"],
                    "VOL BONGKAR": r["VOL BONGKAR"],
                    "HARGA MATERIAL": r["HARGA MATERIAL"],
                    "BIAYA PASANG": r["BIAYA PASANG"],
                    "BIAYA BONGKAR": r["BIAYA BONGKAR"],
                    "TOTAL ESTIMASI": float(tot) if i == 0 else ""
                })

            res = requests.post(WEBHOOK_URL, json={"action": "APPEND_ROWS", "payload": payload_data})
            if res.status_code in [200, 201]:
                st.success("Data berhasil tersimpan!")
                st.session_state.cart = []
                st.cache_data.clear()
                st.rerun()

# ------------------------------------------------------------------------------
# TAB 2: CARI & EDIT PEKERJAAN DIENTRI
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("🔍 Cari & Kelola Pekerjaan Terdaftar")
    
    if st.button("🔄 Reload / Ambil Data Terbaru dari Google Sheets"):
        st.cache_data.clear()
        st.rerun()

    @st.cache_data(ttl=5)
    def fetch_data():
        try:
            r = requests.get(WEBHOOK_URL, timeout=10)
            if r.status_code == 200:
                return pd.DataFrame(r.json())
            return pd.DataFrame()
        except:
            return pd.DataFrame()

    df_gsheet = fetch_data()

    if df_gsheet.empty:
        st.warning("⚠️ Belum ada data pekerjaan tersimpan di Google Sheets atau format kolom belum sesuai.")
        st.info("💡 Silakan submit minimal 1 data pekerjaan dari Tab 1 (Entri Pekerjaan Baru) terlebih dahulu.")
    else:
        # PERBAIKAN PENTING:
        # Menggunakan ALAMAT PEKERJAAN jika NAMA PEKERJAAN diisi "-" agar pilihan tidak kosong
        def generate_label(row):
            nama = str(row.get("NAMA PEKERJAAN", "")).strip()
            alamat = str(row.get("ALAMAT PEKERJAAN", "")).strip()
            if nama != "" and nama != "-":
                return f"{nama} ({alamat})"
            elif alamat != "":
                return f"Alamat: {alamat}"
            else:
                return "Pekerjaan Tanpa Nama"

        df_gsheet["LABEL_PILIHAN"] = df_gsheet.apply(generate_label, axis=1)
        pilihan = sorted(df_gsheet["LABEL_PILIHAN"].unique().tolist())

        pilihan_terpilih = st.selectbox("🎯 Pilih Pekerjaan:", pilihan)
        
        df_sub = df_gsheet[df_gsheet["LABEL_PILIHAN"] == pilihan_terpilih].copy()
        
        st.dataframe(df_sub[[
            "JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL",
            "VOL MATERIAL", "VOL PASANG", "VOL BONGKAR",
            "HARGA MATERIAL", "BIAYA PASANG", "BIAYA BONGKAR"
        ]], use_container_width=True)
