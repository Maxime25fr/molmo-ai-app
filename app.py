import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import base64

# Configuration de la page
st.set_page_config(
    page_title="Nexus AI Assistant",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS Premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: radial-gradient(circle at top right, #1a1c2c, #0e1117);
        color: #ffffff;
    }
    
    /* Titre avec effet de lueur */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #0080ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 0 10px rgba(0, 212, 255, 0.3));
    }
    
    /* Sidebar stylisée */
    section[data-testid="stSidebar"] {
        background-color: rgba(22, 27, 34, 0.8);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Bulles de chat */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
        transition: transform 0.2s ease;
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 212, 255, 0.2) !important;
    }
    
    /* Boutons */
    .stButton>button {
        background: linear-gradient(135deg, #00d4ff 0%, #0080ff 100%);
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2);
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
    }
    
    /* Descriptions */
    .model-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 15px;
        border-left: 4px solid #00d4ff;
        margin: 10px 0;
    }
    
    .model-desc {
        font-size: 0.85rem;
        color: #a0a0a0;
        line-height: 1.4;
    }
    
    /* Masquer les éléments inutiles */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Configuration des modèles
MODELS_CONFIG = {
    "Molmo 2 8B": {
        "id": "allenai/molmo-2-8b:free",
        "desc": "L'expert en vision. Capable d'analyser, décrire et comprendre vos images avec une précision chirurgicale.",
        "vision": True
    },
    "MiMo": {
        "id": "mistralai/mistral-7b-instruct:free",
        "desc": "L'expert en texte. Optimisé pour des réponses rapides, précises et un raisonnement logique fluide.",
        "vision": False
    }
}

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Initialisation de l'état de session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_model" not in st.session_state:
    st.session_state.current_model = "Molmo 2 8B"

# Barre latérale
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00d4ff;'>Nexus Control</h2>", unsafe_allow_html=True)
    st.divider()
    
    # Sélection du modèle avec détection de changement
    new_model = st.selectbox(
        "Intelligence Artificielle",
        options=list(MODELS_CONFIG.keys()),
        index=list(MODELS_CONFIG.keys()).index(st.session_state.current_model)
    )
    
    # Logique de réinitialisation au changement de modèle
    if new_model != st.session_state.current_model:
        st.session_state.current_model = new_model
        st.session_state.messages = []
        st.rerun()
    
    model_info = MODELS_CONFIG[st.session_state.current_model]
    
    # Carte descriptive du modèle
    st.markdown(f"""
        <div class='model-card'>
            <div style='font-weight: 600; color: #ffffff; margin-bottom: 5px;'>{st.session_state.current_model}</div>
            <div class='model-desc'>{model_info['desc']}</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Affichage conditionnel de l'upload d'image
    uploaded_file = None
    if model_info["vision"]:
        st.markdown("### 📸 Vision")
        uploaded_file = st.file_uploader("Analyser une image", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Image chargée", use_container_width=True)
    else:
        st.info("💡 Seul Molmo 2 8B supporte l'analyse d'images.")
    
    st.spacer = st.empty()
    st.divider()
    
    if st.button("🗑️ Réinitialiser Nexus"):
        st.session_state.messages = []
        st.rerun()

# Récupération de la clé API
api_key = st.secrets.get("OPENROUTER_API_KEY")

if not api_key:
    st.error("Configuration manquante : OPENROUTER_API_KEY")
    st.stop()

# Initialisation du client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# Interface principale
st.markdown("<h1 class='main-title'>Nexus AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e; margin-bottom: 2rem;'>L'intelligence artificielle, redéfinie.</p>", unsafe_allow_html=True)

# Affichage des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie
if prompt := st.chat_input("Transmettez votre commande..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Préparation du contenu (Multimodal ou Texte seul)
        if model_info["vision"] and uploaded_file:
            content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{encode_image(image)}"}
                }
            ]
        else:
            content = prompt

        try:
            response = client.chat.completions.create(
                model=model_info["id"],
                messages=[{"role": "user", "content": content}],
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Nexus a rencontré une anomalie : {e}")

st.markdown("---")
st.caption("Nexus AI Framework v2.0 | Sécurisé & Optimisé")
