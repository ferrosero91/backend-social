from fastapi import APIRouter, HTTPException, status, Request
from typing import Dict, Any

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Webhook endpoint for WhatsApp integration.
    Receives messages from WhatsApp and processes them through the interview agent.
    """
    data = await request.json()
    
    # Placeholder for WhatsApp webhook logic
    # In production, integrate with WhatsApp Business API or Twilio
    
    message_type = data.get('type')
    sender = data.get('from')
    message_text = data.get('text', {}).get('body', '')
    
    # Process message through interview agent
    # This would involve:
    # 1. Identify the candidate by phone number
    # 2. Get or create active interview session
    # 3. Process the message as an answer
    # 4. Generate next question or complete interview
    
    return {
        "status": "received",
        "message": "WhatsApp message processed",
        "sender": sender
    }


@router.post("/telegram")
async def telegram_webhook(request: Request):
    """
    Webhook endpoint for Telegram integration.
    Receives messages from Telegram and processes them through the interview agent.
    """
    data = await request.json()
    
    # Placeholder for Telegram webhook logic
    # In production, integrate with Telegram Bot API
    
    message = data.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    message_text = message.get('text', '')
    
    # Process message through interview agent
    # Similar logic to WhatsApp webhook
    
    return {
        "status": "received",
        "message": "Telegram message processed",
        "chat_id": chat_id
    }


@router.get("/whatsapp")
async def whatsapp_webhook_verification(request: Request):
    """
    Verification endpoint for WhatsApp webhook.
    Required by WhatsApp Business API for webhook setup.
    """
    params = request.query_params
    mode = params.get('hub.mode')
    token = params.get('hub.verify_token')
    challenge = params.get('hub.challenge')
    
    # Verify token (should match your configured token)
    VERIFY_TOKEN = "your_verify_token_here"
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return int(challenge)
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verification failed"
    )
