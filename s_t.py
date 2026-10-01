import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# ── Estilos ────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #fffde7; color: #333333; }

div.stButton > button {
    background-color: #f9a825;
    color: white;
    border-radius: 10px;
    padding: 10px 24px;
    border: none;
    font-size: 16px;
    transition: background-color 0.3s ease;
}
div.stButton > button:hover {
    background-color: #f57f17;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #fff9c4;
}

h1, h2, h3 { color: #f57f17; }
</style>
""", unsafe_allow_html=True)

# ── Encabezado ─────────────────────────────────────────────────────
st.title("🌐 TRADUCTOR DE VOZ")
st.subheader("Habla y traduce al instante.")

try:
    image = Image.open('Robot traductor en ciudad vibrante.png')
    st.image(image, width=300)
except:
    st.info("📷 Imagen no encontrada.")

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🗣️ Traductor")
    st.info(
        "1️⃣ Presiona el botón del micrófono\n\n"
        "2️⃣ Habla lo que quieres traducir\n\n"
        "3️⃣ Selecciona los idiomas\n\n"
        "4️⃣ Presiona **Convertir**"
    )
    st.markdown("---")
    st.caption("Desarrollado con gTTS + Google Translate")

# ── Botón de voz ───────────────────────────────────────────────────
st.markdown("### 🎤 Toca el botón y habla")

stt_button = Button(label="🎤  Escuchar", width=300, height=50)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'es-ES';

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.onend = function() { console.log("Reconocimiento detenido"); }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

# ── Resultado de voz ───────────────────────────────────────────────
if result and "GET_TEXT" in result:
    texto_reconocido = str(result.get("GET_TEXT"))

    st.markdown("---")
    st.success(f"🗣️ **Escuché:** {texto_reconocido}")

    try:
        os.mkdir("temp")
    except:
        pass

    translator = Translator()

    # ── Configuración de idiomas ───────────────────────────────────
    st.markdown("### ⚙️ Configuración de traducción")
    col1, col2 = st.columns(2)

    idiomas = {
        "Inglés":   "en",
        "Español":  "es",
        "Bengali":  "bn",
        "Coreano":  "ko",
        "Mandarín": "zh-cn",
        "Japonés":  "ja",
    }

    with col1:
        in_lang = st.selectbox("🔤 Idioma de entrada", list(idiomas.keys()))
        input_language = idiomas[in_lang]

    with col2:
        out_lang = st.selectbox("🔤 Idioma de salida", list(idiomas.keys()), index=1)
        output_language = idiomas[out_lang]

    acentos = {
        "Defecto":       "com",
        "Español":       "com.mx",
        "Reino Unido":   "co.uk",
        "Estados Unidos":"com",
        "Canada":        "ca",
        "Australia":     "com.au",
        "Irlanda":       "ie",
        "Sudáfrica":     "co.za",
    }

    english_accent = st.selectbox("🗺️ Selecciona el acento", list(acentos.keys()))
    tld = acentos[english_accent]

    # ── Función de traducción ──────────────────────────────────────
    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    # ── Opciones y botón convertir ─────────────────────────────────
    st.markdown("---")
    display_output_text = st.checkbox("📄 Mostrar texto traducido")

    if st.button("🔄 Convertir y reproducir"):
        with st.spinner("Traduciendo..."):
            result_file, output_text = text_to_speech(
                input_language, output_language, texto_reconocido, tld)
            audio_file = open(f"temp/{result_file}.mp3", "rb")
            audio_bytes = audio_file.read()

        st.markdown("### 🔊 Tu audio traducido:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
        st.success("✅ ¡Traducción completada!")

        if display_output_text:
            st.markdown("### 📝 Texto traducido:")
            st.info(output_text)

    # ── Limpieza de archivos ───────────────────────────────────────
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n * 86400:
                    os.remove(f)
    remove_files(7)
        
    




        
    


