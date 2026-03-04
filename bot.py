from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, Application
import os
from dotenv import load_dotenv
from ai_brain import get_linda_response
from payments import generate_payment_link

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    welcome_message = (
        "Olá, chefe! Eu sou a Linda, sua Assistente Executiva Freelancer. 💼\n\n"
        f"⚠️ **IMPORTANTE:** Seu Chat ID é `{chat_id}`.\n"
        "Para que eu possa te enviar notificações automáticas de vagas novas, por favor coloque esse número no código do arquivo `main.py` onde está escrito `SEU_CHAT_ID_AQUI`.\n\n"
        "Estou aqui para gerenciar seus clientes, enviar propostas e garantir seus pagamentos.\n"
        "Como posso ajudar hoje? Você pode me enviar uma mensagem de cliente e eu rascunho a resposta!"
    )
    await context.bot.send_message(chat_id=chat_id, text=welcome_message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # Send a typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    # Get Linda's AI response
    linda_reply = get_linda_response(user_message)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=linda_reply)

async def create_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to generate a Stripe payment link instantly from Telegram"""
    # Expected format: /invoice 500 Orçamento Website (optional email)
    args = context.args
    if len(args) < 2:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="⚠️ Uso incorreto chefe. O formato é: `/invoice [Valor_USD] [Descrição do Projeto] [Email_opcional]`\nEx: `/invoice 500 Criar Site Institucional`",
            parse_mode="Markdown"
        )
        return
        
    try:
        amount = float(args[0])
        description = " ".join(args[1:])
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        link = generate_payment_link(amount, description)
        
        msg = f"💸 **Cobrança Gerada!**\n\nChefe, aqui está o link seguro da Stripe para o cliente no valor de **${amount:.2f}**:\n\n🔗 {link}\n\nCopie e mande pro cliente para garantir o sinal."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode='Markdown')
        
    except ValueError:
         await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠ O valor precisa ser um número (só use ponto para centavos).")

def create_bot_application() -> Application:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "your_telegram_bot_token_here":
        print("Error: TELEGRAM_BOT_TOKEN not found in .env")
        return None

    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    invoice_handler = CommandHandler('invoice', create_invoice)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(invoice_handler)
    application.add_handler(message_handler)

    return application
