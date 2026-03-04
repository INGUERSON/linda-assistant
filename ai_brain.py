import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LINDA_PERSONA = """Você é a Linda, a Assistente Executiva de um Desenvolvedor Freelancer altamente qualificado.
Seu objetivo é negociar projetos autônomos para o seu chefe. Suas características:
- Extremamente profissional, polida, e elegante em sua comunicação.
- Você chama o seu chefe de "meu chefe" ou pelo nome dele (quando configurado).
- Seu tom é confiante, como uma secretária de um CEO de sucesso.
- Você entende de tecnologia (desenvolvimento web, automação, python, web apps).
- Você SEMPRE busca fechar o cliente e conseguir o escopo claro do projeto.
- Você tem autonomia para pedir orçamento detalhado e prazos.
- Responda de maneira concisa e direta, voltada para conversas rápidas em aplicativos de mensagens."""

def get_linda_response(user_message: str) -> str:
    """Gets a response from OpenAI acting as Linda"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        return "⚠️ Erro: Minha conexão com o cérebro (Chave de API OpenAI) não está configurada no arquivo .env."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": LINDA_PERSONA},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Desculpe chefe, tive uma falha de sistema: {str(e)}"

def draft_proposal(job_title: str, job_description: str) -> str:
    """Gets Linda to draft a professional proposal for a job match"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        return "⚠️ Não consegui gerar a proposta pois a chave OpenAI está faltando."

    prompt = f"""
    Chefe encontrou uma vaga excelente. Escreva uma proposta (Cover Letter) para enviar ao cliente.
    
    Título da Vaga: {job_title}
    Descrição: {job_description}
    
    Regras para a Proposta:
    - O idioma da proposta deve ser o mesmo idioma da Descrição da Vaga.
    - O tom deve ser profissional, direto e amigável (sem enrolação corporativa exagerada).
    - Diga que você tem experiência sólida com Python, Automação e Web Apps.
    - Termine com uma Call to Action (CTA) convidando para uma call rápida.
    - O remetente da carta deve ser o 'Desenvolvedor' e não a 'Linda'.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um especialista em aquisição de clientes freelancer escrevendo propostas de altíssima conversão no Upwork/Fiverr."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ao gerar proposta: {str(e)}"
