import os
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def generate_payment_link(amount_usd: float, description: str, client_email: str = None) -> str:
    """
    Linda uses this function to create a ready-to-pay Stripe Checkout link
    to send to freelance clients to collect upfront deposits.
    """
    if not stripe.api_key or stripe.api_key == "your_stripe_secret_key_here":
        return "⚠️ Erro: Link de pagamento indisponível. A chave da Stripe não foi configurada."

    try:
        # Convert dollars to cents for Stripe
        amount_cents = int(amount_usd * 100)
        
        session_params = {
            "payment_method_types": ["card"],
            "line_items": [{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": description,
                    },
                    "unit_amount": amount_cents,
                },
                "quantity": 1,
            }],
            "mode": "payment",
            # Users can replace these with actual URLs later
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
        }
        
        if client_email:
            session_params["customer_email"] = client_email
            
        session = stripe.checkout.Session.create(**session_params)
        return session.url
        
    except Exception as e:
        return f"Desculpe chefe, erro ao gerar a cobrança: {str(e)}"
