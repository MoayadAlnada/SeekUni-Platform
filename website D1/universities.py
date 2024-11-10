import streamlit as st
import pandas as pd
import math
from openai import OpenAI
import os

# Streamlit app setup
st.set_page_config(page_title="Üniversite Tavsiye Sistemi", page_icon="🎓", layout="centered")

# Custom CSS for enhanced styling
st.markdown("""
    <style>
        body {
            background: linear-gradient(120deg, #f9f9f9, #ffffff) !important;
            font-family: 'Roboto', sans-serif;
            color: #000000 !important;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        .container {
            max-width: 800px;
            width: 100%;
            text-align: center;
        }
        .header {
            background-color: #4b0082 !important;
            color: white !important;
            padding: 20px;
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            border-radius: 12px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            margin-bottom: 20px;
        }
        .response-box {
            background-color: #f9f9f9;
            color: #000;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            font-size: 14px;
            text-align: left;
        }
        .card-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
        }
        .card {
            background-color: #ffffff;
            color: #000;
            border: 1px solid #ddd;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            width: 280px;
            padding: 15px;
            text-align: left;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
        }
        .pagination {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        .pagination button {
            background-color: #4b0082;
            color: white;
            border: none;
            padding: 8px 12px;
            margin: 0 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .pagination button:hover {
            background-color: #6a0dad;
        }
        .pagination .active {
            background-color: #6a0dad;
        }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
    <div class="header">
        🎓 Üniversite Tavsiye Sistemi - Türkiye
    </div>
""", unsafe_allow_html=True)

# CSV file path
file_path = "universities.csv"

# OpenAI client setup
try:
    # client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY")) # Use environment variable
    client = OpenAI(api_key="YOUR_OPENAI_API_KEY_HERE") # Replace with your key
except Exception as e:
    st.error(f"OpenAI API Key not found or invalid: {e}")
    st.stop()

# Store chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to interact with OpenAI
def ask_ai_about_search(data, query):
    """Interact with OpenAI to process the search query."""
    data_summary = f"Columns: {', '.join(data.columns)}"
    prompt = f"""
    Üniversite aramaları için yardım ediyorsunuz. Aşağıdaki verilerle ilgili soruları yanıtlayın:
    {data_summary}
    İşte gelen sorgu: "{query}".
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen, üniversite arama soruları için yardımcı olan bir asistansın."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Bir hata oluştu: {str(e)}"

try:
    # Load the CSV file
    data = pd.read_csv(file_path)
    st.success(f"CSV başarıyla yüklendi: {file_path}!", icon="✅")

    # Validate required columns
    required_columns = ["University Name", "Department Name", "Faculty Name", "University URL"]
    missing_columns = [col for col in required_columns if col not in data.columns]

    if missing_columns:
        st.error(f"CSV dosyasında eksik sütunlar var: {', '.join(missing_columns)}")
    else:
        # Ensure relevant columns are strings
        for col in required_columns:
            data[col] = data[col].astype(str).str.strip()

        # User choice: Filters or AI Chat Assistant
        user_choice = st.radio("Arama yönteminizi seçin:", ["Filtrelerle Arama", "AI Sohbet Asistanı"], horizontal=True)

        if user_choice == "Filtrelerle Arama":
            st.subheader("Filtrelerle Arama")
            department = st.selectbox("Bölüm Seçin:", [""] + list(data["Department Name"].unique()))
            faculty = st.selectbox("Fakülte Seçin:", [""] + list(data["Faculty Name"].unique()))
            university = st.selectbox("Üniversite Seçin:", [""] + list(data["University Name"].unique()))

            if st.button("Sonuçları Göster"):
                # Apply filters based on user selection
                filtered_data = data.copy()
                if department:
                    filtered_data = filtered_data[filtered_data["Department Name"] == department]
                if faculty:
                    filtered_data = filtered_data[filtered_data["Faculty Name"] == faculty]
                if university:
                    filtered_data = filtered_data[filtered_data["University Name"] == university]

                if not filtered_data.empty:
                    st.markdown("<div class='card-container'>", unsafe_allow_html=True)
                    for _, row in filtered_data.iterrows():
                        st.markdown(f"""
                            <div class='card'>
                                <h4>{row['University Name']}</h4>
                                <p><strong>Bölüm:</strong> {row['Department Name']}</p>
                                <p><strong>Fakülte:</strong> {row['Faculty Name']}</p>
                                <p><a href="{row['University URL']}" target="_blank">Üniversite Linki</a></p>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.warning("Seçimlerinize uygun sonuç bulunamadı.")

        elif user_choice == "AI Sohbet Asistanı":
            st.subheader("🔍 Üniversiteler veya Bölümler Hakkında Soru Sorun")

            # Display chat history
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"<div class='response-box'><strong>Kullanıcı:</strong> {message['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='response-box'><strong>Asistan:</strong> {message['content']}</div>", unsafe_allow_html=True)

            # Compact search bar and buttons under chat messages
            search_query = st.text_input("Soru girin:", placeholder="Sorunuzu buraya yazın...", key="query_input")

            if st.button("Gönder"):
                if search_query.strip():  # Check if input is not empty
                    with st.spinner("Sorgunuzu işliyorum..."):
                        # Add user input to the chat history
                        st.session_state.messages.append({"role": "user", "content": search_query})
                        ai_response = ask_ai_about_search(data, search_query)

                        # Add AI response to the chat history
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})

except FileNotFoundError:
    st.error("CSV dosyası bulunamadı. Lütfen dosya yolunu kontrol edin.")
except Exception as e:
    st.error(f"Bir hata oluştu: {str(e)}")
