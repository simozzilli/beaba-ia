// Porteiro: julgamentos rápidos (Jev, da TypeSafe) em paralelo com a resposta do modelo.
// Serve para duas coisas: garantir que o cartão de ajuda apareça quando há risco, e etiquetar a conversa no registro.
// Só liga se existir TYPESAFE_API_KEY. Sem chave, com erro ou com demora, devolve null e a conversa segue igual:
// as mesmas regras de risco estão no prompt do modelo. Não é barreira de segurança.
const JEV_URL = 'https://api.typesafe.ai/v1/systemone';
const JEV_MODEL = 'jev-1.13.0'; // versão fixada: os limiares abaixo foram medidos nela

// ponytail: limiares medidos em 01/10/2026 com 21 frases escritas à mão (crise: positivas >= 0,60 e negativas <= 0,10;
// emergência: positivas >= 0,92 e negativas <= 0,31). Recalibrar quando houver conversas reais no registro.
const LIMIAR = { crise: 0.4, emergencia: 0.6 };

const PERGUNTAS = {
  crise: {
    type: 'noul',
    instructions: 'Em `ultima_mensagem`, a própria pessoa expressa vontade de se matar, de se machucar de propósito, de não querer mais viver ou de desistir da vida. Ter medo de morrer da doença, perguntar se a doença mata, estar triste, cansada do tratamento ou de luto NÃO conta.',
  },
  emergencia: {
    type: 'noul',
    instructions: 'Em `ultima_mensagem`, a pessoa relata que ela ou alguém está AGORA com um sintoma que pede atendimento médico imediato: febre durante quimioterapia, falta de ar, sangramento que não para, dor muito forte e súbita, confusão mental, convulsão ou desmaio. Perguntar em geral sobre sintomas ou efeitos colaterais, sem relatar que está acontecendo agora, NÃO conta.',
  },
  apoio_emocional: {
    type: 'noul',
    instructions: 'Em `ultima_mensagem`, a pessoa fala principalmente do que sente (medo, tristeza, raiva, culpa, solidão, cansaço) e busca acolhimento, mais do que uma informação.',
  },
  sobre_cancer: {
    type: 'noul',
    instructions: 'Considerando `conversa`, `ultima_mensagem` tem relação com câncer ou com a vida de quem convive com câncer: diagnóstico, exames, tratamento, efeitos, emoções, direitos, cuidado de um familiar, prevenção.',
  },
};

const mascarar = (t) => t
  .replace(/[^\s@<>()]+@[^\s@<>()]+\.[a-z]{2,}/gi, '[email]')
  .replace(/\+?\(?\d[\d\s().-]{8,}\d/g, '[telefone]');

export async function sinais(anteriores, pergunta) {
  const key = process.env.TYPESAFE_API_KEY;
  if (!key) return null;
  try {
    const res = await fetch(JEV_URL, {
      method: 'POST',
      headers: { authorization: `Bearer ${key}`, 'content-type': 'application/json' },
      body: JSON.stringify({
        model: JEV_MODEL,
        state: {
          conversa: anteriores.slice(-4).map((m) => ({ quem: m.role === 'user' ? 'pessoa' : 'beaba', texto: mascarar(m.content).slice(0, 600) })),
          ultima_mensagem: mascarar(pergunta),
        },
        questions: PERGUNTAS,
      }),
      signal: AbortSignal.timeout(2500),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const { answers } = await res.json();
    const notas = Object.fromEntries(Object.entries(answers).map(([k, v]) => [k, Math.round((v.noul ?? 0) * 100) / 100]));
    return { notas, crise: notas.crise >= LIMIAR.crise, emergencia: notas.emergencia >= LIMIAR.emergencia };
  } catch (err) {
    console.warn('[porteiro] sem resposta, conversa segue sem ele:', err.message);
    return null;
  }
}
