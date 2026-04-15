from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes, Application
)
import os
from dotenv import load_dotenv
from datetime import datetime
from ai_brain import get_linda_response, get_smart_summary
from database import (
    add_task, list_tasks, complete_task, delete_task,
    add_project, add_step, complete_step, list_projects, finish_project,
    add_schedule_entry, get_schedule, get_summary
)

load_dotenv()

# ─── /start ───────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 Olá, Igor! Sou a **Linda**, sua secretária executiva pessoal.\n\n"
        "Estou aqui para organizar sua vida! Aqui estão os meus comandos:\n\n"
        "📋 *TAREFAS*\n"
        "`/tarefa [título]` — adicionar tarefa hoje\n"
        "`/tarefas` — ver tarefas pendentes de hoje\n"
        "`/feita [id]` — marcar tarefa como concluída\n\n"
        "📁 *PROJETOS*\n"
        "`/projeto [nome]` — criar projeto\n"
        "`/projetos` — listar projetos ativos\n"
        "`/etapa [id_proj] [etapa]` — adicionar etapa\n\n"
        "📅 *AGENDA*\n"
        "`/agenda` — ver agenda de hoje\n"
        "`/marcar [HH:MM] [evento]` — adicionar compromisso\n\n"
        "⚡ *ATALHOS*\n"
        "`/dia` — resumo completo do dia\n"
        "`/briefing` — Linda te prepara para o dia (com IA)\n\n"
        "💬 Ou simplesmente *me manda uma mensagem* e eu respondo!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ─── TAREFAS ──────────────────────────────────────────────────────────────────
async def cmd_add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📋 Me diga o título da tarefa:\nEx: `/tarefa Revisar relatório do cliente`", parse_mode="Markdown")
        return
    title = " ".join(context.args)
    task = add_task(title)
    await update.message.reply_text(
        f"✅ Tarefa adicionada!\n\n📌 *#{task['id']}* {task['title']}\n📅 Para hoje",
        parse_mode="Markdown"
    )

async def cmd_list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = list_tasks()
    if not tasks:
        await update.message.reply_text("🎉 Nenhuma tarefa pendente para hoje, chefe! Dia livre ou tudo feito.")
        return

    lines = ["📋 *Tarefas de hoje:*\n"]
    for t in tasks:
        pri = "🔴" if t.get("priority") == "alta" else "🟡" if t.get("priority") == "normal" else "🟢"
        lines.append(f"{pri} *#{t['id']}* {t['title']}")
    lines.append(f"\n_Total: {len(tasks)} pendente(s)_\nUse `/feita [id]` para marcar como concluída.")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def cmd_done_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Use: `/feita [id]`\nEx: `/feita 3`", parse_mode="Markdown")
        return
    task_id = int(context.args[0])
    if complete_task(task_id):
        await update.message.reply_text(f"🏆 Tarefa #{task_id} concluída! Bora pro próximo, chefe!")
    else:
        await update.message.reply_text(f"⚠️ Não encontrei a tarefa #{task_id}.")

# ─── PROJETOS ─────────────────────────────────────────────────────────────────
async def cmd_add_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📁 Me diga o nome do projeto:\nEx: `/projeto Site Portfólio 2025`", parse_mode="Markdown")
        return
    name = " ".join(context.args)
    proj = add_project(name)
    await update.message.reply_text(
        f"📁 Projeto criado!\n\n*#{proj['id']}* {proj['name']}\n\nAdicione etapas com `/etapa {proj['id']} [nome da etapa]`",
        parse_mode="Markdown"
    )

async def cmd_list_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    projects = list_projects()
    if not projects:
        await update.message.reply_text("📂 Nenhum projeto ativo no momento.")
        return

    lines = ["📁 *Projetos Ativos:*\n"]
    for p in projects:
        total = len(p["steps"])
        done = len([s for s in p["steps"] if s["done"]])
        progress = f"[{done}/{total} etapas]" if total else "[sem etapas]"
        deadline = f" 📅 {p['deadline']}" if p.get("deadline") else ""
        lines.append(f"*#{p['id']}* {p['name']} {progress}{deadline}")
        for s in p["steps"]:
            icon = "☑️" if s["done"] else "⬜"
            lines.append(f"  {icon} {s['title']}")
        lines.append("")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def cmd_add_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2 or not context.args[0].isdigit():
        await update.message.reply_text("Use: `/etapa [id_projeto] [nome da etapa]`\nEx: `/etapa 1 Criar wireframe`", parse_mode="Markdown")
        return
    proj_id = int(context.args[0])
    step_title = " ".join(context.args[1:])
    if add_step(proj_id, step_title):
        await update.message.reply_text(f"⬜ Etapa adicionada ao projeto #{proj_id}: *{step_title}*", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"⚠️ Projeto #{proj_id} não encontrado.")

# ─── AGENDA ───────────────────────────────────────────────────────────────────
async def cmd_agenda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%Y-%m-%d")
    entries = get_schedule(today)
    label = datetime.now().strftime("%d/%m/%Y")
    if not entries:
        await update.message.reply_text(f"📅 Agenda de hoje ({label}) está vazia.\nUse `/marcar HH:MM evento` para adicionar.")
        return

    lines = [f"📅 *Agenda de hoje ({label}):*\n"]
    for e in entries:
        lines.append(f"🕐 {e['time']} — {e['event']}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def cmd_add_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Use: `/marcar [HH:MM] [evento]`\nEx: `/marcar 14:30 Reunião com cliente`", parse_mode="Markdown")
        return
    time_str = context.args[0]
    event = " ".join(context.args[1:])
    today = datetime.now().strftime("%Y-%m-%d")
    add_schedule_entry(today, time_str, event)
    await update.message.reply_text(f"📅 Compromisso agendado!\n\n🕐 {time_str} — {event}", parse_mode="Markdown")

# ─── RESUMO DO DIA ────────────────────────────────────────────────────────────
async def cmd_day_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_summary()
    today = datetime.now().strftime("%d/%m/%Y")
    lines = [f"⚡ *Resumo do Dia — {today}*\n"]

    # Agenda
    if s["agenda"]:
        lines.append("📅 *Agenda:*")
        for e in s["agenda"]:
            lines.append(f"  🕐 {e['time']} — {e['event']}")
        lines.append("")

    # Tarefas
    lines.append(f"📋 *Tarefas:* {s['pending_tasks']} pendente(s) | {s['done_tasks']} feita(s)")
    for t in s["tasks"][:5]:
        lines.append(f"  ⬜ #{t['id']} {t['title']}")
    if s["pending_tasks"] > 5:
        lines.append(f"  _...e mais {s['pending_tasks'] - 5}_")
    lines.append("")

    # Projetos
    lines.append(f"📁 *Projetos ativos:* {s['active_projects']}")
    for p in s["projects"][:3]:
        done = len([st for st in p["steps"] if st["done"]])
        total = len(p["steps"])
        lines.append(f"  📌 {p['name']} [{done}/{total}]")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

# ─── BRIEFING COM IA ─────────────────────────────────────────────────────────
async def cmd_briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Preparando seu briefing do dia, chefe...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    briefing = get_smart_summary()
    await update.message.reply_text(f"🌅 *Briefing do Dia*\n\n{briefing}", parse_mode="Markdown")

# ─── CHAT LIVRE COM IA ───────────────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    summary = get_summary()
    reply = get_linda_response(user_message, context_data=summary)
    await update.message.reply_text(reply)

# ─── APP ─────────────────────────────────────────────────────────────────────
def create_bot_application() -> Application:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ERRO: TELEGRAM_BOT_TOKEN não encontrado no .env")
        return None

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", start))
    app.add_handler(CommandHandler("tarefa", cmd_add_task))
    app.add_handler(CommandHandler("tarefas", cmd_list_tasks))
    app.add_handler(CommandHandler("feita", cmd_done_task))
    app.add_handler(CommandHandler("projeto", cmd_add_project))
    app.add_handler(CommandHandler("projetos", cmd_list_projects))
    app.add_handler(CommandHandler("etapa", cmd_add_step))
    app.add_handler(CommandHandler("agenda", cmd_agenda))
    app.add_handler(CommandHandler("marcar", cmd_add_schedule))
    app.add_handler(CommandHandler("dia", cmd_day_summary))
    app.add_handler(CommandHandler("briefing", cmd_briefing))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    return app
