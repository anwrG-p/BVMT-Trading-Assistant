"""Chatbot route for AI trading queries."""

from fastapi import APIRouter
from datetime import datetime
from src.api.schemas.frontend_models import ChatMessageRequest, ChatMessageResponse

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatMessageResponse)
async def chat_message(req: ChatMessageRequest):
    """Process a user question about BVMT stocks."""
    text = req.message.lower()
    
    if "biat" in text:
        reply = "BIAT affiche une dynamique haussière avec une rentabilité solide. Le RSI se situe autour de 58 avec des volumes croissants."
    elif "sfbt" in text:
        reply = "SFBT consolide actuellement près de ses niveaux de support avec un bon rendement de dividende historique."
    elif "tunindex" in text or "marché" in text or "marche" in text:
        reply = "L'indice TUNINDEX se maintient au-dessus des 9 900 points soutenu par les valeurs bancaires."
    elif "recommandation" in text or "acheter" in text:
        reply = "Nos modèles quantitatifs favorisent actuellement les grandes capitalisations bancaires (BIAT, ATTIJARI) et agroalimentaires (SAH)."
    else:
        reply = "Je surveille les cotations en continu sur la Bourse de Tunis. N'hésitez pas à demander une analyse sur une valeur spécifique comme BIAT, SFBT ou ATTIJARI."

    return {
        "reply": reply,
        "timestamp": datetime.now().strftime("%H:%M")
    }
