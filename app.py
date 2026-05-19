import streamlit as st

st.set_page_config(page_title="YouTube Creator Finder", page_icon="🔍", layout="centered")

st.title("🔍 YouTube Creator Finder")
st.caption("Cari kontak publik kreator YouTube berdasarkan nama channel")

channel_name = st.text_input("Nama Channel YouTube", placeholder="contoh: Masak Enak Indonesia")

if channel_name:
    q = channel_name.strip()
    q_encoded = q.replace(" ", "+")
    q_nospace = q.replace(" ", "").lower()
    q_quoted = f'"{q}"'

    st.markdown("---")

    # ── YouTube & Google ──────────────────────────────────────────
    st.subheader("📺 YouTube & Google")

    col1, col2 = st.columns(2)
    with col1:
        st.link_button(
            "🔎 YouTube Search",
            f"https://www.youtube.com/results?search_query={q_encoded}&sp=EgIQAg%3D%3D",
            use_container_width=True
        )
        st.link_button(
            "📧 Google — Email/Kontak",
            f"https://www.google.com/search?q={q_quoted}+(email+OR+contact+OR+kontak)",
            use_container_width=True
        )
        st.link_button(
            "🌐 Google — Website/Blog",
            f"https://www.google.com/search?q={q_quoted}+(site:wordpress.com+OR+site:blogspot.com+OR+website)",
            use_container_width=True
        )
    with col2:
        st.link_button(
            "🔍 Google — Nama Channel",
            f"https://www.google.com/search?q={q_quoted}",
            use_container_width=True
        )
        st.link_button(
            "📱 Google — Medsos",
            f"https://www.google.com/search?q={q_quoted}+(instagram+OR+tiktok+OR+twitter+OR+facebook)",
            use_container_width=True
        )

    st.markdown("---")

    # ── Media Sosial ──────────────────────────────────────────────
    st.subheader("📱 Media Sosial")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.link_button(
            "📸 Instagram",
            f"https://www.instagram.com/{q_nospace}",
            use_container_width=True
        )
        st.link_button(
            "📸 Instagram Search",
            f"https://www.google.com/search?q=site:instagram.com+{q_quoted}",
            use_container_width=True
        )
    with col2:
        st.link_button(
            "🎵 TikTok",
            f"https://www.tiktok.com/@{q_nospace}",
            use_container_width=True
        )
        st.link_button(
            "🎵 TikTok Search",
            f"https://www.google.com/search?q=site:tiktok.com+{q_quoted}",
            use_container_width=True
        )
    with col3:
        st.link_button(
            "👤 Facebook",
            f"https://www.facebook.com/search/top?q={q_encoded}",
            use_container_width=True
        )
        st.link_button(
            "🐦 Twitter / X",
            f"https://x.com/search?q={q_encoded}&f=user",
            use_container_width=True
        )

    st.markdown("---")

    # ── Platform Kreator ──────────────────────────────────────────
    st.subheader("🎨 Platform Kreator Indonesia")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.link_button(
            "🔗 Linktree",
            f"https://linktr.ee/{q_nospace}",
            use_container_width=True
        )
        st.link_button(
            "🔗 Linktree Search",
            f"https://www.google.com/search?q=site:linktr.ee+{q_quoted}",
            use_container_width=True
        )
    with col2:
        st.link_button(
            "❤️ Karyakarsa",
            f"https://karyakarsa.com/{q_nospace}",
            use_container_width=True
        )
    with col3:
        st.link_button(
            "☕ Saweria",
            f"https://saweria.co/{q_nospace}",
            use_container_width=True
        )

    st.markdown("---")

    # ── Referensi Channel ─────────────────────────────────────────
    st.subheader("📊 Referensi & Statistik Channel")

    col1, col2 = st.columns(2)
    with col1:
        st.link_button(
            "📈 Social Blade",
            f"https://socialblade.com/search/search?query={q_encoded}",
            use_container_width=True
        )
    with col2:
        st.link_button(
            "📉 Noxinfluencer",
            f"https://www.noxinfluencer.com/youtube/search?keyword={q_encoded}",
            use_container_width=True
        )

    st.markdown("---")
    st.caption("💡 Tips: Coba Google dorking email/kontak dan Linktree Search — sering nemu kontak yang ga dicantumkan di YouTube.")

else:
    st.info("👆 Masukkan nama channel YouTube di atas untuk mulai mencari.")
