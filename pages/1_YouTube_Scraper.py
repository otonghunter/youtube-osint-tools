import streamlit as st
import pandas as pd
import time
import re
from datetime import datetime, timezone
from googleapiclient.discovery import build

st.set_page_config(page_title="YouTube Channel Scraper", page_icon="📊", layout="wide")

st.title("📊 YouTube Channel Scraper")
st.caption("Cari dan filter channel YouTube sesuai kriteria buyer")

# ── Sidebar Konfigurasi ───────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Konfigurasi")

    api_key = st.text_input("YouTube API Key", type="password", placeholder="Masukkan API Key lo")

    st.markdown("---")
    st.subheader("🎯 Filter Kriteria")

    min_subs = st.number_input("Min Subscriber", value=100000, step=10000)
    max_subs = st.number_input("Max Subscriber", value=5000000, step=100000)
    min_videos = st.number_input("Min Jumlah Video", value=30, step=5)
    max_year = st.number_input("Channel dibuat sebelum tahun", value=2022, step=1)
    min_inactive = st.number_input("Minimal tidak aktif (bulan)", value=6, step=1)
    max_results = st.slider("Max hasil per keyword", 10, 50, 30)

    st.markdown("---")
    st.subheader("🔑 Keywords")
    keywords_input = st.text_area(
        "Satu keyword per baris",
        value="resep masakan rumahan\nmasak sehari hari\notomotif modifikasi\nmusik original indonesia\ntips otomotif",
        height=150
    )

# ── Helper Functions ──────────────────────────────────────────────

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
            part="snippet",
            q=keyword,
            type="channel",
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
                part="snippet,statistics",
                id=",".join(batch)
            ).execute()
            for item in response.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                published_at = snippet.get("publishedAt", "")
                description = snippet.get("description", "")
                channel_id = item["id"]
                results.append({
                    "channel_id": channel_id,
                    "Nama Channel": snippet.get("title", ""),
                    "Subscriber": int(stats.get("subscriberCount", 0)),
                    "Jumlah Video": int(stats.get("videoCount", 0)),
                    "Total Views": int(stats.get("viewCount", 0)),
                    "Tahun Dibuat": int(published_at[:4]) if published_at else 9999,
                    "Tanggal Dibuat": published_at[:10] if published_at else "",
                    "Negara": snippet.get("country", "-"),
                    "Email": extract_email(description),
                    "URL": f"https://www.youtube.com/channel/{channel_id}",
                    "Upload Terakhir": "",
                    "Tidak Aktif (bulan)": 0,
                    "✅ Lolos Filter": False,
                    "❌ Alasan Gagal": "",
                })
        except Exception as e:
            st.warning(f"Error ambil detail: {e}")
        time.sleep(0.3)
    return results

def get_last_upload(youtube, channel_id):
    try:
        response = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            order="date",
            maxResults=1,
            type="video"
        ).execute()
        items = response.get("items", [])
        if items:
            return items[0]["snippet"]["publishedAt"][:10]
    except:
        pass
    return None

def apply_filter(ch, min_subs, max_subs, min_videos, max_year, min_inactive):
    reasons = []
    if ch["Subscriber"] < min_subs:
        reasons.append(f"subscriber {ch['Subscriber']:,} < {min_subs:,}")
    if ch["Subscriber"] > max_subs:
        reasons.append("subscriber terlalu besar")
    if ch["Jumlah Video"] < min_videos:
        reasons.append(f"video {ch['Jumlah Video']} < {min_videos}")
    if ch["Tahun Dibuat"] >= max_year:
        reasons.append(f"dibuat tahun {ch['Tahun Dibuat']} (terlalu baru)")
    if ch["Tidak Aktif (bulan)"] < min_inactive:
        reasons.append(f"masih aktif ({ch['Tidak Aktif (bulan)']} bulan lalu)")
    if reasons:
        ch["❌ Alasan Gagal"] = " | ".join(reasons)
        ch["✅ Lolos Filter"] = False
    else:
        ch["✅ Lolos Filter"] = True
    return ch

# ── Main UI ───────────────────────────────────────────────────────

st.markdown("---")

if not api_key:
    st.warning("⚠️ Masukkan YouTube API Key di sidebar kiri dulu.")
    st.stop()

keywords = [k.strip() for k in keywords_input.strip().split("\n") if k.strip()]

if st.button("🚀 Mulai Scraping", type="primary", use_container_width=True):

    if not keywords:
        st.error("Tambahkan minimal 1 keyword dulu.")
        st.stop()

    youtube = build("youtube", "v3", developerKey=api_key)

    all_ids = []
    st.markdown("### 🔍 Tahap 1 — Search Channel")
    progress_search = st.progress(0)
    status_search = st.empty()

    for i, kw in enumerate(keywords):
        status_search.text(f"Nyari keyword: '{kw}'...")
        ids = search_channels(youtube, kw, max_results)
        all_ids.extend(ids)
        progress_search.progress((i + 1) / len(keywords))
        time.sleep(0.5)

    all_ids = list(set(all_ids))
    status_search.text(f"✅ Total channel unik ditemukan: {len(all_ids)}")

    st.markdown("### 📋 Tahap 2 — Ambil Detail Channel")
    progress_detail = st.progress(0)
    status_detail = st.empty()
    status_detail.text("Mengambil detail channel...")

    channels = get_channel_details(youtube, all_ids)
    progress_detail.progress(1.0)
    status_detail.text(f"✅ Detail berhasil diambil: {len(channels)} channel")

    st.markdown("### 📅 Tahap 3 — Cek Upload Terakhir")
    progress_upload = st.progress(0)
    status_upload = st.empty()

    # Live table placeholder
    live_table = st.empty()
    partial_data = []

    for i, ch in enumerate(channels):
        last = get_last_upload(youtube, ch["channel_id"])
        ch["Upload Terakhir"] = last or "-"
        ch["Tidak Aktif (bulan)"] = months_since(last)
        ch = apply_filter(ch, min_subs, max_subs, min_videos, max_year, min_inactive)
        partial_data.append(ch)

        progress_upload.progress((i + 1) / len(channels))
        status_upload.text(f"Progress: {i+1}/{len(channels)} — {ch['Nama Channel']}")

        # Update live table setiap 5 channel
        if (i + 1) % 5 == 0 or (i + 1) == len(channels):
            df_partial = pd.DataFrame(partial_data)
            df_partial = df_partial.drop(columns=["channel_id"], errors="ignore")
            df_partial = df_partial.sort_values("✅ Lolos Filter", ascending=False)
            live_table.dataframe(df_partial, use_container_width=True, height=400)

        time.sleep(0.3)

    status_upload.text(f"✅ Selesai!")

    # ── Final Results ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🎯 Hasil Akhir")

    df_final = pd.DataFrame(partial_data).drop(columns=["channel_id"], errors="ignore")
    df_final = df_final.sort_values("✅ Lolos Filter", ascending=False)

    lolos = df_final[df_final["✅ Lolos Filter"] == True]
    gagal = df_final[df_final["✅ Lolos Filter"] == False]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Channel", len(df_final))
    col2.metric("✅ Lolos Filter", len(lolos))
    col3.metric("❌ Tidak Lolos", len(gagal))

    st.markdown("#### ✅ Channel yang Lolos")
    if len(lolos) > 0:
        st.dataframe(lolos, use_container_width=True, height=400)
    else:
        st.info("Belum ada yang lolos filter. Coba kurangi kriteria di sidebar.")

    with st.expander("📋 Lihat semua channel (termasuk yang tidak lolos)"):
        st.dataframe(df_final, use_container_width=True, height=400)

    # ── Download CSV ──────────────────────────────────────────────
    st.markdown("---")
    csv = df_final.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="⬇️ Download Semua Hasil (CSV)",
        data=csv,
        file_name=f"hasil_scraping_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

    csv_lolos = lolos.to_csv(index=False).encode("utf-8-sig") if len(lolos) > 0 else b""
    if csv_lolos:
        st.download_button(
            label="⬇️ Download yang Lolos Filter Saja (CSV)",
            data=csv_lolos,
            file_name=f"hasil_lolos_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
