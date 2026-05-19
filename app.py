import streamlit as st

st.set_page_config(page_title="Creator Finder", page_icon="", layout="centered")

st.markdown("""
<style>
/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.block-container {
    max-width: 680px !important;
    padding: 3rem 2rem 4rem !important;
    margin: 0 auto;
}
/* Hide streamlit branding */
#MainMenu, footer, header {visibility: hidden;}

/* Page title */
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
.divider {
    border: none;
    border-top: 1px solid #ebebeb;
    margin: 2rem 0;
}

/* Input */
.stTextInput > div > div > input {
    border: 1.5px solid #ddd !important;
    border-radius: 10px !important;
    font-size: 1rem !important;
    padding: 0.65rem 1rem !important;
    color: #111 !important;
    background: #fff !important;
    box-shadow: none !important;
    transition: border 0.15s;
}
.stTextInput > div > div > input:focus {
    border-color: #111 !important;
    box-shadow: 0 0 0 3px rgba(0,0,0,0.06) !important;
}

/* Section label */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #bbb;
    margin: 2rem 0 0.75rem;
}

/* Link row */
.link-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.7rem 1rem;
    background: #fff;
    border: 1px solid #ebebeb;
    border-radius: 10px;
    margin-bottom: 0.45rem;
    text-decoration: none !important;
    cursor: pointer;
    transition: border-color 0.15s, background 0.15s;
}
.link-row:hover {
    border-color: #111;
    background: #fafafa;
}
.link-name {
    font-size: 0.9rem;
    font-weight: 600;
    color: #111;
    margin-bottom: 2px;
}
.link-desc {
    font-size: 0.78rem;
    color: #aaa;
}
.link-arrow {
    font-size: 0.85rem;
    color: #ccc;
    flex-shrink: 0;
    margin-left: 1rem;
}

/* Tip */
.tip-box {
    background: #f7f7f7;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-top: 2rem;
    font-size: 0.85rem;
    color: #555;
    line-height: 1.6;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 5rem 0 3rem;
    color: #ccc;
}
.empty-state p {
    font-size: 0.95rem;
    color: #bbb;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="page-title">Creator Finder</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Cari kontak publik kreator YouTube berdasarkan nama channel</p>', unsafe_allow_html=True)

channel_name = st.text_input("", placeholder="Ketik nama channel YouTube...", label_visibility="collapsed")

if channel_name:
    q = channel_name.strip()
    q_encoded = q.replace(" ", "+")
    q_nospace = q.replace(" ", "").lower()
    q_quoted = f'"{q}"'

    def section(title):
        st.markdown(f'<p class="section-label">{title}</p>', unsafe_allow_html=True)

    def link_row(name, desc, url):
        st.markdown(f"""
        <a class="link-row" href="{url}" target="_blank">
            <div>
                <div class="link-name">{name}</div>
                <div class="link-desc">{desc}</div>
            </div>
            <span class="link-arrow">&#8599;</span>
        </a>""", unsafe_allow_html=True)

    section("YouTube & Google")
    link_row("YouTube Search", "Cari channel langsung di YouTube", f"https://www.youtube.com/results?search_query={q_encoded}&sp=EgIQAg%3D%3D")
    link_row("Google — Nama Channel", "Referensi umum nama channel", f"https://www.google.com/search?q={q_quoted}")
    link_row("Google — Email & Kontak", "Dorking kontak yang dipublish secara publik", f"https://www.google.com/search?q={q_quoted}+(email+OR+contact+OR+kontak)")
    link_row("Google — Media Sosial", "Dorking akun media sosial terkait", f"https://www.google.com/search?q={q_quoted}+(instagram+OR+tiktok+OR+twitter+OR+facebook)")
    link_row("Google — Website & Blog", "Cari website atau blog pribadi kreator", f"https://www.google.com/search?q={q_quoted}+(site:wordpress.com+OR+site:blogspot.com+OR+website)")

    section("Media Sosial")
    link_row("Instagram", "Coba username tanpa spasi", f"https://www.instagram.com/{q_nospace}")
    link_row("Instagram Search via Google", "Dorking nama di Instagram", f"https://www.google.com/search?q=site:instagram.com+{q_quoted}")
    link_row("TikTok", "Coba username tanpa spasi", f"https://www.tiktok.com/@{q_nospace}")
    link_row("TikTok Search via Google", "Dorking nama di TikTok", f"https://www.google.com/search?q=site:tiktok.com+{q_quoted}")
    link_row("Facebook", "Cari halaman atau profil di Facebook", f"https://www.facebook.com/search/top?q={q_encoded}")
    link_row("Twitter / X", "Cari akun Twitter atau X", f"https://x.com/search?q={q_encoded}&f=user")

    section("Platform Kreator Indonesia")
    link_row("Linktree", "Banyak kreator cantumkan semua kontak di sini", f"https://linktr.ee/{q_nospace}")
    link_row("Linktree Search via Google", "Dorking profil Linktree kreator", f"https://www.google.com/search?q=site:linktr.ee+{q_quoted}")
    link_row("Karyakarsa", "Platform monetisasi kreator Indonesia", f"https://karyakarsa.com/{q_nospace}")
    link_row("Saweria", "Platform donasi kreator Indonesia", f"https://saweria.co/{q_nospace}")

    section("Statistik Channel")
    link_row("Social Blade", "Data statistik dan histori pertumbuhan channel", f"https://socialblade.com/search/search?query={q_encoded}")
    link_row("Noxinfluencer", "Estimasi earning dan analitik channel", f"https://www.noxinfluencer.com/youtube/search?keyword={q_encoded}")

    st.markdown("""
    <div class="tip-box">
        <strong>Tips:</strong> Mulai dari Google dorking email/kontak dan Linktree Search.
        Banyak kreator tidak mencantumkan kontak di YouTube tapi punya Linktree yang lengkap.
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty-state">
        <p>Ketik nama channel YouTube di atas untuk mulai mencari kontak kreator.</p>
    </div>
    """, unsafe_allow_html=True)
