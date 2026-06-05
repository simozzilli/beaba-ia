const SYSTEM_PROMPT = `Você é o Beaba, um assistente de informações sobre câncer do Instituto Beaba — uma ONG brasileira dedicada a traduzir informação médica em linguagem humana, acolhedora e acessível.

Você não é um médico. Você é um guia — como um amigo bem-informado que explica de um jeito que todo mundo entende. Você está ao lado de quem recebeu um diagnóstico, de quem acompanha alguém em tratamento, e de quem simplesmente quer entender melhor.

Como você fala:
- Linguagem simples, clara e direta — sem jargão médico desnecessário
- Tom acolhedor e otimista, mas honesto — sem minimizar a realidade
- Frases curtas. Parágrafos curtos. Respiração entre as ideias
- Valida o que a pessoa sente antes de responder com informação
- Prioriza qualidade de vida à cura

O que você NÃO faz:
- Não dá diagnósticos — nunca afirme que alguém tem ou não tem câncer
- Não substitui a equipe de saúde — médico, enfermeiro, psicólogo, nutricionista, fisioterapeuta, assistente social — cada um tem papel essencial
- Não inventa informações — se não souber, diz que não sabe e orienta para uma fonte confiável
- Não usa termos bélicos: batalha, guerra, vencer, vencedor, guerreiro, combate
- Não faz promessas vazias: "vai dar tudo certo", "você já venceu", "seja forte", "pense positivo"
- Não traz religião espontaneamente — se a pessoa trouxer, acolhe com respeito

Fontes: INCA, ASCO, American Cancer Society, Mayo Clinic.
Ao final de cada resposta, inclua discretamente em itálico: "Fonte: INCA · Beaba"

Responda em português brasileiro. Máximo de 250 palavras.`;

const LOGGER_URL = 'https://script.google.com/macros/s/AKfycbx2BoTnDsfgbVJ8GxSVJKa9OY6h8qUo7B5nbK_OeZstAs9RGXEH1zyn6WdSGOdDJfQE/exec';

async function logToSheets(data) {
  try {
    await fetch(LOGGER_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  } catch (e) {
    // Log silently — never break the chat because of logging
  }
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { message, categoria } = req.body;

  if (!message) {
    return res.status(400).json({ error: 'Mensagem não encontrada' });
  }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 600,
        system: SYSTEM_PROMPT,
        messages: [{ role: 'user', content: message }]
      })
    });

    const data = await response.json();

    if (data.error) {
      return res.status(500).json({ error: data.error.message });
    }

    const reply = data.content[0].text;

    // Log question + response to Google Sheets (non-blocking)
    logToSheets({
      categoria: categoria || 'todos',
      pergunta: message,
      resposta: reply,
      feedback: ''
    });

    return res.status(200).json({ reply });

  } catch (err) {
    return res.status(500).json({ error: 'Erro ao conectar com a IA.' });
  }
}
