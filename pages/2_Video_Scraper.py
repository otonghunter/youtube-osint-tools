import streamlit as st
import pandas as pd
import time
import re
from datetime import datetime, timezone
from googleapiclient.discovery import build
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Video Scraper", layout="centered")

CSS = """
<style>
html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
.block-container { max-width: 720px !important; padding: 3rem 2rem 4rem !important; margin: 0 auto; }
#MainMenu, footer, header {visibility: hidden;}
.page-title { font-size: 2rem; font-weight: 800; color: #111; margin: 0 0 0.25rem; letter-spacing: -0.02em; }
.page-sub { font-size: 0.95rem; color: #888; margin: 0 0 2rem; }
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    border: 1.5px solid #ddd !important; border-radius: 10px !important;
    font-size: 0.95rem !important; color: #111 !important; background: #fff !important; box-shadow: none !important;
}
label { font-size: 0.8rem !important; font-weight: 600 !important; color: #555 !important; letter-spacing: 0.02em !important; text-transform: uppercase !important; }
.stButton > button {
    background: #111 !important; color: #fff !important; border: none !important;
    border-radius: 10px !important; font-size: 0.95rem !important; font-weight: 600 !important;
    padding: 0.65rem 1.5rem !important; width: 100% !important; margin-top: 1rem !important;
}
.stButton > button:hover { background: #333 !important; }
.divider { border: none; border-top: 1px solid #ebebeb; margin: 2rem 0; }
.step-row { display: flex; align-items: center; gap: 0.75rem; margin: 1.25rem 0 0.5rem; }
.step-num { width: 26px; height: 26px; border-radius: 50%; background: #111; color: #fff; font-size: 0.75rem; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.step-text { font-size: 0.88rem; font-weight: 600; color: #111; }
.metric-row { display: flex; gap: 1rem; margin: 1.5rem 0; }
.metric-box { flex: 1; background: #f9f9f9; border: 1px solid #ebebeb; border-radius: 12px; padding: 1.1rem; text-align: center; }
.metric-num { font-size: 2rem; font-weight: 800; color: #111; line-height: 1; margin-bottom: 0.35rem; }
.metric-num.green { color: #1a7a4a; }
.metric-lbl { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #aaa; }
.stDownloadButton > button { border: 1.5px solid #ddd !important; border-radius: 10px !important; background: #fff !important; color: #111 !important; font-size: 0.88rem !important; font-weight: 600 !important; width: 100% !important; }
.stDownloadButton > button:hover { border-color: #111 !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

API_KEYS = {
    "API Key 1": "AIzaSyB9nUe2ThxR26Y8_RSA3y5JFaJx2hPSrQ8",
    "API Key 2": "AIzaSyBo6lZZ-CjO3O_Qv57ucqKltP8AOQOSErw",
}

def get_sheets_client():
    try:
        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]),
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        return gspread.authorize(creds)
    except Exception:
        return None

def get_existing_ids_from_sheets(client, spreadsheet_id):
    try:
        records = client.open_by_key(spreadsheet_id).sheet1.get_all_records()
        return set(str(r["channel_id"]) for r in records if r.get("channel_id"))
    except Exception:
        return set()

def push_to_sheets(client, spreadsheet_id, df):
    try:
        ws = client.open_by_key(spreadsheet_id).sheet1
        existing = ws.get_all_values()
        if not existing or existing == [[]]:
            ws.update([df.columns.tolist()] + df.values.tolist())
        else:
            ws.append_rows(df.values.tolist())
        return True, len(df)
    except Exception as e:
        return False, str(e)

st.markdown('<p class="page-title">Video-Based Channel Scraper</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Cari channel lewat keyword video — hasil lebih relevan dan hemat quota API</p>', unsafe_allow_html=True)

with st.expander("Pengaturan dan Filter", expanded=True):
    selected_label = st.selectbox("Pilih API Key", list(API_KEYS.keys()))
    api_key = API_KEYS[selected_label]
    st.caption("Key aktif: " + api_key[:8] + "..." + api_key[-4:])

    st.markdown('<hr style="border:none;border-top:1px solid #ebebeb;margin:1rem 0">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        min_subs = st.number_input("Min Subscriber", value=100000, step=10000)
        max_year = st.number_input("Dibuat sebelum tahun", value=2022, step=1)
    with col2:
        max_subs = st.number_input("Max Subscriber", value=5000000, step=100000)
        max_results = st.slider("Max video per keyword", 10, 50, 30)

    st.markdown('<hr style="border:none;border-top:1px solid #ebebeb;margin:1rem 0">', unsafe_allow_html=True)

    keywords_input = st.text_area(
        "Keywords (satu per baris)",
        value="resep masakan rumahan\nmasak sehari hari\notomotif modifikasi\nmusik original indonesia\ntips otomotif",
        height=140
    )

    st.markdown('<hr style="border:none;border-top:1px solid #ebebeb;margin:1rem 0">', unsafe_allow_html=True)

    use_sheets = st.toggle("Kirim hasil ke Google Sheets", value=False)
    if use_sheets:
        try:
            sheet_id = st.secrets["sheets"]["spreadsheet_id"]
            st.caption("Spreadsheet ID: " + sheet_id[:24] + "...")
        except Exception:
            st.warning("Spreadsheet ID belum diset di Streamlit Secrets.")
            use_sheets = False

    st.markdown('<hr style="border:none;border-top:1px solid #ebebeb;margin:1rem 0">', unsafe_allow_html=True)

    uploaded_csv = st.file_uploader("Upload CSV sebelumnya untuk skip duplikat (opsional)", type=["csv"])
    if uploaded_csv:
        st.caption("Channel yang sudah ada akan otomatis dilewati.")

# ── Helpers ────────────────────────────────────────────────────────
def search_videos(yt, keyword, n):
    """
    Cari video, return dict {channel_id: {title_video, tanggal_upload}}.
    Satu channel hanya diambil sekali — video pertama yang muncul.
    """
    results = {}
    try:
        res = yt.search().list(
            part="snippet", q=keyword, type="video",
            maxResults=min(50, n), order="relevance"
        ).execute()
        for item in res.get("items", []):
            cid   = item["snippet"].get("channelId", "")
            title = item["snippet"].get("title", "")
            pub   = item["snippet"].get("publishedAt", "")[:10]
            if cid and cid not in results:
                results[cid] = {"Judul Video": title, "Tanggal Upload Video": pub}
    except Exception as e:
        st.warning("Error search: " + str(e))
    return results

def get_channel_details(yt, channel_ids):
    results = []
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i+50]
        try:
            res = yt.channels().list(part="snippet,statistics", id=",".join(batch)).execute()
            for item in res.get("items", []):
                s   = item.get("snippet", {})
                st2 = item.get("statistics", {})
                pub = s.get("publishedAt", "")
                results.append({
                    "channel_id":   item["id"],
                    "Nama Channel": s.get("title", ""),
                    "Subscriber":   int(st2.get("subscriberCount", 0)),
                    "Tahun Dibuat": int(pub[:4]) if pub else 9999,
                    "URL Channel":  "https://www.youtube.com/channel/" + item["id"],
                })
        except Exception as e:
            st.warning("Error detail: " + str(e))
        time.sleep(0.3)
    return results

def apply_filter(ch):
    reasons = []
    if ch["Subscriber"] < min_subs:
        reasons.append("subscriber < " + str(min_subs))
    if ch["Subscriber"] > max_subs:
        reasons.append("subscriber terlalu besar")
    if ch["Tahun Dibuat"] >= max_year:
        reasons.append("dibuat tahun " + str(ch["Tahun Dibuat"]))
    return len(reasons) == 0, " | ".join(reasons)

# ── Run ────────────────────────────────────────────────────────────
keywords = [k.strip() for k in keywords_input.strip().split("\n") if k.strip()]

if st.button("Mulai Scraping", use_container_width=True):

    if not api_key.startswith("AIza"):
        st.warning("Masukkan YouTube API Key yang valid.")
        st.stop()
    if not keywords:
        st.error("Tambahkan minimal 1 keyword.")
        st.stop()

    sheets_client = get_sheets_client() if use_sheets else None

    existing_ids = set()
    if use_sheets and sheets_client:
        sheet_id = st.secrets["sheets"]["spreadsheet_id"]
        existing_ids = get_existing_ids_from_sheets(sheets_client, sheet_id)
        if existing_ids:
            st.info(str(len(existing_ids)) + " channel dari Google Sheets akan dilewati.")
    elif uploaded_csv is not None:
        try:
            df_old = pd.read_csv(uploaded_csv)
            if "channel_id" in df_old.columns:
                existing_ids = set(df_old["channel_id"].dropna().tolist())
            st.info(str(len(existing_ids)) + " channel dari CSV akan dilewati.")
        except Exception as e:
            st.warning("Gagal baca CSV: " + str(e))

    yt = build("youtube", "v3", developerKey=api_key)

    # Step 1 — Cari video, deduplikasi channel di sini
    st.markdown('<div class="step-row"><div class="step-num">1</div><div class="step-text">Cari Video dan Deduplikasi Channel</div></div>', unsafe_allow_html=True)
    prog1 = st.progress(0)
    stat1 = st.empty()

    video_map = {}
    for i, kw in enumerate(keywords):
        stat1.caption("Mencari video: " + kw)
        found = search_videos(yt, kw, max_results)
        for cid, meta in found.items():
            if cid not in video_map and cid not in existing_ids:
                video_map[cid] = meta
        prog1.progress((i + 1) / len(keywords))
        time.sleep(0.5)

    stat1.caption(str(len(video_map)) + " channel unik ditemukan (duplikat sudah dibuang)")

    # Step 2 — Ambil detail channel
    st.markdown('<div class="step-row"><div class="step-num">2</div><div class="step-text">Ambil Detail Channel</div></div>', unsafe_allow_html=True)
    prog2 = st.progress(0)
    stat2 = st.empty()
    stat2.caption("Mengambil data...")
    channels = get_channel_details(yt, list(video_map.keys()))
    prog2.progress(1.0)
    stat2.caption(str(len(channels)) + " channel berhasil diambil")

    # Step 3 — Filter dan gabung data video
    st.markdown('<div class="step-row"><div class="step-num">3</div><div class="step-text">Filter dan Susun Hasil</div></div>', unsafe_allow_html=True)
    prog3 = st.progress(0)
    live_table = st.empty()
    partial_data = []

    for i, ch in enumerate(channels):
        lolos, alasan = apply_filter(ch)
        meta = video_map.get(ch["channel_id"], {})
        row = {
            "channel_id":         ch["channel_id"],
            "Nama Channel":       ch["Nama Channel"],
            "Judul Video":        meta.get("Judul Video", ""),
            "Tanggal Upload Video": meta.get("Tanggal Upload Video", ""),
            "Subscriber":         ch["Subscriber"],
            "Tahun Dibuat":       ch["Tahun Dibuat"],
            "URL Channel":        ch["URL Channel"],
            "Lolos Filter":       lolos,
            "Alasan Gagal":       alasan,
        }
        partial_data.append(row)
        prog3.progress((i + 1) / len(channels))

        if (i + 1) % 10 == 0 or (i + 1) == len(channels):
            df_live = pd.DataFrame(partial_data).drop(columns=["channel_id"], errors="ignore")
            live_table.dataframe(df_live.sort_values("Lolos Filter", ascending=False), use_container_width=True, height=280)

    # Push ke Sheets
    if use_sheets and sheets_client and partial_data:
        sheet_id = st.secrets["sheets"]["spreadsheet_id"]
        ok, result = push_to_sheets(sheets_client, sheet_id, pd.DataFrame(partial_data))
        if ok:
            st.success(str(result) + " baris berhasil dikirim ke Google Sheets.")
        else:
            st.error("Gagal kirim ke Google Sheets: " + str(result))

    # Results
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    df_final = pd.DataFrame(partial_data).drop(columns=["channel_id"], errors="ignore")
    df_final = df_final.sort_values("Lolos Filter", ascending=False)
    lolos_df = df_final[df_final["Lolos Filter"] == True]
    gagal_df = df_final[df_final["Lolos Filter"] == False]

    metric_html = (
        '<div class="metric-row">'
        '<div class="metric-box"><div class="metric-num">' + str(len(df_final)) + '</div><div class="metric-lbl">Total Channel</div></div>'
        '<div class="metric-box"><div class="metric-num green">' + str(len(lolos_df)) + '</div><div class="metric-lbl">Lolos Filter</div></div>'
        '</div>'
    )
    st.markdown(metric_html, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Lolos Filter (" + str(len(lolos_df)) + ")", "Semua (" + str(len(df_final)) + ")"])
    with tab1:
        if len(lolos_df) > 0:
            st.dataframe(lolos_df, use_container_width=True, height=420)
        else:
            st.info("Belum ada yang lolos. Coba kurangi kriteria filter.")
    with tab2:
        st.dataframe(df_final, use_container_width=True, height=420)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    with col1:
        st.download_button(
            "Download Semua (CSV)",
            df_final.to_csv(index=False).encode("utf-8-sig"),
            "video_scraper_semua_" + ts + ".csv",
            "text/csv", use_container_width=True
        )
    with col2:
        if len(lolos_df) > 0:
            st.download_button(
                "Download Lolos Filter (CSV)",
                lolos_df.to_csv(index=False).encode("utf-8-sig"),
                "video_scraper_lolos_" + ts + ".csv",
                "text/csv", use_container_width=True
            )
