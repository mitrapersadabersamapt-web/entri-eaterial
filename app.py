import json
import datetime
import pandas as pd
import requests
import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Sistem Entri Material PLN",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 2. CUSTOM CSS UNTUK TAMPILAN
# ==========================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4f7fa;
    }
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
    label, .stSelectbox label, .stTextInput label, .stNumberInput label {
        color: #1e293b !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox > div > div, .stNumberInput input {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
        font-weight: 500 !important;
    }
    .section-title {
        color: #0f172a;
        font-weight: 700;
        font-size: 20px;
        margin-bottom: 15px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
    }
    .total-box {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 2px solid #dc2626 !important;
        padding: 18px 24px;
        border-radius: 12px;
        text-align: left;
        margin-top: 15px;
        margin-bottom: 20px;
        box-shadow: 0 0 10px rgba(220, 38, 38, 0.2);
    }
    .total-title {
        color: #dc2626;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .total-amount {
        color: #991b1b;
        font-size: 32px;
        font-weight: 800;
        margin-top: 4px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 3. URL GOOGLE APPS SCRIPT WEBHOOK
# ==========================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyyDW104My3hp0fnW-KLQOWyIkVBSZ4iQu1wXA9fH6Kw8P942IF1f5Hi-Tjf5lTYL-U/exec"

# ==========================================
# 4. LOAD & CLEANING MASTER DATABASE EXCEL
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
# 5. INISIALISASI SESSION STATE & CALLBACK AMAN
# ==========================================
if "keranjang" not in st.session_state:
    st.session_state.keranjang = []

if "pesan_sukses" not in st.session_state:
    st.session_state.pesan_sukses = False

# Gunakan key unik versi/counter untuk mereset widget input text secara aman
if "form_version" not in st.session_state:
    st.session_state.form_version = 0

def reset_seluruh_form():
    st.session_state.keranjang = []
    st.session_state.form_version += 1

# BANNER HEADER APLIKASI
st.markdown(
    """
    <div class="pln-header">
        <h1>⚡ SISTEM ENTRI MATERIAL PLN</h1>
        <p>Aplikasi Input Rekap Material & Estimasi Biaya Pekerjaan</p>
    </div>
""",
    unsafe_allow_html=True,
)

# NOTIFIKASI BERHASIL
if st.session_state.pesan_sukses:
    st.success("🎉 **DATA BERHASIL DISIMPAN KE GOOGLE SHEETS! FORM PEKERJAAN & KERANJANG TELAH DI-RESET.**")
    st.balloons()
    st.session_state.pesan_sukses = False

# TAB UTAMA
tab_entri, tab_kelola = st.tabs(["📝 Entri Pekerjaan Baru", "🔍 Cari & Edit Pekerjaan Dientri"])

# ==============================================================================
# TAB 1: ENTRI PEKERJAAN BARU
# ==============================================================================
with tab_entri:
    ver = st.session_state.form_version
    
    st.markdown('<div class="section-title">1. Header Data Pekerjaan (Opsional)</div>', unsafe_allow_html=True)
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        nama_pekerjaan = st.text_input(
            "NAMA PEKERJAAN (Opsional) :",
            placeholder="Masukkan Nama Pekerjaan (Boleh Dikosongkan)",
            key=f"input_nama_{ver}"
        )
        alamat_pekerjaan = st.text_area(
            "ALAMAT PEKERJAAN :",
            placeholder="Masukkan Alamat Lengkap Pekerjaan...",
            key=f"input_alamat_{ver}"
        )
    with col_h2:
        jenis_pekerjaan = st.selectbox(
            "JENIS PEKERJAAN :",
            ["SAR", "PFK", "PREVENTIF", "KEYPOINT", "PEMELIHARAAN JARINGAN"],
            key=f"input_jenis_{ver}"
        )
        tanggal = st.date_input("TANGGAL :", key=f"input_tanggal_{ver}")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">2. Pilih Material Per Konstruksi</div>', unsafe_allow_html=True)
    col_k1, col_k2 = st.columns(2)

    list_jenis = sorted(df_master["JENIS KONSTRUKSI"].unique().tolist())
    with col_k1:
        jenis_selected = st.selectbox("1. Pilih Jenis Konstruksi:", list_jenis, key="entri_j_konst")

    df_filtered_jenis = df_master[df_master["JENIS KONSTRUKSI"] == jenis_selected]
    with col_k2:
        list_type = sorted(df_filtered_jenis["TYPE KONSTRUKSI"].unique().tolist())
        type_selected = st.selectbox("2. Pilih Type Konstruksi:", list_type, key="entri_t_konst")

    df_filtered = df_filtered_jenis[df_filtered_jenis["TYPE KONSTRUKSI"] == type_selected].copy()
    st.caption("☑️ **Tandai / Centang material yang akan dipakai di bawah ini, lalu klik tombol tambah ke keranjang:**")

    df_filtered["Pilih"] = False
    df_pilihan_display = df_filtered[["Pilih", "NAMA MATERIAL"]].rename(columns={"NAMA MATERIAL": "Nama Material"})

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

    if st.button("➕ Masukkan Material Terpilih ke Keranjang", type="primary", key="btn_add_katalog"):
        mat_terpilih = selected_materials_editor[selected_materials_editor["Pilih"] == True]["Nama Material"].tolist()
        if not mat_terpilih:
            st.warning("⚠️ Harap centang minimal satu material terlebih dahulu!")
        else:
            jumlah_ditambah = 0
            for mat in mat_terpilih:
                item_baru = {
                    "Jenis Konstruksi": jenis_selected,
                    "Type Konstruksi": type_selected,
                    "Material": mat,
                    "Volume Material": 0,
                    "Volume Pasang": 0,
                    "Volume Bongkar": 0,
                }
                st.session_state.keranjang.append(item_baru)
                jumlah_ditambah += 1
            st.toast(f"✅ Berhasil menambahkan {jumlah_ditambah} material ke keranjang!")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">3. Material Tambahan</div>', unsafe_allow_html=True)
    with st.expander("➕ **Klik di sini untuk menambah Material Tambahan di luar paket konstruksi**", expanded=False):
        all_materials = sorted(df_master["NAMA MATERIAL"].unique().tolist())
        material_tambahan = st.selectbox("Pilih / Cari Nama Material Tambahan:", all_materials, key="mat_tambahan")
        
        col_tv1, col_tv2, col_tv3 = st.columns(3)
        with col_tv1:
            vol_mat_t = st.number_input("Vol Material", min_value=0, value=0, step=1, key="vol_mat_t")
        with col_tv2:
            vol_pasang_t = st.number_input("Vol Pasang", min_value=0, value=0, step=1, key="vol_pasang_t")
        with col_tv3:
            vol_bongkar_t = st.number_input("Vol Bongkar", min_value=0, value=0, step=1, key="vol_bongkar_t")
                
        def tambah_material_tambahan():
            if vol_mat_t == 0 and vol_pasang_t == 0 and vol_bongkar_t == 0:
                st.warning("⚠️ Harap isi minimal salah satu volume lebih dari 0!")
                return
            
            matched = df_master[df_master["NAMA MATERIAL"] == material_tambahan]
            if not matched.empty:
                j_konst_auto = matched.iloc[0]["JENIS KONSTRUKSI"]
                t_konst_auto = matched.iloc[0]["TYPE KONSTRUKSI"]
            else:
                j_konst_auto = "MATERIAL TAMBAHAN"
                t_konst_auto = "TAMBAHAN"

            item_tambahan = {
                "Jenis Konstruksi": j_konst_auto,
                "Type Konstruksi": t_konst_auto,
                "Material": material_tambahan,
                "Volume Material": int(vol_mat_t),
                "Volume Pasang": int(vol_pasang_t),
                "Volume Bongkar": int(vol_bongkar_t),
            }
            st.session_state.keranjang.append(item_tambahan)
            st.toast("✅ Material Tambahan berhasil masuk ke keranjang!")

        st.button("➕ Tambahkan Material Tambahan", on_click=tambah_material_tambahan, key="btn_add_tambahan")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">4. Keranjang Input Material (Isi & Edit Volume di Sini)</div>', unsafe_allow_html=True)
    if st.session_state.keranjang:
        df_cart_raw = pd.DataFrame(st.session_state.keranjang)
        merged = pd.merge(
            df_cart_raw, df_master,
            left_on=["Jenis Konstruksi", "Type Konstruksi", "Material"],
            right_on=["JENIS KONSTRUKSI", "TYPE KONSTRUKSI", "NAMA MATERIAL"],
            how="left",
        )
        df_cart_raw["Harga Satuan"] = merged["HARGA MATERIAL"].fillna(0.0)
        df_cart_raw["Jasa Pasang Satuan"] = merged["JASA PASANG"].fillna(0.0)
        df_cart_raw["Jasa Bongkar Satuan"] = merged["JASA BONGKAR"].fillna(0.0)

        df_cart_raw["Biaya Pasang"] = df_cart_raw["Volume Pasang"] * df_cart_raw["Jasa Pasang Satuan"]
        df_cart_raw["Biaya Bongkar"] = df_cart_raw["Volume Bongkar"] * df_cart_raw["Jasa Bongkar Satuan"]

        def hitung_biaya_material(row):
            return 0.0 if "PLN" in str(row["Material"]).upper() else row["Volume Material"] * row["Harga Satuan"]

        df_cart_raw["Harga Material"] = df_cart_raw.apply(hitung_biaya_material, axis=1)
        df_cart_raw["Subtotal"] = df_cart_raw["Harga Material"] + df_cart_raw["Biaya Pasang"] + df_cart_raw["Biaya Bongkar"]

        edited_df = st.data_editor(
            df_cart_raw[[
                "Jenis Konstruksi", "Type Konstruksi", "Material",
                "Volume Material", "Volume Pasang", "Volume Bongkar",
                "Harga Material", "Biaya Pasang", "Biaya Bongkar", "Subtotal"
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
            use_container_width=True, hide_index=True, key=f"editor_keranjang_{ver}"
        )

        st.session_state.keranjang = edited_df[[
            "Jenis Konstruksi", "Type Konstruksi", "Material", 
            "Volume Material", "Volume Pasang", "Volume Bongkar"
        ]].to_dict("records")

        total_biaya = edited_df["Subtotal"].sum()
        df_hasil = edited_df
    else:
        st.info("💡 Keranjang masih kosong. Silakan centang material dari paket konstruksi atau gunakan Material Tambahan.")
        total_biaya = 0.0
        df_hasil = pd.DataFrame()

    # KOTAK TOTAL ESTIMASI BINGKAI MERAH
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
        if st.button("🗑️ Kosongkan Keranjang", use_container_width=True, key="btn_reset"):
            st.session_state.keranjang = []
            st.rerun()

    with col_act2:
        if st.button("🚀 SUBMIT DATA KE GOOGLE SHEETS", type="primary", use_container_width=True, key="btn_submit"):
            if not st.session_state.keranjang:
                st.error("❌ Keranjang masih kosong!")
            else:
                try:
                    nama_pekerjaan_kirim = nama_pekerjaan.strip() if nama_pekerjaan.strip() else "-"
                    alamat_pekerjaan_kirim = alamat_pekerjaan.strip() if alamat_pekerjaan.strip() else "-"
                    payload = []
                    records = df_hasil.to_dict("records")
                    
                    for idx, item in enumerate(records):
                        estimasi_val = round(float(total_biaya), 2) if idx == 0 else ""
                        
                        payload.append({
                            "NAMA PEKERJAAN": nama_pekerjaan_kirim,
                            "ALAMAT PEKERJAAN": alamat_pekerjaan_kirim,
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
                            "TOTAL ESTIMASI": estimasi_val,
                        })

                    with st.spinner("Sedang mengunggah data ke Google Sheets..."):
                        response = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=20)

                    if response.status_code == 200:
                        reset_seluruh_form()
                        st.session_state.pesan_sukses = True
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"⚠️ Gagal mengirim data. Status Code: {response.status_code}")
                except Exception as e:
                    st.error(f"⚠️ Terjadi kesalahan saat mengirim: {e}")

# ==============================================================================
# TAB 2: CARI & EDIT PEKERJAAN DIENTRI
# ==============================================================================
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

    if df_gsheet.empty or "NAMA PEKERJAAN" not in df_gsheet.columns:
        st.warning("⚠️ Belum ada data pekerjaan tersimpan di Google Sheets atau format kolom belum sesuai.")
        st.info("💡 Silakan submit minimal 1 data pekerjaan dari **Tab 1 (Entri Pekerjaan Baru)** terlebih dahulu.")
    else:
        list_pekerjaan = [p for p in df_gsheet["NAMA PEKERJAAN"].dropna().unique().tolist() if str(p).strip() != "" and str(p).strip() != "-"]

        if not list_pekerjaan:
            st.warning("⚠️ Belum ada nama pekerjaan yang tersimpan.")
        else:
            pekerjaan_selected = st.selectbox("🎯 Pilih Pekerjaan yang Akan Dikelola / Diedit:", list_pekerjaan)

            df_pekerjaan_edit = df_gsheet[df_gsheet["NAMA PEKERJAAN"] == pekerjaan_selected].copy()
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
                key=f"edit_sheet_{pekerjaan_selected}"
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
                    st.success(f"Material '{m_edit}' berhasil disisipkan! Jangan lupa klik tombol Simpan di bawah.")

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
                    df_gsheet_sisa = df_gsheet[df_gsheet["NAMA PEKERJAAN"] != pekerjaan_selected].copy()

                    edited_sheet_df["NAMA PEKERJAAN"] = header_info.get("NAMA PEKERJAAN", "-")
                    edited_sheet_df["ALAMAT PEKERJAAN"] = header_info.get("ALAMAT PEKERJAAN", "-")
                    edited_sheet_df["JENIS PEKERJAAN"] = header_info.get("JENIS PEKERJAAN", "-")
                    edited_sheet_df["TANGGAL"] = str(header_info.get("TANGGAL", "-"))
                    
                    edited_sheet_df["TOTAL ESTIMASI"] = ""
                    if not edited_sheet_df.empty:
                        edited_sheet_df.iloc[0, edited_sheet_df.columns.get_loc("TOTAL ESTIMASI")] = float(total_estimasi_baru)

                    df_final_all = pd.concat([df_gsheet_sisa, edited_sheet_df], ignore_index=True)

                    payload_update = {
                        "action": "OVERWRITE_ALL",
                        "payload": df_final_all.to_dict("records")
                    }

                    with st.spinner("Menyimpan pembaruan ke Google Sheets..."):
                        res_update = requests.post(WEBHOOK_URL, data=json.dumps(payload_update), headers={"Content-Type": "application/json"}, timeout=20)

                    if res_update.status_code == 200:
                        st.success("✅ Data berhasil diperbarui di Google Sheets!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"⚠️ Gagal memperbarui data. Status code: {res_update.status_code}")

                except Exception as ex:
                    st.error(f"⚠️ Terjadi kesalahan saat menyimpan: {ex}")
