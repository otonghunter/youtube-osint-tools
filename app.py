import streamlit as st

st.set_page_config(page_title="Creator Finder", page_icon="🔍", layout="wide")

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
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 900px;
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
.section-label {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #aaa;
    margin: 1.8rem 0 0.8rem;
}
.link-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    text-decoration: none;
    color: #0f1117;
}
.link-card:hover {
    border-color: #0f1117;
    background: #fafafa;
}
.link-card-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.link-icon {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    background: #f5f5f5;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
}
.link-name {
    font-size: 0.9rem;
    font-weight: 500;
    color: #0f1117;
}
.link-desc {
    font-size: 0.78rem;
    color: #999;
}
.tip-box {
    background: #f8f9fa;
    border-left: 3px solid #0f1117;
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    margin-top: 2rem;
    font-size: 0.85rem;
    color: #555;
}
.stTextInput > div > div > input {
    border-radius: 8px !important;
    border: 1.5px solid #e0e0e0 !important;
    font-size: 1rem !important;
    padding: 0.6rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #0f1117 !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <p class="page-title">🔍 Creator Finder</p>
    <p class="page-sub">Cari kontak publik kreator YouTube berdasarkan nama channel</p>
</div>
""", unsafe_allow_html=True)

channel_name = st.text_input("", placeholder="Ketik nama channel YouTube...", label_visibility="collapsed")

if channel_name:
    q = channel_name.strip()
    q_encoded = q.replace(" ", "+")
    q_nospace = q.replace(" ", "").lower()
    q_quoted = f'"{q}"'

    def render_section(title, items):
        st.markdown(f'<p class="section-label">{title}</p>', unsafe_allow_html=True)
        for item in items:
            st.markdown(f"""
            <a class="link-card" href="{item['url']}" target="_blank">
                <div class="link-card-left">
                    <div class="link-icon">{item['icon']}</div>
                    <div>
                        <div class="link-name">{item['name']}</div>
                        <div class="link-desc">{item['desc']}</div>
                    </div>
                </div>
                <span style="color:#ccc;">↗</span>
            </a>
            """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        render_section("YouTube & Google", [
            {"icon": "▶️", "name": "YouTube Search", "desc": "Cari channel langsung", "url": f"https://www.youtube.com/results?search_query={q_encoded}&sp=EgIQAg%3D%3D"},
            {"icon": "🔍", "name": "Google — Nama Channel", "desc": "Referensi nama di Google", "url": f"https://www.google.com/search?q={q_quoted}"},
            {"icon": "📧", "name": "Google — Email/Kontak", "desc": "Dorking kontak publik", "url": f"https://www.google.com/search?q={q_quoted}+(email+OR+contact+OR+kontak)"},
            {"icon": "📱", "name": "Google — Medsos", "desc": "Dorking akun media sosial", "url": f"https://www.google.com/search?q={q_quoted}+(instagram+OR+tiktok+OR+twitter+OR+facebook)"},
            {"icon": "🌐", "name": "Google — Website/Blog", "desc": "Cari blog atau website pribadi", "url": f"https://www.google.com/search?q={q_quoted}+(site:wordpress.com+OR+site:blogspot.com+OR+website)"},
        ])

        render_section("Statistik Channel", [
            {"icon": "📈", "name": "Social Blade", "desc": "Statistik & histori channel", "url": f"https://socialblade.com/search/search?query={q_encoded}"},
            {"icon": "📉", "name": "Noxinfluencer", "desc": "Data & estimasi earning", "url": f"https://www.noxinfluencer.com/youtube/search?keyword={q_encoded}"},
        ])

    with col2:
        render_section("Media Sosial", [
            {"icon": "📸", "name": "Instagram", "desc": "Coba username tanpa spasi", "url": f"https://www.instagram.com/{q_nospace}"},
            {"icon": "📸", "name": "Instagram Search", "desc": "Dorking via Google", "url": f"https://www.google.com/search?q=site:instagram.com+{q_quoted}"},
            {"icon": "🎵", "name": "TikTok", "desc": "Coba username tanpa spasi", "url": f"https://www.tiktok.com/@{q_nospace}"},
            {"icon": "🎵", "name": "TikTok Search", "desc": "Dorking via Google", "url": f"https://www.google.com/search?q=site:tiktok.com+{q_quoted}"},
            {"icon": "👤", "name": "Facebook", "desc": "Cari nama di Facebook", "url": f"https://www.facebook.com/search/top?q={q_encoded}"},
            {"icon": "🐦", "name": "Twitter / X", "desc": "Cari akun Twitter/X", "url": f"https://x.com/search?q={q_encoded}&f=user"},
        ])

        render_section("Platform Kreator Indonesia", [
            {"icon": "🔗", "name": "Linktree", "desc": "Banyak kreator punya Linktree", "url": f"https://linktr.ee/{q_nospace}"},
            {"icon": "🔗", "name": "Linktree Search", "desc": "Dorking Linktree via Google", "url": f"https://www.google.com/search?q=site:linktr.ee+{q_quoted}"},
            {"icon": "❤️", "name": "Karyakarsa", "desc": "Platform kreator Indonesia", "url": f"https://karyakarsa.com/{q_nospace}"},
            {"icon": "☕", "name": "Saweria", "desc": "Platform donasi kreator", "url": f"https://saweria.co/{q_nospace}"},
        ])

    st.markdown("""
    <div class="tip-box">
        💡 <strong>Tips:</strong> Mulai dari <strong>Google dorking email/kontak</strong> dan <strong>Linktree Search</strong> — sering nemu kontak yang tidak dicantumkan langsung di YouTube.
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center; padding: 4rem 0;">
        <div style="font-size: 2.5rem; margin-bottom: 1rem;">🔍</div>
        <p style="font-size: 1rem; color: #aaa;">Ketik nama channel YouTube di atas untuk mulai mencari</p>
    </div>
    """, unsafe_allow_html=True)
