import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# ==============================================================================
# CONFIGURASI HALAMAN
# ==============================================================================
st.set_page_config(
    page_title="Sistem Entri Material PLN",
    page_icon="⚡",
    layout="wide"
)

# URL Apps Script Web App (Webhook Google Sheets)
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbz_CONTOH_DEPLOYMENT_ID_ANDA/exec" 

# ==============================================================================
# CSS CUSTOM DESIGN
# ==============================================================================
st.markdown("""
<style>
    .main-header {
        background-color: #007bff;
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 25px;
    }
    .main-header h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 700;
    }
    .main-header p {
        margin: 5px 0 0 0;
        opacity: 0.9;
    }
    .total-box {
        background-color: #e9f5ff;
        border: 2px solid #007bff;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .total-title {
        font-size: 16px;
        font-weight: bold;
        color: #0056b3;
    }
    .total-amount {
        font-size: 28px;
        font-weight: bold;
        color: #28a745;
    }
    .section-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 15px;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# Header Utama
st.markdown("""
<div class="main-header">
    <h1>⚡ SISTEM ENTRI MATERIAL PLN</h1>
    <p>Aplikasi Input Rekap Material & Estimasi Biaya Pekerjaan</p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# MASTER DATA MATERIAL & JASA (STUB / LOCAL DATABASE)
# ==============================================================================
@st.cache_data
def get_master_material():
    # Data master material & harga satuan PLN
    data_master = [
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
    ]
    return pd.DataFrame(data_master)

df_master = get_master_material()

# ==============================================================================
# TAB MANAJEMEN APLIKASI
# ==============================================================================
tab_baru, tab_kelola = st.tabs(["📝 Entri Pekerjaan Baru", "🔍 Cari & Edit Pekerjaan Dientri"])

# ------------------------------------------------------------------------------
# TAB 1: ENTRI PEKERJAAN BARU
# ------------------------------------------------------------------------------
with tab_baru:
    st.markdown('<div class="section-title">📌 Informasi Header Pekerjaan</div>', unsafe_allow_html=True)
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        nama_pekerjaan = st.text_input("Nama Pekerjaan:", value="-", help="Bisa diisi '-' jika tidak ada nama pekerjaan spesifik")
        alamat_pekerjaan = st.text_input("Alamat Pekerjaan:", value="")
    with col_h2:
        jenis_pekerjaan = st.selectbox("Jenis Pekerjaan:", ["SUTM", "SKTM", "GTT 1 TIANG", "GTT 2 TIANG", "PENGANGKUTAN"])
        tanggal = st.date_input("Tanggal Transaksi:", datetime.today())

    st.markdown("---")
    st.markdown('<div class="section-title">📦 Pilih & Masukkan Volume Material</div>', unsafe_allow_html=True)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        list_j_konstruksi = sorted(df_master["JENIS KONSTRUKSI"].unique().tolist())
        sel_j_konstruksi = st.selectbox("Pilih Jenis Konstruksi:", list_j_konstruksi, key="new_j")
        
        df_filtered_t = df_master[df_master["JENIS KONSTRUKSI"] == sel_j_konstruksi]
        list_t_konstruksi = sorted(df_filtered_t["TYPE KONSTRUKSI"].unique().tolist())
        sel_t_konstruksi = st.selectbox("Pilih Type Konstruksi:", list_t_konstruksi, key="new_t")

    df_filtered_m = df_filtered_t[df_filtered_t["TYPE KONSTRUKSI"] == sel_t_konstruksi]
    
    # State untuk menyimpan item material sementara
    if "temp_items" not in st.session_state:
        st.session_state.temp_items = []

    with col_m2:
        sel_material = st.selectbox("Pilih Nama Material:", sorted(df_filtered_m["NAMA MATERIAL"].unique().tolist()), key="new_m")
        col_v1, col_v2, col_v3 = st.columns(3)
        v_mat = col_v1.number_input("Vol Material", min_value=0, value=0, step=1)
        v_pas = col_v2.number_input("Vol Pasang", min_value=0, value=0, step=1)
        v_bon = col_v3.number_input("Vol Bongkar", min_value=0, value=0, step=1)

    if st.button("➕ Tambahkan Item Material ke Daftar", use_container_width=True):
        if v_mat == 0 and v_pas == 0 and v_bon == 0:
            st.warning("⚠️ Masukkan minimal salah satu Volume (Material / Pasang / Bongkar) lebih besar dari 0.")
        else:
            item_match = df_master[
                (df_master["JENIS KONSTRUKSI"] == sel_j_konstruksi) &
                (df_master["TYPE KONSTRUKSI"] == sel_t_konstruksi) &
                (df_master["NAMA MATERIAL"] == sel_material)
            ].iloc[0]

            st.session_state.temp_items.append({
                "JENIS KONSTRUKSI": sel_j_konstruksi,
                "TYPE KONSTRUKSI": sel_t_konstruksi,
                "NAMA MATERIAL": sel_material,
                "VOL MATERIAL": v_mat,
                "VOL PASANG": v_pas,
                "VOL BONGKAR": v_bon,
                "Harga Satuan": item_match["HARGA MATERIAL"],
                "Jasa Pasang Satuan": item_match["JASA PASANG"],
                "Jasa Bongkar Satuan": item_match["JASA BONGKAR"],
            })
            st.success(f"Berhasil menambahkan '{sel_material}'!")

    # Tampilkan Tabel Sementara jika ada item
    if st.session_state.temp_items:
        st.markdown("### Daftar Material Yang Akan Disimpan:")
        df_temp = pd.DataFrame(st.session_state.temp_items)
        
        # Hitung Biaya
        df_temp["BIAYA PASANG"] = df_temp["VOL PASANG"] * df_temp["Jasa Pasang Satuan"]
        df_temp["BIAYA BONGKAR"] = df_temp["VOL BONGKAR"] * df_temp["Jasa Bongkar Satuan"]
        
        def hitung_mat(row):
            return 0.0 if "PLN" in str(row["NAMA MATERIAL"]).upper() else row["VOL MATERIAL"] * row["Harga Satuan"]
            
        df_temp["HARGA MATERIAL"] = df_temp.apply(hitung_mat, axis=1)
        subtotal = df_temp["HARGA MATERIAL"] + df_temp["BIAYA PASANG"] + df_temp["BIAYA BONGKAR"]
        total_estimasi = subtotal.sum()

        st.dataframe(df_temp[[
            "JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL",
            "VOL MATERIAL", "VOL PASANG", "VOL BONGKAR",
            "HARGA MATERIAL", "BIAYA PASANG", "BIAYA BONGKAR"
        ]], use_container_width=True)

        st.markdown(
            f"""
            <div class="total-box">
                <div class="total-title">💰 TOTAL ESTIMASI BIAYA PEKERJAAN</div>
                <div class="total-amount">Rp {total_estimasi:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_b1, col_b2 = st.columns(2)
        if col_b1.button("🗑️ Kosongkan Daftar", use_container_width=True):
            st.session_state.temp_items = []
            st.rerun()

        if col_b2.button("🚀 SUBMIT PEKERJAAN KE GOOGLE SHEETS", type="primary", use_container_width=True):
            if not alamat_pekerjaan.strip():
                st.error("⚠️ Alamat Pekerjaan wajib diisi!")
            else:
                rows_payload = []
                for idx, r in enumerate(df_temp.to_dict("records")):
                    rows_payload.append({
                        "NAMA PEKERJAAN": nama_pekerjaan,
                        "ALAMAT PEKERJAAN": alamat_pekerjaan,
                        "JENIS PEKERJAAN": jenis_pekerjaan,
                        "TANGGAL": tanggal.strftime("%Y-%m-%d"),
                        "JENIS KONSTRUKSI": r["JENIS KONSTRUKSI"],
                        "TYPE KONSTRUKSI": r["TYPE KONSTRUKSI"],
                        "NAMA MATERIAL": r["NAMA MATERIAL"],
                        "VOL MATERIAL": r["VOL MATERIAL"],
                        "VOL PASANG": r["VOL PASANG"],
                        "VOL BONGKAR": r["VOL BONGKAR"],
                        "HARGA MATERIAL": r["HARGA MATERIAL"],
                        "BIAYA PASANG": r["BIAYA PASANG"],
                        "BIAYA BONGKAR": r["BIAYA BONGKAR"],
                        "TOTAL ESTIMASI": float(total_estimasi) if idx == 0 else ""
                    })

                payload = {
                    "action": "APPEND_ROWS",
                    "payload": rows_payload
                }

                try:
                    with st.spinner("Mengirim data ke Google Sheets..."):
                        res = requests.post(
                            WEBHOOK_URL,
                            data=json.dumps(payload),
                            headers={"Content-Type": "application/json"},
                            timeout=25,
                            allow_redirects=True
                        )
                    if res.status_code in [200, 201, 302]:
                        st.success("✅ Data pekerjaan berhasil tersimpan di Google Sheets!")
                        st.session_state.temp_items = []
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"⚠️ Gagal menyimpan. Response Status: {res.status_code}")
                except Exception as e:
                    st.error(f"⚠️ Terjadi error saat menghubungi server: {e}")

# ------------------------------------------------------------------------------
# TAB 2: CARI & EDIT PEKERJAAN DIENTRI
# ------------------------------------------------------------------------------
with tab_kelola:
    st.markdown('<div class="section-title">🔍 Cari & Kelola Pekerjaan Terdaftar</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Reload / Ambil Data Terbaru dari Google Sheets", key="btn_fetch"):
        st.cache_data.clear()
        st.rerun()
    
    @st.cache_data(ttl=5)
    def fetch_sheet_data():
        try:
            res = requests.get(WEBHOOK_URL, timeout=15)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    df = pd.DataFrame(data)
                    df.columns = df.columns.astype(str).str.strip()
                    return df
            return pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    df_gsheet = fetch_sheet_data()

    if df_gsheet.empty:
        st.warning("⚠️ Belum ada data pekerjaan tersimpan di Google Sheets atau format kolom belum sesuai.")
        st.info("💡 Silakan submit minimal 1 data pekerjaan dari Tab 1 (Entri Pekerjaan Baru) terlebih dahulu.")
    else:
        # Fungsi pembantu untuk membuat nama label pilihan drop down yang cerdas
        def buat_label_pekerjaan(row):
            nama = str(row.get("NAMA PEKERJAAN", "")).strip()
            alamat = str(row.get("ALAMAT PEKERJAAN", "")).strip()
            jenis = str(row.get("JENIS PEKERJAAN", "")).strip()
            
            if nama != "" and nama != "-":
                return f"{nama} | ({alamat})"
            elif alamat != "" and alamat != "-":
                return f"[{jenis}] Alamat: {alamat}"
            else:
                return f"Pekerjaan Tanpa Nama"

        df_gsheet["LABEL_TAMPILAN"] = df_gsheet.apply(buat_label_pekerjaan, axis=1)
        list_label = sorted(df_gsheet["LABEL_TAMPILAN"].unique().tolist())

        if not list_label:
            st.warning("⚠️ Belum ada data pekerjaan yang tersimpan.")
        else:
            label_selected = st.selectbox("🎯 Pilih Pekerjaan yang Akan Dikelola / Diedit:", list_label)

            df_pekerjaan_edit = df_gsheet[df_gsheet["LABEL_TAMPILAN"] == label_selected].copy()
            header_info = df_pekerjaan_edit.iloc[0]
            
            st.info(f"📌 **Detail Pekerjaan:** {header_info.get('NAMA PEKERJAAN', '-')} | **Jenis:** {header_info.get('JENIS PEKERJAAN', '-')} | **Alamat:** {header_info.get('ALAMAT PEKERJAAN', '-')} | **Tanggal:** {header_info.get('TANGGAL', '-')}")

            st.markdown("---")
            st.markdown("### 1. Edit Volume / Hapus Material Terdaftar")
            
            cols_num = ["VOL MATERIAL", "VOL PASANG", "VOL BONGKAR", "HARGA MATERIAL", "BIAYA PASANG", "BIAYA BONGKAR"]
            for c in cols_num:
                if c in df_pekerjaan_edit.columns:
                    df_pekerjaan_edit[c] = pd.to_numeric(df_pekerjaan_edit[c], errors="coerce").fillna(0)

            edited_sheet_df = st.data_editor(
                df_pekerjaan_edit[[
                    "JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL",
                    "VOL MATERIAL", "VOL PASANG", "VOL BONGKAR"
                ]],
                column_config={
                    "JENIS KONSTRUKSI": st.column_config.TextColumn("Jenis Konstruksi", disabled=True),
                    "TYPE KONSTRUKSI": st.column_config.TextColumn("Type Konstruksi", disabled=True),
                    "NAMA MATERIAL": st.column_config.TextColumn("Nama Material", disabled=True),
                    "VOL MATERIAL": st.column_config.NumberColumn("Vol Material", min_value=0, step=1),
                    "VOL PASANG": st.column_config.NumberColumn("Vol Pasang", min_value=0, step=1),
                    "VOL BONGKAR": st.column_config.NumberColumn("Vol Bongkar", min_value=0, step=1),
                },
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key=f"edit_sheet_{label_selected}"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 2. Tambah Material Baru ke Pekerjaan Ini")
            
            with st.expander("➕ **Klik untuk menambah material baru pada pekerjaan terpilih ini**"):
                col_e1, col_e2 = st.columns(2)
                list_j_edit = sorted(df_master["JENIS KONSTRUKSI"].unique().tolist())
                with col_e1:
                    j_edit = st.selectbox("Jenis Konstruksi:", list_j_edit, key="j_edit")
                    df_m_j = df_master[df_master["JENIS KONSTRUKSI"] == j_edit]
                    t_edit = st.selectbox("Type Konstruksi:", sorted(df_m_j["TYPE KONSTRUKSI"].unique().tolist()), key="t_edit")
                
                df_m_t = df_m_j[df_m_j["TYPE KONSTRUKSI"] == t_edit]
                with col_e2:
                    m_edit = st.selectbox("Nama Material:", sorted(df_m_t["NAMA MATERIAL"].unique().tolist()), key="m_edit")
                    col_ev1, col_ev2, col_ev3 = st.columns(3)
                    v_mat_e = col_ev1.number_input("Vol Mat", min_value=0, value=0, step=1, key="v_mat_e")
                    v_pas_e = col_ev2.number_input("Vol Pasang", min_value=0, value=0, step=1, key="v_pas_e")
                    v_bon_e = col_ev3.number_input("Vol Bongkar", min_value=0, value=0, step=1, key="v_bon_e")

                if st.button("➕ Sisipkan Material ke Pekerjaan", key="btn_insert_mat"):
                    row_baru = pd.DataFrame([{
                        "JENIS KONSTRUKSI": j_edit,
                        "TYPE KONSTRUKSI": t_edit,
                        "NAMA MATERIAL": m_edit,
                        "VOL MATERIAL": v_mat_e,
                        "VOL PASANG": v_pas_e,
                        "VOL BONGKAR": v_bon_e,
                    }])
                    edited_sheet_df = pd.concat([edited_sheet_df, row_baru], ignore_index=True)
                    st.success(f"Material '{m_edit}' berhasil disisipkan! Klik SIMPAN di bawah untuk mengonfirmasi.")

            merged_edit = pd.merge(
                edited_sheet_df, df_master,
                left_on=["JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL"],
                right_on=["JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL"],
                how="left"
            )
            
            edited_sheet_df["Harga Satuan"] = merged_edit["HARGA MATERIAL"].fillna(0.0)
            edited_sheet_df["Jasa Pasang Satuan"] = merged_edit["JASA PASANG"].fillna(0.0)
            edited_sheet_df["Jasa Bongkar Satuan"] = merged_edit["JASA BONGKAR"].fillna(0.0)

            edited_sheet_df["BIAYA PASANG"] = edited_sheet_df["VOL PASANG"] * edited_sheet_df["Jasa Pasang Satuan"]
            edited_sheet_df["BIAYA BONGKAR"] = edited_sheet_df["VOL BONGKAR"] * edited_sheet_df["Jasa Bongkar Satuan"]

            def hitung_mat_edit(row):
                return 0.0 if "PLN" in str(row["NAMA MATERIAL"]).upper() else row["VOL MATERIAL"] * row["Harga Satuan"]

            edited_sheet_df["HARGA MATERIAL"] = edited_sheet_df.apply(hitung_mat_edit, axis=1)
            subtotal_edit = edited_sheet_df["HARGA MATERIAL"] + edited_sheet_df["BIAYA PASANG"] + edited_sheet_df["BIAYA BONGKAR"]
            total_estimasi_baru = subtotal_edit.sum()

            st.markdown(
                f"""
                <div class="total-box">
                    <div class="total-title">💰 REKAP ESTIMASI HARGA SETELAH DIEDIT</div>
                    <div class="total-amount">Rp {total_estimasi_baru:,.2f}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

            if st.button("💾 SIMPAN PERUBAHAN KE GOOGLE SHEETS", type="primary", use_container_width=True, key="btn_save_edit"):
                try:
                    df_gsheet_sisa = df_gsheet[df_gsheet["LABEL_TAMPILAN"] != label_selected].copy()

                    edited_sheet_df["NAMA PEKERJAAN"] = header_info.get("NAMA PEKERJAAN", "-")
                    edited_sheet_df["ALAMAT PEKERJAAN"] = header_info.get("ALAMAT PEKERJAAN", "-")
                    edited_sheet_df["JENIS PEKERJAAN"] = header_info.get("JENIS PEKERJAAN", "-")
                    edited_sheet_df["TANGGAL"] = str(header_info.get("TANGGAL", "-"))
                    
                    edited_sheet_df["TOTAL ESTIMASI"] = ""
                    if not edited_sheet_df.empty:
                        edited_sheet_df.iloc[0, edited_sheet_df.columns.get_loc("TOTAL ESTIMASI")] = float(total_estimasi_baru)

                    # Hapus kolom pembantu sebelum dikirim balik ke Google Sheets
                    df_gsheet_sisa = df_gsheet_sisa.drop(columns=["LABEL_TAMPILAN"], errors="ignore")
                    edited_sheet_clean = edited_sheet_df.drop(columns=["LABEL_TAMPILAN", "Harga Satuan", "Jasa Pasang Satuan", "Jasa Bongkar Satuan"], errors="ignore")

                    df_final_all = pd.concat([df_gsheet_sisa, edited_sheet_clean], ignore_index=True)

                    payload_update = {
                        "action": "OVERWRITE_ALL",
                        "payload": df_final_all.to_dict("records")
                    }

                    with st.spinner("Menyimpan pembaruan ke Google Sheets..."):
                        res_update = requests.post(
                            WEBHOOK_URL, 
                            data=json.dumps(payload_update), 
                            headers={"Content-Type": "application/json"}, 
                            timeout=25,
                            allow_redirects=True
                        )

                    if res_update.status_code in [200, 201, 302]:
                        st.success("✅ Data berhasil diperbarui di Google Sheets!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"⚠️ Gagal memperbarui data. Status code: {res_update.status_code}")

                except Exception as ex:
                    st.error(f"⚠️ Terjadi kesalahan saat menyimpan: {ex}")
