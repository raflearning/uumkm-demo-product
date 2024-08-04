import streamlit as st
import pandas as pd
import time
import plotly.express as px
import google.generativeai as genai
from google.api_core.exceptions import InternalServerError
from dotenv import load_dotenv
from vis_interpret import (
    visualize_pelanggan, visualize_produk, visualize_transaksi_penjualan, 
    visualize_lokasi_penjualan, visualize_staf_penjualan, visualize_inventaris, 
    visualize_promosi_pemasaran, visualize_feedback_pengembalian, 
    visualize_analisis_penjualan, visualize_lainnya
)
from state_management import StateManager

state_manager = StateManager()

st.title("🚀 Pantau Kinerja Bisnis Kamu!")
st.write(
    "Memudahkan kamu untuk mengambil informasi bisnis dan rekomendasi pengambilan keputusan dengan Artificial Intelligence!"
)

# Section divider
st.markdown("---")

# Ambil API key dari variabel lingkungan
API_KEY = st.secrets["general"]["API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

# Function to load data from all sheets
def load_data(uploaded_file):
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file, sheet_name=None)
        return data
    else:
        return None

# Function to get business info options based on selected sheet
def get_business_options(sheet_name):
    options = {
        'Pelanggan': [
            'Analisis demografi pelanggan',
            'Distribusi usia dan jenis kelamin pelanggan',
            'Segmentasi pelanggan berdasarkan preferensi'
        ],
        'Produk': [
            'Kinerja penjualan produk dan stok',
            'Distribusi penjualan berdasarkan kategori produk',
            'Analisis harga produk dan trend penjualan'
        ],
        'Transaksi Penjualan': [
            'Jumlah penjualan, pendapatan, dan metode pembayaran',
            'Tren penjualan',
            'Analisis status penjualan dan metode pembayaran'
        ],
        'Lokasi Penjualan': [
            'Kinerja penjualan di berbagai lokasi',
            'Distribusi penjualan berdasarkan kota/provinsi',
            'Analisis lokasi dengan penjualan tertinggi/rendah'
        ],
        'Staf Penjualan': [
            'Kinerja dan komisi staf penjualan',
            'Analisis penilaian kinerja staf',
            'Distribusi staf berdasarkan posisi/jabatan'
        ],
        'Inventaris': [
            'Manajemen stok produk',
            'Tren stok masuk dan keluar',
            'Analisis produk dengan stok terbanyak/terkecil'
        ],
        'Promosi dan Pemasaran': [
            'Efektivitas kampanye promosi',
            'Distribusi penjualan berdasarkan media promosi',
            'Analisis kode diskon promosi'
        ],
        'Feedback dan Pengembalian': [
            'Masalah dan kepuasan pelanggan',
            'Distribusi alasan pengembalian produk',
            'Status pengembalian produk'
        ],
        'Analisis Penjualan': [
            'Penjualan agregat dan tren',
            'Analisis penjualan berdasarkan produk/kategori',
            'Tren penjualan/tahunan'
        ],
        'Lainnya': [
            'Analisis tambahan dan faktor eksternal',
            'Tren penjualan berdasarkan faktor ekonomi',
            'Distribusi biaya operasional terkait penjualan'
        ]
    }
    return options.get(sheet_name, [])

if 'charts' not in st.session_state:
    st.session_state.charts = []
if 'interpretation' not in st.session_state:
    st.session_state.interpretation = ""
if 'selected_sheet' not in st.session_state:
    st.session_state.selected_sheet = ""
if 'selected_business_info' not in st.session_state:
    st.session_state.selected_business_info = ""
if 'keep_interpretation' not in st.session_state:
    st.session_state.keep_interpretation = False
if 'chatbot_response' not in st.session_state:
    st.session_state.chatbot_response = ""
if 'interpretation_done' not in st.session_state:
    st.session_state.interpretation_done = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []    

# Sidebar for file upload
st.sidebar.header("Unggah Data Penjualan Bisnis Kamu")
uploaded_file = st.sidebar.file_uploader("Unggah file Excel", type=["xlsx"])
data = load_data(uploaded_file)

if data is not None:
    st.sidebar.success("Data berhasil diunggah!")
    sheet_names = list(data.keys())
else:
    st.sidebar.warning("Silakan unggah file Excel untuk melanjutkan.")
    sheet_names = []

# Main content area
tab_selection = st.sidebar.radio("Pilih Halaman", ["Dashboard", "Chatbot"])

# Hint notification
st.sidebar.write("🔍 **Butuh bantuan?**")
with st.sidebar.expander("Bantuan", expanded=False):
    st.write("**Dashboard**: Unggah data, pilih kategori, dan lihat analitik serta interpretasi.")
    st.write("**Chatbot**: Tanyakan sesuatu tentang hasil visualisasi dan interpretasi di sini.")
    st.write("Untuk bantuan lebih lanjut, kunjungi [dokumentasi kami](#).")

# Floating notification for hints
if not st.session_state.get('hint_shown', False):
    st.info("🔔 **Hint:** Untuk bantuan menggunakan aplikasi ini, lihat panel Bantuan di sidebar.")
    st.session_state['hint_shown'] = True

def add_date_picker(df):
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", min_value=df.index.min(), max_value=df.index.max(), value=df.index.min())
    with col2:
        end_date = st.date_input("End Date", min_value=df.index.min(), max_value=df.index.max(), value=df.index.max())
    return start_date, end_date

def add_sort_buttons():
    col1, col2 = st.columns(2)
    with col1:
        sort_order = st.radio("Sort Order", ("Ascending", "Descending"))
    with col2:
        sort_by = st.radio("Sort By", ("Value", "Category"))
    return sort_order, sort_by

if tab_selection == "Dashboard":
    if data is not None:
        selected_sheet = st.selectbox("Pilih Kategori Data", [""] + sheet_names)

        if selected_sheet:
            sheet_data = data[selected_sheet]
            st.write("#### Data yang Diunggah")
            st.dataframe(sheet_data)

            st.write("#### 👇 Pilih Informasi Bisnis yang Kamu Inginkan")
            business_options = get_business_options(selected_sheet)
            selected_business_info = st.selectbox("", [""] + business_options)

            if selected_business_info:
                def get_visualization_and_interpretation(sheet_data, selected_business_info, selected_sheet):
                    if selected_sheet == 'Pelanggan':
                        return visualize_pelanggan(sheet_data, selected_business_info, model)
                    elif selected_sheet == 'Produk':
                        return visualize_produk(sheet_data, selected_business_info, model)
                    elif selected_sheet == 'Transaksi Penjualan':
                        return visualize_transaksi_penjualan(sheet_data, selected_business_info, model)
                    elif selected_sheet == 'Lokasi Penjualan':
                        return visualize_lokasi_penjualan(sheet_data, selected_business_info, model)
                    elif selected_sheet == 'Staf Penjualan':
                        return visualize_staf_penjualan(sheet_data, selected_business_info, model)
                    elif selected_sheet == 'Inventaris':
                        return visualize_inventaris(sheet_data, selected_business_info, model)
                    elif selected_sheet == 'Promosi dan Pemasaran':
                        return visualize_promosi_pemasaran(sheet_data, selected_business_info, model)
                    elif selected_sheet == 'Feedback dan Pengembalian':
                        return visualize_feedback_pengembalian(sheet_data, selected_business_info, model)
                    elif selected_sheet == 'Analisis Penjualan':
                        return visualize_analisis_penjualan(sheet_data, selected_business_info, model)
                    elif selected_sheet == 'Lainnya':
                        return visualize_lainnya(sheet_data, selected_business_info, model)
                    else:
                        return [], ""

                if (st.session_state.selected_sheet != selected_sheet or
                    st.session_state.selected_business_info != selected_business_info or
                    not st.session_state.interpretation_done):
                    try:
                        charts, interpretation = get_visualization_and_interpretation(sheet_data, selected_business_info, selected_sheet)
                        st.session_state.charts = charts
                        st.session_state.interpretation = interpretation
                        st.session_state.selected_sheet = selected_sheet
                        st.session_state.selected_business_info = selected_business_info
                        st.session_state.interpretation_done = True
                    except InternalServerError as e:
                        st.error("Terjadi kesalahan pada server saat mencoba mendapatkan interpretasi. Silakan coba lagi nanti.")
                        st.stop()

                def display_charts(charts):
                    for chart in charts:
                        figure = chart.get('figure')
                        try:
                            st.plotly_chart(figure)
                        except Exception as e:
                            st.write(f"### Error: Could not display Plotly figure. Error: {e}")

                # Display charts first
                if 'charts' in st.session_state:
                    display_charts(st.session_state.charts)

                # Then display interpretation with typing effect
                st.write("### ✨ Interpretasi AI")
                typing_response = ""
                typing_box = st.empty()
                for i in range(len(st.session_state.interpretation)):
                    typing_response += st.session_state.interpretation[i]
                    typing_box.markdown(
                        f'<div style="border: 2px solid #008080; padding: 10px; border-radius: 10px; margin-bottom: 10px;">'
                        f'{typing_response}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    time.sleep(0.004)

    # Hyperlink to Chatbot
    st.markdown("[Masih bingung sama hasilnya? Yuk tanyain ke Chatbot!](#chatbot)")

elif tab_selection == "Chatbot":
    st.write("### ✨ Business AIssistant")
    st.write("Ketik pertanyaan kamu di bawah ini untuk mendapatkan jawaban berdasarkan hasil visualisasi dan interpretasi data.")

    def get_chatbot_response(user_question):
        try:
            prompt = (
                "Bertindaklah sebagai data dan business analyst profesional. Tugas kamu adalah menjawab pertanyaan dari pelaku UMKM seputar bisnis UMKM mereka. "
                "Jawablah sesuai dengan pertanyaan pelaku UMKM. Kamu menjawab berdasarkan visualisasi chart dan interpretasi yang telah kamu buat sendiri. "
                "Jawab dengan gaya bahasa yang sama dari interpretasi yang kamu buat sendiri tersebut. "
                "Gunakan bahasa yang santai, mudah dipahami, friendly untuk pemula hingga ahli, dan tetap berfokus pada konteks bisnis. "
                "Selalu panggil user dengan 'Kamu', gunakan bahasa yang energik, menarik, dan tidak membosankan. "
                "Interpretasikan secara spesifik dan mendalam dalam konteks bisnis yang sesuai dan berikan rekomendasi yang dapat membantu bisnis untuk berkembang. "
                "Jelaskan data dengan detail, sampaikan informasi yang bermanfaat kepada pelaku UMKM. "
                "Tekankan kalimat atau kata yang penting dengan **bold**, _italic_, atau __underline__ sesuai kebutuhan. Buatkan poin-poin atau tabel jika perlu. "
                "Berikut adalah pertanyaan yang harus kamu jawab.\n"
                f"Pertanyaan: {user_question}\n"
                f"Jawab dalam konteks bisnis, berdasarkan hasil visualisasi dan interpretasi yang telah kamu buat sendiri.\n\n"
                f"**Ini adalah hasil Visualisasi dan Interpretasi yang sudah kamu buat sendiri sebelumnya:**\n"
            )

            if 'charts' in st.session_state:
                prompt += "Berikut adalah visualisasi yang telah ditampilkan:\n"
                for idx, chart in enumerate(st.session_state.charts):
                    prompt += f"Visualisasi {idx + 1}: {chart.get('description', 'Tidak ada deskripsi')}\n"

            if 'interpretation' in st.session_state:
                prompt += "\nInterpretasi sebelumnya:\n"
                prompt += st.session_state.interpretation

            # Update response generation method
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"### Error: {e}"

    # Display previous visualizations and interpretations
    st.write("### **Hasil Visualisasi dan Interpretasi Sebelumnya**")
    
    if 'charts' in st.session_state:
        for chart in st.session_state.charts:
            figure = chart.get('figure')
            try:
                st.plotly_chart(figure)
            except Exception as e:
                st.write(f"### Error: Could not display Plotly figure. Error: {e}")

    if 'interpretation' in st.session_state:
        st.write("#### **Interpretasi:**")
        interpretation_text = st.session_state.interpretation
        st.markdown(
            f'<div style="border: 2px solid #008080; padding: 10px; border-radius: 10px; margin-bottom: 10px;">'
            f'{interpretation_text}'
            f'</div>',
            unsafe_allow_html=True
        )

    # Function to display chat history in styled boxes
    def display_chat(chat_history, typing_response=""):
        chat_display = '<div style="border: 2px solid #e0e0e0; padding: 10px; border-radius: 10px; width: 100%; white-space: pre-wrap;">'
        for chat in chat_history:
            if "user" in chat:
                chat_display += (
                    f'<div style="display: flex; justify-content: flex-end; margin-bottom: 5px;">'
                    f'<div style="background-color: #dcf8c6; padding: 10px; border-radius: 10px; max-width: 80%;">'
                    f'<strong>You:</strong> {chat["user"]}'
                    f'</div>'
                    f'</div>'
                )
            if "bot" in chat:
                chat_display += (
                    f'<div style="display: flex; justify-content: flex-start; margin-bottom: 5px;">'
                    f'<div style="padding: 10px; border-radius: 10px; max-width: 80%;">'
                    f'<strong>Bot:</strong> {chat["bot"]}'
                    f'</div>'
                    f'</div>'
                )
        if typing_response:
            chat_display += (
                f'<div style="display: flex; justify-content: flex-start; margin-bottom: 5px;">'
                f'<div style="padding: 10px; border-radius: 10px; max-width: 80%;">'
                f'<strong>Bot:</strong> {typing_response}'
                f'</div>'
                f'</div>'
            )
        chat_display += '</div>'
        return chat_display

    # Create a container for the chat history
    chat_container = st.empty()

    # Chat interface in the middle
    def chat_interface():
        with st.form(key="chat_form"):
            user_input = st.text_area("Tanya AI", placeholder="Ketik pertanyaan kamu di sini...", key="chat_input")
            submit_button = st.form_submit_button(label="Kirim")

            # Submit handler
            if submit_button or st.session_state.get('submit_on_enter', False):
                if user_input:
                    st.session_state.chat_history.append({"user": user_input})
                    st.session_state.keep_interpretation = True
                    chatbot_response = get_chatbot_response(user_input)
                    st.session_state.chatbot_response = chatbot_response
                    st.session_state.chat_history.append({"bot": ""})  # Temporary empty response for typing effect

                    # Typing effect
                    typing_response = ""
                    typing_box = st.empty()
                    for i in range(len(chatbot_response)):
                        typing_response += chatbot_response[i]
                        with typing_box.container():
                            chat_container.markdown(display_chat(st.session_state.chat_history[:-1], typing_response), unsafe_allow_html=True)
                        time.sleep(0.004)

                    # Replace the temporary empty response with the final response
                    st.session_state.chat_history[-1]["bot"] = chatbot_response

                    # Reset submit_on_enter flag
                    st.session_state.submit_on_enter = False

        # Set flag for Enter key press to trigger form submission
        st.session_state.submit_on_enter = st.session_state.get('submit_on_enter', False) or submit_button

        chat_container.markdown(display_chat(st.session_state.chat_history), unsafe_allow_html=True)

    # Call chat interface
    chat_interface()

    # Hyperlink to Dashboard
    st.markdown("[Mau lihat informasi bisnis lain dari bisnis Kamu? Klik ini ya!](#)")
