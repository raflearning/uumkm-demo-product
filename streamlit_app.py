import streamlit as st
import pandas as pd
import time
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

# Inisialisasi session state
if 'charts' not in st.session_state:
    st.session_state.charts = []
if 'interpretation' not in st.session_state:
    st.session_state.interpretation = ""
if 'selected_sheet' not in st.session_state:
    st.session_state.selected_sheet = ""
if 'selected_business_info' not in st.session_state:
    st.session_state.selected_business_info = ""
if 'chatbot_response' not in st.session_state:
    st.session_state.chatbot_response = ""
if 'interpretation_done' not in st.session_state:
    st.session_state.interpretation_done = False
if 'keep_interpretation' not in st.session_state:
    st.session_state.keep_interpretation = False

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

                if 'charts' in st.session_state:
                    display_charts(st.session_state.charts)

                def display_interpretation(interpretation):
                    interpretation_text = ""
                    interpretation_box = st.empty()
                    for i in range(len(interpretation)):
                        interpretation_text += interpretation[i]
                        interpretation_box.markdown(interpretation_text)
                        time.sleep(0.004)

                if 'interpretation' in st.session_state:
                    display_interpretation(st.session_state.interpretation)

                st.write("---")
                st.write("[Masih bingung sama hasilnya? Yuk kunjungi Chatbot!](#)")


elif tab_selection == "Chatbot":
    st.write("💬 **Chatbot AI**")
    st.write("Kamu masih punya pertanyaan terkait hasil visualisasinya? Tanyakan di bawah ya!")

    # Display visualizations and interpretations
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
        interpretation_text = ""
        interpretation_box = st.empty()
        for i in range(len(st.session_state.interpretation)):
            interpretation_text += st.session_state.interpretation[i]
        interpretation_box.markdown(interpretation_text)
        time.sleep(0.004)

    # Text generation
    st.write("### **Ajukan Pertanyaan Kamu**")
    
    # Text area for user question input
    user_question = st.text_area("Tuliskan pertanyaan di sini...", key="chat_input", height=100)

    # Add a button for 'enter' functionality
    if st.button("✈️ Kirim"):
        if user_question:
            if state_manager.is_new_input(user_question):
                state_manager.update_last_input(user_question)
                try:
                    prompt = (
                        f"Pertanyaan: {user_question}\n"
                        f"Jawab dalam konteks bisnis, berdasarkan hasil visualisasi dan interpretasi yang ada.\n\n"
                        f"**Visualisasi dan Interpretasi Sebelumnya:**\n"
                    )
                    
                    if 'charts' in st.session_state:
                        prompt += "Berikut adalah visualisasi yang telah ditampilkan:\n"
                        for idx, chart in enumerate(st.session_state.charts):
                            prompt += f"Visualisasi {idx + 1}: {chart.get('description', 'Tidak ada deskripsi')}\n"
                    
                    if 'interpretation' in st.session_state:
                        prompt += "\nInterpretasi sebelumnya:\n"
                        for interpretation in st.session_state.interpretation:
                            prompt += f"{interpretation}\n"

                    response = model.generate_content(prompt)
                    st.session_state.chatbot_response = response.text

                    st.write("#### **Jawaban Chatbot:**")
                    typing_response = ""
                    typing_box = st.empty()
                    for i in range(len(st.session_state.chatbot_response)):
                        typing_response += st.session_state.chatbot_response[i]
                        typing_box.markdown(typing_response)
                        time.sleep(0.004)
                except Exception as e:
                    st.write(f"### Error: {e}")
