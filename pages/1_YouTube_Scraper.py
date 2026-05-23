import streamlit as st
import pandas as pd
import time
import re
import json
from datetime import datetime, timezone
from googleapiclient.discovery import build
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="YouTube Scraper", page_icon="", layout="centered")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.block-container {
    max-width: 720px !important;
    padding: 3rem 2rem 6rem !important;
    margin: 0 auto;
}
#MainMenu, footer, header {visibility: hidden;}

.page-title {
    font-size: 2rem;
    font-weight: 800;
    color: #111;
    margin: 0 0 0.25rem;
    letter-spacing: -0.02em;
}
.page-sub {
    font-size: 0.95rem;
    color: #888;
    margin: 0 0 2rem;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    border: 1.5px solid #ddd !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
    color: #111 !important;
    background: #fff !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #111 !important;
    box-shadow: 0 0 0 3px rgba(0,0,0,0.06) !important;
}
label, .stTextInput label, .stNumberInput label, .stTextArea label {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: #555 !important;
    letter-spacing: 0.02em !important;
    text-transform: uppercase !important;
}

/* Tombol utama — normal, tidak fixed */
.stButton > button {
    background: #111 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    padding: 0.65rem 1.5rem !important;
    width: 100% !important;
    transition: background 0.15s !important;
    margin-top: 1rem !important;
}
.stButton > button:hover {
    background: #333 !important;
}
.divider {
    border: none;
    border-top: 1px solid #ebebeb;
    margin: 2rem 0;
}
.step-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 1.25rem 0 0.5rem;
}
.step-num {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: #111;
    color: #fff;
    font-size: 0.75rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.step-text {
    font-size: 0.88rem;
    font-weight: 600;
    color: #111;
}
.metric-row {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
}
.metric-box {
    flex: 1;
    background: #f9f9f9;
    border: 1px solid #ebebeb;
    border-radius: 12px;
    padding: 1.1rem;
    text-align: center;
}
.metric-num {
    font-size: 2rem;
    font-weight: 800;
    color: #111;
    line-height: 1;
    margin-bottom: 0.35rem;
}
.metric-num.green { color: #1a7a4a; }
.metric-num.red   { color: #b0281a; }
.metric-lbl {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #aaa;
}
.stDownloadButton > button {
    border: 1.5px solid #ddd !important;
    border-radius: 10px !important;
    background: #fff !important;
    color: #111 !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    width: 100% !important;
}
.stDownloadButton > button:hover {
    border-color: #111 !important;
    background: #fafafa !important;
}
.sheets-badge {
    display: inline-block;
    background: #e6f4ea;
    color: #1a7a4a;
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    font-size: 0.78rem;
    font-weight: 600;
    margin-left: 0.5rem;
}
.sheets-badge.error {
    background: #fce8e6;
    color: #b0281a;
}
</style>
""", unsafe_allow_html=True)

# ── Daftar API Key ─────────────────────────────────────────────────
API_KEYS = {
    "API Key 1": "AIzaSyB9nUe2ThxR26Y8_RSA3y5JFaJx2hPSrQ8",
    "API Key 2": "AIzaSyBo6lZZ-CjO3O_Qv57ucqKltP8AOQOSErw"
    "KOSONG": "MASUKKAN_API_KEY_3_DISINI",
}

# ── Google Sheets Helper ───────────────────────────────────────────
def get_sheets_client():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
        )
        return gspread.authorize(creds)
    except Exception as e:
        return None

def get_existing_ids_from_sheets(client, spreadsheet_id):
    try:
        sh = client.open_by_key(spreadsheet_id)
        ws = sh.sheet1
        records = ws.get_all_records()
        ids = set()
        for r in records:
            if r.get("channel_id"):
                ids.add(str(r["channel_id"]))
            elif r.get("URL"):
                m = re.search(r'channel/([A-Za-z0-9_-]+)', str(r["URL"]))
                if m:
                    ids.add(m.group(1))
        return ids
    except:
        return set()

def push_to_sheets(client, spreadsheet_id, df):
    try:
        sh = client.open_by_key(spreadsheet_id)
        ws = sh.sheet1
        existing = ws.get_all_values()

        if not existing or existing == [[]]:
            # Sheet kosong — tulis header + data
            ws.update([df.columns.tolist()] + df.values.tolist())
        else:
            # Append di bawah data yang ada
            ws.append_rows(df.values.tolist())
        return True, len(df)
    except Exception as e:
        return False, str(e)

# ── Page Header ────────────────────────────────────────────────────
st.markdown('<p class="page-title">YouTube Channel Scraper</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Temukan channel YouTube yang sesuai kriteria buyer secara otomatis</p>', unsafe_allow_html=True)

# ── Config Form ────────────────────────────────────────────────────
with st.expander("Pengaturan & Filter", expanded=True):
    selected_label = st.selectbox("Pilih API Key", list(API_KEYS.keys()))
    api_key = API_KEYS[selected_label]
    key_preview = api_key[:8] + "..." + (api_key[-4:] if len(api_key) > 12 else "")
    st.markdown(
        f"<p style='font-size:0.78rem;color:#aaa;margin:0.25rem 0 0;'>"
        f"Key aktif: <code>{key_preview}</code></p>",
        unsafe_allow_html=True
    )

    st.markdown('<hr style="border:none;border-top:1px solid #ebebeb;margin:1rem 0">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        min_subs     = st.number_input("Min Subscriber", value=100000, step=10000)
        min_videos   = st.number_input("Min Jumlah Video", value=30, step=5)
        min_inactive = st.number_input("Tidak aktif minimal (bulan)", value=6, step=1)
    with col2:
        max_subs    = st.number_input("Max Subscriber", value=5000000, step=100000)
        max_year    = st.number_input("Dibuat sebelum tahun", value=2022, step=1)
        max_results = st.slider("Max hasil per keyword", 10, 50, 30)

    st.markdown('<hr style="border:none;border-top:1px solid #ebebeb;margin:1rem 0">', unsafe_allow_html=True)

    keywords_input = st.text_area(
        "Keywords (satu per baris)",
        value="resep masakan rumahan\nmasak sehari hari\notomotif modifikasi\nmusik original indonesia\ntips otomotif",
        height=140
    )

    st.markdown('<hr style="border:none;border-top:1px solid #ebebeb;margin:1rem 0">', unsafe_allow_html=True)

    # Google Sheets toggle
    use_sheets = st.toggle("Kirim hasil ke Google Sheets", value=False)
    if use_sheets:
        try:
            spreadsheet_id = st.secrets["sheets"]["spreadsheet_id"]
            sheet_preview = spreadsheet_id[:20]
            st.markdown(
                f"<p style='font-size:0.78rem;color:#1a7a4a;margin:0.25rem 0 0;'>"
                f"Spreadsheet ID: <code>{sheet_preview}...</code></p>",
                unsafe_allow_html=True
            )
        except:
            st.warning("Spreadsheet ID belum diset di Streamlit Secrets.")
            use_sheets = False

    st.markdown('<hr style="border:none;border-top:1px solid #ebebeb;margin:1rem 0">', unsafe_allow_html=True)

    uploaded_csv = st.file_uploader(
        "Upload CSV sebelumnya untuk skip duplikat (opsional)",
        type=["csv"]
    )
    if uploaded_csv:
        st.caption("Channel yang sudah ada di file ini akan otomatis dilewati.")

# ── Helper Functions ───────────────────────────────────────────────
def extract_email(text):
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, text)
    return emails[0] if emails else ""

def months_since(date_str):
    if not date_str:
        return 0
    try:
        last = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now  = datetime.now(timezone.utc)
        return round((now - last).days / 30, 1)
    except:
        return 0

def search_channels(youtube, keyword, max_results):
    ids = []
    try:
        res = youtube.search().list(
            part="snippet", q=keyword, type="channel",
            maxResults=min(50, max_results)
        ).execute()
        for item in res.get("items", []):
            ids.append(item["snippet"]["channelId"])
    except Exception as e:
        st.warning(f"Error search '{keyword}': {e}")
    return ids

def get_channel_details(youtube, channel_ids):
    results = []
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i+50]
        try:
            res = youtube.channels().list(
                part="snippet,statistics", id=",".join(batch)
            ).execute()
            for item in res.get("items", []):
                s   = item.get("snippet", {})
                st2 = item.get("statistics", {})
                pub = s.get("publishedAt", "")
                results.append({
                    "channel_id":          item["id"],
                    "Nama Channel":        s.get("title", ""),
                    "Subscriber":          int(st2.get("subscriberCount", 0)),
                    "Jumlah Video":        int(st2.get("videoCount", 0)),
                    "Total Views":         int(st2.get("viewCount", 0)),
                    "Tahun Dibuat":        int(pub[:4]) if pub else 9999,
                    "Tanggal Dibuat":      pub[:10] if pub else "",
                    "Negara":              s.get("country", "-"),
                    "Email":               extract_email(s.get("description", "")),
                    "URL":                 f"https://www.youtube.com/channel/{item['id']}",
                    "Upload Terakhir":     "",
                    "Tidak Aktif (bulan)": 0,
                    "Lolos Filter":        False,
                    "Alasan Gagal":        "",
                })
        except Exception as e:
            st.warning(f"Error detail: {e}")
        time.sleep(0.3)
    return results

def get_last_upload(youtube, channel_id):
    try:
        res = youtube.search().list(
            part="snippet", channelId=channel_id,
            order="date", maxResults=1, type="video"
        ).execute()
        items = res.get("items", [])
        if items:
            return items[0]["snippet"]["publishedAt"][:10]
    except:
        pass
    return None

def apply_filter(ch):
    reasons = []
    if ch["Subscriber"] < min_subs:
        reasons.append(f"subscriber {ch['Subscriber']:,} < {min_subs:,}")
    if ch["Subscriber"] > max_subs:
        reasons.append("subscriber terlalu besar")
    if ch["Jumlah Video"] < min_videos:
        reasons.append(f"video {ch['Jumlah Video']} < {min_videos}")
    if ch["Tahun Dibuat"] >= max_year:
        reasons.append(f"dibuat tahun {ch['Tahun Dibuat']}")
    if ch["Tidak Aktif (bulan)"] < min_inactive:
        reasons.append(f"masih aktif ({ch['Tidak Aktif (bulan)']} bln)")
    if reasons:
        ch["Alasan Gagal"] = " | ".join(reasons)
        ch["Lolos Filter"] = False
    else:
        ch["Lolos Filter"] = True
    return ch

# ── Run Button ─────────────────────────────────────────────────────
keywords = [k.strip() for k in keywords_input.strip().split("\n") if k.strip()]

st.button("Mulai Scraping", key="run_btn", use_container_width=True)
run = st.session_state.get("run_btn", False)

if run and not api_key.startswith("AIza"):
    st.warning("Masukkan YouTube API Key yang valid di pengaturan di atas.")
    st.stop()

if run and not keywords:
    st.error("Tambahkan minimal 1 keyword dulu.")
    st.stop()

if run:
    sheets_client = get_sheets_client() if use_sheets else None

    # Load existing IDs
    existing_ids = set()
    if use_sheets and sheets_client:
        spreadsheet_id = st.secrets["sheets"]["spreadsheet_id"]
        existing_ids = get_existing_ids_from_sheets(sheets_client, spreadsheet_id)
        if existing_ids:
            st.info(f"{len(existing_ids)} channel dari Google Sheets akan dilewati.")
    elif uploaded_csv is not None:
        try:
            df_existing = pd.read_csv(uploaded_csv)
            if "channel_id" in df_existing.columns:
                existing_ids = set(df_existing["channel_id"].dropna().tolist())
            elif "URL" in df_existing.columns:
                existing_ids = set(
                    df_existing["URL"].dropna()
                    .str.extract(r'channel/([A-Za-z0-9_-]+)')[0]
                    .dropna().tolist()
                )
            st.info(f"{len(existing_ids)} channel dari CSV akan dilewati.")
        except Exception as e:
            st.warning(f"Gagal baca CSV: {e}")

    youtube = build("youtube", "v3", developerKey=api_key)
    all_ids = []

    # Step 1
    st.markdown('<div class="step-row"><div class="step-num">1</div><div class="step-text">Search Channel</div></div>', unsafe_allow_html=True)
    prog1 = st.progress(0)
    stat1 = st.empty()
    for i, kw in enumerate(keywords):
        stat1.caption(f"Mencari: {kw}")
        ids = search_channels(youtube, kw, max_results)
        all_ids.extend(ids)
        prog1.progress((i + 1) / len(keywords))
        time.sleep(0.5)
    all_ids = list(set(all_ids) - existing_ids)
    stat1.caption(f"{len(all_ids)} channel baru ditemukan (duplikat dilewati)")

    # Step 2
    st.markdown('<div class="step-row"><div class="step-num">2</div><div class="step-text">Ambil Detail Channel</div></div>', unsafe_allow_html=True)
    prog2 = st.progress(0)
    stat2 = st.empty()
    stat2.caption("Mengambil data...")
    channels = get_channel_details(youtube, all_ids)
    prog2.progress(1.0)
    stat2.caption(f"{len(channels)} channel berhasil diambil")

    # Step 3
    st.markdown('<div class="step-row"><div class="step-num">3</div><div class="step-text">Cek Upload Terakhir & Filter</div></div>', unsafe_allow_html=True)
    prog3        = st.progress(0)
    stat3        = st.empty()
    live_table   = st.empty()
    partial_data = []

    for i, ch in enumerate(channels):
        last = get_last_upload(youtube, ch["channel_id"])
        ch["Upload Terakhir"]      = last or "-"
        ch["Tidak Aktif (bulan)"] = months_since(last)
        ch = apply_filter(ch)
        partial_data.append(ch)
        prog3.progress((i + 1) / len(channels))
        stat3.caption(f"Memproses {i+1}/{len(channels)}: {ch['Nama Channel']}")

        if (i + 1) % 5 == 0 or (i + 1) == len(channels):
            df_live = pd.DataFrame(partial_data).drop(columns=["channel_id"], errors="ignore")
            df_live = df_live.sort_values("Lolos Filter", ascending=False)
            live_table.dataframe(df_live, use_container_width=True, height=280)

        time.sleep(0.3)

    stat3.caption("Selesai.")

    # ── Push ke Google Sheets ──────────────────────────────────────
    if use_sheets and sheets_client and partial_data:
        spreadsheet_id = st.secrets["sheets"]["spreadsheet_id"]
        df_push = pd.DataFrame(partial_data)
        ok, result = push_to_sheets(sheets_client, spreadsheet_id, df_push)
        if ok:
            st.success(f"{result} baris berhasil dikirim ke Google Sheets.")
        else:
            st.error(f"Gagal kirim ke Google Sheets: {result}")

    # ── Results ────────────────────────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    df_final = pd.DataFrame(partial_data).drop(columns=["channel_id"], errors="ignore")
    df_final = df_final.sort_values("Lolos Filter", ascending=False)
    lolos    = df_final[df_final["Lolos Filter"] == True]
    gagal    = df_final[df_final["Lolos Filter"] == False]

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-box">
            <div class="metric-num">{len(df_final)}</div>
            <div class="metric-lbl">Total Channel</div>
        </div>
        <div class="metric-box">
            <div class="metric-num green">{len(lolos)}</div>
            <div class="metric-lbl">Lolos Filter</div>
        </div>
        <div class="metric-box">
            <div class="metric-num red">{len(gagal)}</div>
            <div class="metric-lbl">Tidak Lolos</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs([f"Lolos Filter  ({len(lolos)})", f"Semua Channel  ({len(df_final)})"])
    with tab1:
        if len(lolos) > 0:
            st.dataframe(lolos, use_container_width=True, height=420)
        else:
            st.info("Belum ada yang lolos. Coba kurangi kriteria filter.")
    with tab2:
        st.dataframe(df_final, use_container_width=True, height=420)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            "Download Semua (CSV)",
            df_final.to_csv(index=False).encode("utf-8-sig"),
            f"semua_channel_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv", use_container_width=True
        )
    with col_dl2:
        if len(lolos) > 0:
            st.download_button(
                "Download Lolos Filter (CSV)",
                lolos.to_csv(index=False).encode("utf-8-sig"),
                f"lolos_filter_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv", use_container_width=True
            )
