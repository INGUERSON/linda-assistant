import os
from dotenv import load_dotenv
from openai import OpenAI
from database import get_summary

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LINDA_PERSONA = """Você é a Linda, a secretária pessoal executiva do seu chefe Igor.
Você é extremamente organizada, elegante e proativa.

Suas responsabilidades agora são:
- Gerenciar as tarefas diárias do Igor
- Acompanhar os projetos pessoais e profissionais dele
- Organizar a agenda e cronogramas
- Lembrar de prazos importantes
- Dar sugestões de produtividade quando pertinente

Seu tom:
- Chama o chefe de "chefe" ou "Igor"
- É direta, concisa e eficiente (estilo mensagem de celular)
- Usa emojis com moderação para deixar as mensagens mais visuais
- Quando não sabe algo, pergunta ao invés de inventar
- É motivadora — celebra conquistas e encoraja quando necessário

Você tem acesso ao sistema de gerenciamento do chefe com tarefas, projetos e agenda.
Responda sempre em português do Brasil."""


def get_linda_response(user_message: str, context_data: dict = None) -> str:
    """Obtém a resposta da Linda com contexto da situação atual."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        return "⚠️ Chefe, minha chave de IA não está configurada no .env."

    # Injeta contexto atual no sistema
    system_prompt = LINDA_PERSONA
    if context_data:
        system_prompt += f"""

--- CONTEXTO ATUAL ---
Tarefas pendentes hoje: {context_data.get('pending_tasks', 0)}
Tarefas concluídas hoje: {context_data.get('done_tasks', 0)}
Projetos ativos: {context_data.get('active_projects', 0)}
Compromissos hoje: {context_data.get('agenda_count', 0)}
---"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Desculpe chefe, tive uma falha: {str(e)}"


def get_smart_summary() -> str:
    """Linda gera um resumo inteligente do dia."""
    summary = get_summary()

    prompt = f"""O chefe pediu um resumo do dia. Aqui estão os dados:

Tarefas pendentes: {summary['pending_tasks']}
Lista: {[t['title'] for t in summary['tasks'][:5]]}

Projetos ativos: {summary['active_projects']}
Lista: {[p['name'] for p in summary['projects'][:3]]}

Agenda de hoje: {summary['agenda_count']} compromisso(s)
Lista: {[(e['time'], e['event']) for e in summary['agenda']]}

Gere um briefing matinal executivo conciso, como uma secretária que está preparando o chefe para o dia.
Inclua o que é mais urgente, o que tem na agenda e motive brevemente."""

    return get_linda_response(prompt)
