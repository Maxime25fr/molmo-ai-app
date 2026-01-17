import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import base64

# Configuration de la page
st.set_page_config(
    page_title="Multi-IA Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé pour une interface esthétique
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .stSidebar {
        background-color: #161b22;
    }
    h1 {
        color: #00d4ff;
        font-family: 'Inter', sans-serif;
        text-align: center;
    }
    .model-desc {
        font-size: 0.9em;
        color: #8b949e;
        font-style: italic;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #00d4ff;
        color: #0e1117;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #00a3cc;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# Configuration des modèles (Les clés sont récupérées via st.secrets)
MODELS_CONFIG = {
    "Molmo 2 8B": {
        "id": "allenai/molmo-2-8b:free",
        "secret_key": "MOLMO_KEY",
        "desc": "Un modèle multimodal ultra-performant capable de comprendre et d'analyser des images avec une précision exceptionnelle. Idéal pour la vision par ordinateur et les descriptions détaillées."
    },
    "MiMo": {
        "id": "mistralai/mistral-7b-instruct:free",
        "secret_key": "MIMO_KEY",
        "desc": "Un modèle optimisé pour la rapidité et l'efficacité textuelle. Excellent pour le raisonnement logique, la rédaction et les conversations fluides."
    }
}

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Barre latérale
with st.sidebar:
    st.header("⚙️ Configuration")
    
    selected_model_name = st.selectbox(
        "Choisir votre modèle IA",
        options=list(MODELS_CONFIG.keys())
    )
    
    model_info = MODELS_CONFIG[selected_model_name]
    st.markdown(f"<div class='model-desc'>{model_info['desc']}</div>", unsafe_allow_html=True)
    
    st.divider()
    
    uploaded_file = st.file_uploader("📸 Télécharger une image (Molmo uniquement)", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Image prête pour analyse", use_container_width=True)
    
    if st.button("🗑️ Effacer la conversation"):
        st.session_state.messages = []
        st.rerun()

# Récupération de la clé API via les Secrets Streamlit
api_key = st.secrets.get(model_info["secret_key"])

if not api_key:
    st.error(f"La clé API pour {selected_model_name} n'est pas configurée dans les Secrets Streamlit.")
    st.stop()

# Initialisation du client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# Interface principale
st.title("🚀 Multi-IA Assistant")

# Historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de chat
if prompt := st.chat_input("Posez votre question ici..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Préparation du contenu
        if selected_model_name == "Molmo 2 8B" and uploaded_file:
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
            st.error(f"Erreur : {e}")

st.markdown("---")
st.caption("Interface IA Premium - Développé pour une expérience utilisateur fluide.")
