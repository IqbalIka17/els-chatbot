import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="ELSBOT Chatbot", page_icon="💻")

# ================================
# 1. CSS CUSTOM CHAT UI
# ================================
st.markdown("""
<style>

/* ===== BACKGROUND ===== */
body {
    background: radial-gradient(circle at top, #0f172a 0%, #020617 40%, #000000 100%);
    color: white;
}

/* ===== CHAT CONTAINER ===== */
.chat-container {
    max-width: 760px;
    margin: auto;
    padding-bottom: 80px;
}

/* ===== QUICK BUTTON STYLE ===== */
div[data-testid="column"] > div > button {
    width: 100%;
    padding: 14px 0;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.1);
    background: linear-gradient(145deg, #0f172a, #020617);
    color: white;
    font-size: 15px;
    font-weight: 500;
    transition: all 0.25s ease;
    box-shadow: 0 4px 18px rgba(0,0,0,0.4);
}

div[data-testid="column"] > div > button:hover {
    transform: translateY(-2px) scale(1.02);
    background: linear-gradient(145deg, #1e293b, #020617);
    box-shadow: 0 8px 25px rgba(0,0,0,0.6);
}

/* ===== USER MESSAGE ===== */
.user-row {
    display: flex;
    justify-content: flex-end;
    margin: 14px 0;
}

.user-bubble {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    padding: 12px 18px;
    border-radius: 20px 20px 4px 20px;
    max-width: 72%;
    font-size: 15px;
    line-height: 1.5;
    box-shadow: 0 4px 15px rgba(37,99,235,0.35);
    animation: fadeInUp 0.25s ease;
}

/* ===== BOT MESSAGE ===== */
.bot-row {
    display: flex;
    justify-content: flex-start;
    margin: 14px 0;
}

.bot-bubble {
    background: linear-gradient(135deg, #f1f5f9, #e5e7eb);
    color: #020617;
    padding: 12px 18px;
    border-radius: 20px 20px 20px 4px;
    max-width: 72%;
    font-size: 15px;
    line-height: 1.5;
    box-shadow: 0 4px 15px rgba(0,0,0,0.25);
    animation: fadeInUp 0.25s ease;
}

/* ===== INPUT BOX ===== */
textarea, input {
    border-radius: 14px !important;
    background: #020617 !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}

/* ===== ANIMATION ===== */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(8px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

</style>
""", unsafe_allow_html=True)



# ================================
# 2. LOAD STORE DATA
# ================================
def load_store_data_txt(file_path="store_data.txt"):
    if not os.path.exists(file_path):
        st.error(f"File {file_path} tidak ditemukan.")
        st.stop()
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# ================================
# 3. INIT GEMINI MODEL
# ================================
def initialize_gemini():
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)

    store_info = load_store_data_txt("store_data.txt")

    system_prompt = f"""
    Kamu adalah chatbot Customer Service untuk toko laptop.

    Gunakan informasi berikut untuk menjawab:

    {store_info}

    Aturan Respon:
    - Jawab dengan ramah dan profesional.
    - Berikan produk yang ada di daftar katalog saja.
    - Jika ditanya harga: berikan harga tertera.
    - Jika ditanya stok: jawab bahwa stok biasanya tersedia, tapi harus dicek.
    - Jangan gunakan tanda bintang (*), bold (** **).
    - Selalu tawarkan bantuan di akhir chat.
    """

    return genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction=system_prompt
    )


# ================================
# 4. CHAT FUNGSI
# ================================
def ask_gemini(prompt):
    response = st.session_state.model.generate_content(prompt)
    return response.text.strip()


# ================================
# 5. MAIN UI
# ================================
def handle_quick_reply(text):
    st.session_state.history.append({"role": "user", "msg": text})
    reply = ask_gemini(text)
    st.session_state.history.append({"role": "bot", "msg": reply})
    st.rerun()

def main():

    st.title("🖥️ ELS Chatbot")
    st.write("Halo! Saya siap membantu mencari laptop sesuai kebutuhan Anda 😊")

    # =======================
    # QUICK REPLY BUTTONS
    # =======================
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📍 Alamat Toko"):
            handle_quick_reply("Di mana alamat toko?")

    with col2:
        if st.button("📞 Nomor Telepon"):
            handle_quick_reply("Berapa nomor telepon toko?")

    with col3:
        if st.button("🕒 Jam Buka"):
            handle_quick_reply("Jam operasional toko?")


    # Load model sekali
    if "model" not in st.session_state:
        st.session_state.model = initialize_gemini()

    # Chat history
    if "history" not in st.session_state:
        st.session_state.history = [
            {"role": "bot", "msg": "Halo! Saya ELSBOT. Ada yang bisa saya bantu hari ini? 😊"}
        ]

    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    # =======================
    # 6. RENDER CHAT
    # =======================
    for chat in st.session_state.history:
        if chat["role"] == "user":
            st.markdown(
                f"""
                <div class="user-row">
                    <div class="user-bubble">{chat['msg']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="bot-row">
                    <div class="bot-bubble">{chat['msg']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # =======================
    # 7. INPUT CHAT
    # =======================
    user_input = st.chat_input("Ketik pesan Anda...")

    if user_input:
        st.session_state.history.append({"role": "user", "msg": user_input})

        reply = ask_gemini(user_input)
        st.session_state.history.append({"role": "bot", "msg": reply})

        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ================================
# 8. RUN
# ================================
if __name__ == "__main__":
    main()
