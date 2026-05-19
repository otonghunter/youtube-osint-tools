import streamlit as st
import pandas as pd
import time
import re
from datetime import datetime, timezone
from googleapiclient.discovery import build

st.set_page_config(page_title="YouTube Scraper", page_icon="📊", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #0f1117;
}
[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}
[data-testid="stSidebarNav"] a {
    color: #e0e0e0 !important;
}
[data-testid="stSidebar"] .stTextInput input {
    background: #1e2130 !important;
    border-color: #333 !important;
    color: #fff !important;
}
[data-testid="stSidebar"] .stNumberInput input {
    background: #1e2130 !important;
    border-color: #333 !important;
    color: #fff !important;
}
[data-testid="stSidebar"] .stTextArea textarea {
    background: #1e2130 !important;
    border-color: #333 !important;
    color: #fff !important;
}
[data-testid="stSidebar"] .stSlider {
    color: #e0e0e0 !important;
}
[data-testid="stSidebar"] label {
    color: #aaa !important;
    font-size: 0.8rem !important;
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #fff !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.page-header {
    border-bottom: 2px solid #f0f0f0;
    padding-bottom: 1rem;
    margin-bottom: 2rem;
}
.page-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #0f1117;
    margin: 0;
}
.page-sub {
    font-size: 0.9rem;
    color: #888;
    margin-top: 0.3rem;
}
.metric-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    text-align: center;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #0f1117;
}
.metric-label {
    font-size: 0.78rem;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.step-badge {
    display: inline-block;
    background: #0f1117;
    color: #fff;
    border-radius: 50%;
    width: 22px;
    height: 22px;
    text-align: center;
    line-height: 22px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.5rem;
}
.step-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #0f1117;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔑 API")
    api_key = st.text_input("YouTube API Key", type="password", placeholder="Paste API key lo")

    st.markdown("---")
    st.markdown("## 🎯 Filter")
    min_subs = st.number_input("Min Subscriber", value=100000, step=10000)
    max_subs = st.number_input("Max Subscriber", value=5000000, step=100000)
    min_videos = st.number_input("Min Jumlah Video", value=30, step=5)
    max_year = st.number_input("Dibuat sebelum tahun", value=2022, step=1)
    min_inactive = st.number_input("Tidak aktif minimal (bulan)", value=6, step=1)
    max_results = st.slider("Max hasil per keyword", 10, 50, 30)

    st.markdown("---")
    st.markdown("## 🔑 Keywords")
    keywords_input = st.text_area(
        "Satu keyword per baris",
        value="resep masakan rumahan\nmasak sehari hari\notomotif modifikasi\nmusik original indonesia\ntips otomotif",
        height=160,
        label_visibility="collapsed"
    )

# ── Header ─────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <p class="page-title">📊 YouTube Channel Scraper</p>
    <p class="page-sub">Temukan channel YouTube yang sesuai kriteria buyer secara otomatis</p>
</div>
""", unsafe_allow_html=True)

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
        now = datetime.now(timezone.utc)
        return round((now - last).days / 30, 1)
    except:
        return 0

def search_channels(youtube, keyword, max_results):
    channel_ids = []
    try:
        response = youtube.search().list(
            part="snippet", q=keyword, type="channel",
            maxResults=min(50, max_results)
        ).execute()
        for item in response.get("items", []):
            channel_ids.append(item["snippet"]["channelId"])
    except Exception as e:
        st.warning(f"Error search '{keyword}': {e}")
    return channel_ids

def get_channel_details(youtube, channel_ids):
    results = []
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i+50]
        try:
            response = youtube.channels().list(
                part="snippet,statistics", id=",".join(batch)
            ).execute()
            for item in response.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                published_at = snippet.get("publishedAt", "")
                description = snippet.get("description", "")
                results.append({
                    "channel_id": item["id"],
                    "Nama Channel": snippet.get("title", ""),
                    "Subscriber": int(stats.get("subscriberCount", 0)),
                    "Jumlah Video": int(stats.get("videoCount", 0)),
                    "Total Views": int(stats.get("viewCount", 0)),
                    "Tahun Dibuat": int(published_at[:4]) if published_at else 9999,
                    "Tanggal Dibuat": published_at[:10] if published_at else "",
                    "Negara": snippet.get("country", "-"),
                    "Email": extract_email(description),
                    "URL": f"https://www.youtube.com/channel/{item['id']}",
                    "Upload Terakhir": "",
                    "Tidak Aktif (bulan)": 0,
                    "Lolos Filter": False,
                    "Alasan Gagal": "",
                })
        except Exception as e:
            st.warning(f"Error detail: {e}")
        time.sleep(0.3)
    return results

def get_last_upload(youtube, channel_id):
    try:
        response = youtube.search().list(
            part="snippet", channelId=channel_id,
            order="date", maxResults=1, type="video"
        ).execute()
        items = response.get("items", [])
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

# ── Main ───────────────────────────────────────────────────────────
if not api_key:
    st.info("👈 Masukkan YouTube API Key di sidebar kiri untuk mulai.")
    st.stop()

keywords = [k.strip() for k in keywords_input.strip().split("\n") if k.strip()]

if st.button("🚀 Mulai Scraping", type="primary", use_container_width=True):
    if not keywords:
        st.error("Tambahkan minimal 1 keyword dulu.")
        st.stop()

    youtube = build("youtube", "v3", developerKey=api_key)
    all_ids = []

    # Step 1
    st.markdown('<p><span class="step-badge">1</span><span class="step-label">Search Channel</span></p>', unsafe_allow_html=True)
    prog1 = st.progress(0)
    stat1 = st.empty()
    for i, kw in enumerate(keywords):
        stat1.caption(f"Mencari: *{kw}*")
        ids = search_channels(youtube, kw, max_results)
        all_ids.extend(ids)
        prog1.progress((i + 1) / len(keywords))
        time.sleep(0.5)
    all_ids = list(set(all_ids))
    stat1.caption(f"✅ {len(all_ids)} channel unik ditemukan")

    # Step 2
    st.markdown('<p><span class="step-badge">2</span><span class="step-label">Ambil Detail Channel</span></p>', unsafe_allow_html=True)
    prog2 = st.progress(0)
    stat2 = st.empty()
    stat2.caption("Mengambil data detail...")
    channels = get_channel_details(youtube, all_ids)
    prog2.progress(1.0)
    stat2.caption(f"✅ {len(channels)} channel berhasil diambil")

    # Step 3
    st.markdown('<p><span class="step-badge">3</span><span class="step-label">Cek Upload Terakhir & Filter</span></p>', unsafe_allow_html=True)
    prog3 = st.progress(0)
    stat3 = st.empty()
    live_table = st.empty()
    partial_data = []

    for i, ch in enumerate(channels):
        last = get_last_upload(youtube, ch["channel_id"])
        ch["Upload Terakhir"] = last or "-"
        ch["Tidak Aktif (bulan)"] = months_since(last)
        ch = apply_filter(ch)
        partial_data.append(ch)
        prog3.progress((i + 1) / len(channels))
        stat3.caption(f"Memproses {i+1}/{len(channels)}: *{ch['Nama Channel']}*")

        if (i + 1) % 5 == 0 or (i + 1) == len(channels):
            df_live = pd.DataFrame(partial_data).drop(columns=["channel_id"], errors="ignore")
            df_live = df_live.sort_values("Lolos Filter", ascending=False)
            live_table.dataframe(df_live, use_container_width=True, height=300)

        time.sleep(0.3)

    stat3.caption("✅ Selesai!")

    # Results
    st.markdown("---")
    df_final = pd.DataFrame(partial_data).drop(columns=["channel_id"], errors="ignore")
    df_final = df_final.sort_values("Lolos Filter", ascending=False)
    lolos = df_final[df_final["Lolos Filter"] == True]
    gagal = df_final[df_final["Lolos Filter"] == False]

    # Metric cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df_final)}</div><div class="metric-label">Total Channel</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#1a7a4a;">{len(lolos)}</div><div class="metric-label">✅ Lolos Filter</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#c0392b;">{len(gagal)}</div><div class="metric-label">❌ Tidak Lolos</div></div>', unsafe_allow_html=True)

    st.markdown("&nbsp;", unsafe_allow_html=True)

    tab1, tab2 = st.tabs([f"✅ Lolos Filter ({len(lolos)})", f"📋 Semua Channel ({len(df_final)})"])

    with tab1:
        if len(lolos) > 0:
            st.dataframe(lolos, use_container_width=True, height=450)
        else:
            st.info("Belum ada yang lolos. Coba kurangi kriteria filter di sidebar.")

    with tab2:
        st.dataframe(df_final, use_container_width=True, height=450)

    # Download
    st.markdown("---")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            "⬇️ Download Semua (CSV)",
            df_final.to_csv(index=False).encode("utf-8-sig"),
            f"semua_channel_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv", use_container_width=True
        )
    with col_dl2:
        if len(lolos) > 0:
            st.download_button(
                "⬇️ Download Lolos Filter (CSV)",
                lolos.to_csv(index=False).encode("utf-8-sig"),
                f"lolos_filter_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv", use_container_width=True
            )
