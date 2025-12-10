import streamlit as st
import google.generativeai as genai
import os

# ================================
# 1. CSS CUSTOM CHAT UI
# ================================
st.markdown("""
<style>

.chat-container {
    max-width: 700px;
    margin: auto;
}

/* USER MESSAGE (KANAN) */
.user-row {
    display: flex;
    justify-content: flex-end;
    align-items: flex-end;
    margin: 12px 0;
}

.user-bubble {
    background-color: #007AFF;
    color: white;
    padding: 10px 15px;
    border-radius: 18px;
    max-width: 70%;
    text-align: right;
    font-size: 16px;
    line-height: 1.4;
    margin-right: 8px;
}

/* BOT MESSAGE (KIRI) */
.bot-row {
    display: flex;
    justify-content: flex-start;
    align-items: flex-end;
    margin: 12px 0;
}

.bot-bubble {
    background-color: #E5E5EA;
    color: black;
    padding: 10px 15px;
    border-radius: 18px;
    max-width: 70%;
    text-align: left;
    font-size: 16px;
    line-height: 1.4;
    margin-left: 8px;
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
def main():

    st.set_page_config(page_title="ELSBOT Chatbot", page_icon="💻")

    st.title("🖥️ ELS Chatbot")
    st.write("Halo! Ada yang bisa saya bantu? 😊")

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
