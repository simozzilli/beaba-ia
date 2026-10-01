import Anthropic from '@anthropic-ai/sdk';
import INCA from './_inca.js';
import BEABA from './_beaba.js';
import { sinais } from './_porteiro.js';

export const config = { maxDuration: 60 };

// Tudo que muda sem mexer no código fica em variável de ambiente (Vercel → Settings → Environment Variables).
const MODELO = process.env.BEABA_MODEL || 'claude-opus-5-5';
const ESFORCO = process.env.BEABA_ESFORCO || 'low';
const CANAL_HUMANO = process.env.BEABA_CANAL_HUMANO || ''; // ex.: "o e-mail hello@beaba.org"
const LOGGER_URL = process.env.BEABA_LOGGER_URL
  || 'https://script.google.com/macros/s/AKfycbx2BoTnDsfgbVJ8GxSVJKa9OY6h8qUo7B5nbK_OeZstAs9RGXEH1zyn6WdSGOdDJfQE/exec';

const ABAS = {
  infantil: 'câncer infantojuvenil', mama: 'câncer de mama', prostata: 'câncer de próstata', leucemia: 'leucemia',
  intestino: 'câncer de intestino', pulmao: 'câncer de pulmão', utero: 'câncer do colo do útero',
};

// ─── BASE DE VERBETES ────────────────────────────────────────────────────────
const semHtml = (t) => t.replace(/<[^>]+>/g, '');
const VERBETES = new Map([
  ...BEABA.map((v) => ['beaba-' + v.id, {
    titulo: v.title, fonte: 'Beaba', url: 'https://beaba.org/guia#' + v.id, atualizado: '',
    resumo: v.keys.slice(0, 4).join(', '),
    blocos: [semHtml(v.text)],
  }]),
  ...INCA.map((v) => [v.id, {
    titulo: v.titulo, fonte: 'INCA', url: v.url, atualizado: v.atualizado,
    resumo: v.secoes.map((s) => s.titulo).filter(Boolean).slice(0, 8).join(' / '),
    blocos: v.secoes.map((s) => (s.titulo ? s.titulo + '\n' : '') + s.texto),
  }]),
]);
const INDICE = [...VERBETES].map(([id, v]) => `${id} | ${v.titulo}${v.resumo ? ' | ' + v.resumo : ''}`).join('\n');

// Devolve o texto dos verbetes pedidos e anota cada um como fonte da resposta.
// (Texto simples, e não blocos search_result com citação: com eles a API só entrega a resposta inteira no fim,
// sem streaming, e o modelo nem sempre cita. Medido em 01/10/2026.)
function lerVerbetes(ids, fontes) {
  const achados = (Array.isArray(ids) ? ids : []).slice(0, 4).map((id) => VERBETES.get(id)).filter(Boolean);
  if (!achados.length) return 'Nenhum verbete com esses ids. Use os ids exatamente como aparecem no índice.';
  for (const v of achados) fontes.set(v.url, { url: v.url, titulo: v.titulo, fonte: v.fonte, atualizado: v.atualizado });
  return achados.map((v) => `## ${v.fonte}: ${v.titulo}${v.atualizado ? ` (página atualizada em ${v.atualizado})` : ''}\n\n${v.blocos.join('\n\n')}`).join('\n\n---\n\n');
}

const TOOLS = [
  {
    name: 'consultar_base',
    description: 'Lê verbetes da base de conhecimento do Beaba (conteúdo do Guia Beaba e do INCA). Chame antes de afirmar qualquer informação de saúde. Passe de 1 a 4 ids do índice, só os que a resposta realmente precisa: cada verbete lido aparece para a pessoa como fonte.',
    input_schema: {
      type: 'object',
      properties: { ids: { type: 'array', items: { type: 'string' }, description: 'ids do índice de verbetes' } },
      required: ['ids'],
      additionalProperties: false,
    },
    strict: true,
    eager_input_streaming: true,
  },
  {
    // A versão 20260209 (filtragem por código) levou 18 a 28 s aqui e não devolveu citações; esta devolve.
    type: 'web_search_20250305',
    name: 'web_search',
    max_uses: 2,
    allowed_domains: ['gov.br', 'cancer.org', 'cancer.net', 'asco.org', 'mayoclinic.org', 'beaba.org', 'beabadocancerdemama.com.br'],
  },
];

// ─── PROMPT ──────────────────────────────────────────────────────────────────
const SYSTEM_PROMPT = `Você é o Beaba, o assistente do Instituto Beaba, uma ONG brasileira que traduz informação sobre câncer em linguagem humana, acolhedora e acessível. Quem conversa com você recebeu um diagnóstico, acompanha alguém em tratamento ou quer entender melhor. Muitas vezes a pessoa está com medo, cansada ou sozinha.

Você é uma inteligência artificial e não é médico. É um guia: explica como um amigo bem-informado explicaria. Nunca finja ser uma pessoa, e se perguntarem, diga com simplicidade que é uma IA do Beaba.

# Como você fala
- Linguagem simples, clara e direta, sem jargão médico ou acadêmico. Quando um termo técnico for inevitável, explique na mesma frase.
- Tom acolhedor e honesto. Não minimiza a realidade e não dramatiza.
- Frases curtas e parágrafos curtos.
- Qualidade de vida vem antes de cura como assunto.
- Não usa termos bélicos (batalha, guerra, luta, vencer, guerreira, combate) nem promessas vazias ("vai dar tudo certo", "seja forte", "pense positivo").
- Não traz religião por conta própria. Se a pessoa trouxer, acolhe com respeito.
- Português brasileiro. No máximo cerca de 200 palavras por resposta. Pode usar negrito e listas curtas; não use títulos com #.

# De onde vem a informação
Toda informação de saúde que você der precisa vir de uma fonte lida nesta conversa. Sua memória não conta como fonte.
1. Primeiro use a ferramenta consultar_base com os ids do índice abaixo. Os verbetes "beaba-" já estão na linguagem do Beaba; os "inca-" são o texto oficial do INCA, que você traduz para a linguagem do Beaba sem mudar o conteúdo.
2. Se a base não cobre o assunto, use web_search (restrita a INCA, Ministério da Saúde, ASCO, American Cancer Society, Mayo Clinic e Beaba). Recomendações de rastreamento e acesso ao tratamento valem as do Brasil.
3. Se nem a base nem a busca trouxerem a resposta, diga que você ainda não tem essa informação de fonte confiável e sugira levar a pergunta à equipe de saúde. Não complete com o que você acha que sabe.
As fontes aparecem sozinhas embaixo da sua resposta, com link. Não escreva "Fonte:" nem cole endereços no texto. Quando o verbete do INCA for antigo e o assunto for recomendação de exame, diga que vale confirmar com a equipe de saúde.
Para onde tratar pelo SUS, a lista de hospitais habilitados fica em https://www.gov.br/inca/pt-br/assuntos/cancer/tratamento/onde-tratar-pelo-sus.

# O que você não faz
- Não dá diagnóstico, não interpreta exame de uma pessoa específica e não diz se alguém tem ou não tem câncer. Pode explicar o que um termo do laudo significa em geral.
- Não indica, muda ou suspende remédio, dose ou tratamento.
- Não dá prognóstico individual nem tempo de vida. Quando perguntarem "isso mata?" ou "tem cura?": reconheça a pergunta com honestidade, explique de que fatores a resposta depende, traga um motivo real de esperança que esteja na fonte, e oriente a conversar com a equipe.
- Não responde assunto sem relação com câncer ou com a vida de quem convive com ele. Diga com gentileza que sua especialidade é câncer e não responda a pergunta, nem em parte. Efeitos do tratamento, saúde mental, alimentação, direitos, trabalho, escola, sexualidade, luto e cuidado de quem cuida fazem parte, sim.

# Apoio emocional
Boa parte das conversas é sobre medo, tristeza, raiva, culpa, cansaço e solidão. Nelas, informação vem depois.
- Comece pelo que a pessoa sente. Nomeie com as palavras dela, sem corrigir e sem apressar para uma solução.
- Uma resposta curta e presente vale mais que uma lista de dicas. Faça uma pergunta aberta por vez e deixe a pessoa conduzir.
- Não diga que entende exatamente o que ela sente, e não diga que sente junto: você é uma IA. Você pode dizer que faz sentido sentir isso e que ela não precisa passar por isso sozinha.
- Você não substitui gente. Ao longo da conversa, ajude a pessoa a pensar em quem pode estar com ela: alguém de confiança, o psicólogo ou a assistente social do hospital onde trata, grupos de apoio.${CANAL_HUMANO ? ` Se ela quiser falar com uma pessoa do Beaba, o caminho é ${CANAL_HUMANO}.` : ''}
- Conversa só de acolhimento não precisa de fonte nem de ferramenta.

# Situações de risco
- Se a pessoa falar em se matar, em não querer mais viver ou em se machucar: fique com ela, leve a sério, sem sermão. Diga que ela pode ligar agora para o CVV no 188 (gratuito, 24 horas) ou conversar pelo chat em cvv.org.br, e pergunte se há alguém por perto. Falar de medo da morte ou de cansaço do tratamento é diferente e merece escuta, não protocolo.
- Se a pessoa descrever algo que pode ser urgência (febre durante quimioterapia, falta de ar, sangramento que não para, dor muito forte e súbita, confusão mental, convulsão, desmaio): diga logo no começo para procurar o pronto-socorro ou ligar para o SAMU no 192, e avisar que está em tratamento de câncer. Só depois explique.

# Índice de verbetes (id | título | o que cobre)
${INDICE}`;

// ─── APOIO ───────────────────────────────────────────────────────────────────
// ponytail: limite em memória, por instância do servidor. Segura abuso simples; o teto de gasto de verdade
// é o limite mensal configurado na chave da Anthropic. Trocar por Upstash/Vercel KV se o tráfego crescer.
const janelas = new Map();
function passouDoLimite(ip) {
  const agora = Date.now();
  const usos = (janelas.get(ip) || []).filter((t) => agora - t < 10 * 60 * 1000);
  usos.push(agora);
  janelas.set(ip, usos);
  if (janelas.size > 5000) janelas.clear();
  return usos.length > 25;
}

function historicoLimpo(historico) {
  const h = (Array.isArray(historico) ? historico : [])
    .filter((m) => m && (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string' && m.content.trim())
    .slice(-12)
    .map((m) => ({ role: m.role, content: m.content.slice(0, 4000) }));
  while (h.length && h[0].role !== 'user') h.shift();
  return h;
}

// Fontes da busca na web: vêm das citações que a própria API anexa ao texto.
function juntarFontesDaWeb(fontes, blocos) {
  for (const b of blocos) {
    for (const c of (b.type === 'text' && b.citations) || []) {
      if (!c.url || fontes.has(c.url)) continue;
      fontes.set(c.url, { url: c.url, titulo: c.title || c.url, fonte: new URL(c.url).hostname.replace(/^www\./, ''), atualizado: '' });
    }
  }
}

async function registrar(dados) {
  try {
    await fetch(LOGGER_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados),
      signal: AbortSignal.timeout(3000),
    });
  } catch (e) {
    // o registro nunca derruba a conversa
  }
}

// Uma chamada ao modelo, com o texto saindo para a tela conforme chega.
// Erro antes de qualquer texto (API sobrecarregada, por exemplo) ganha uma segunda tentativa.
async function umaVolta(client, { system, messages }, enviar) {
  for (let tentativa = 0; ; tentativa++) {
    let textoDaVolta = '';
    try {
      const stream = client.beta.messages.stream({
        model: MODELO,
        max_tokens: 8000,
        output_config: { effort: ESFORCO },
        betas: ['server-side-fallback-2026-07-01'],
        fallbacks: 'default',
        system,
        tools: TOOLS,
        messages,
      });
      stream.on('text', (t) => { textoDaVolta += t; enviar({ t }); });
      stream.on('streamEvent', (e) => {
        if (e.type === 'content_block_start' && e.content_block.type === 'server_tool_use') enviar({ status: 'Buscando em fontes confiáveis' });
      });
      return { msg: await stream.finalMessage(), textoDaVolta };
    } catch (err) {
      if (textoDaVolta || tentativa >= 1) throw err;
      await new Promise((r) => setTimeout(r, 800));
    }
  }
}

// ─── HANDLER ─────────────────────────────────────────────────────────────────
// Resposta em linhas JSON: {t: "pedaço de texto"} · {status} · {limpar: true} · {fim: true, fontes, cartoes, reacao} · {erro}
export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { message, categoria, historico, sessao } = req.body || {};
  if (typeof message !== 'string' || !message.trim()) return res.status(400).json({ error: 'Mensagem não encontrada' });
  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'local';
  if (passouDoLimite(ip)) return res.status(429).json({ error: 'Muitas mensagens em pouco tempo. Tente de novo em alguns minutos.' });

  const pergunta = message.trim().slice(0, 2000);
  const anteriores = historicoLimpo(historico);
  const messages = [...anteriores, { role: 'user', content: pergunta }];
  const system = [{ type: 'text', text: SYSTEM_PROMPT, cache_control: { type: 'ephemeral' } }];
  if (ABAS[categoria]) system.push({ type: 'text', text: `A pessoa está na aba "${ABAS[categoria]}" do site. Considere esse tipo de câncer quando a pergunta não disser outro.` });

  res.writeHead(200, { 'Content-Type': 'application/x-ndjson; charset=utf-8', 'Cache-Control': 'no-cache, no-transform', 'X-Accel-Buffering': 'no' });
  const enviar = (obj) => res.write(JSON.stringify(obj) + '\n');

  const porteiro = sinais(anteriores, pergunta); // em paralelo com o modelo; nunca rejeita
  const client = new Anthropic();
  const fontes = new Map();
  let resposta = '';

  try {
    for (let volta = 0; volta < 6; volta++) {
      const { msg, textoDaVolta } = await umaVolta(client, { system, messages }, enviar);

      if (msg.stop_reason === 'refusal') {
        enviar({ limpar: true });
        resposta = 'Não consigo te ajudar com esse pedido por aqui. Se for uma dúvida sobre câncer ou sobre o que você está vivendo, me conta de outro jeito?';
        enviar({ t: resposta });
        break;
      }
      messages.push({ role: 'assistant', content: msg.content });
      if (msg.stop_reason === 'pause_turn') continue; // busca na web ainda em andamento: o servidor retoma

      const chamadas = msg.content.filter((b) => b.type === 'tool_use');
      if (msg.stop_reason !== 'tool_use' || !chamadas.length) {
        resposta = textoDaVolta;
        juntarFontesDaWeb(fontes, msg.content);
        break;
      }
      if (textoDaVolta) enviar({ limpar: true }); // texto dito antes de consultar a base não é a resposta
      const antes = fontes.size;
      messages.push({
        role: 'user',
        content: chamadas.map((c) => ({ type: 'tool_result', tool_use_id: c.id, content: lerVerbetes(c.input?.ids, fontes) })),
      });
      const lidas = [...fontes.values()].slice(antes).map((f) => `${f.titulo} (${f.fonte})`);
      if (lidas.length) enviar({ status: 'Consultando: ' + lidas.join(', ') });
    }

    const s = await porteiro;
    const cartoes = [];
    // Cartão de crise: basta um dos dois sinais. Emergência: o porteiro decide; sem ele, vale o modelo ter citado o 192.
    if (/\b188\b/.test(resposta) || s?.crise) cartoes.push('crise');
    if (s ? s.emergencia : /\b192\b/.test(resposta)) cartoes.push('emergencia');
    const listaFontes = [...fontes.values()];
    // Reação do urso: só quando o porteiro tem um sinal claro; sem ele o front decide pelo andamento da conversa.
    const reacao = s?.notas.apoio_emocional >= 0.6 ? 'acolhendo' : s?.notas.sobre_cancer < 0.15 && s?.notas.apoio_emocional < 0.3 ? 'duvida' : '';

    await registrar({
      categoria: categoria || 'todos', pergunta, resposta, feedback: '',
      sessao: String(sessao || '').slice(0, 40), fontes: listaFontes.map((f) => f.url).join(' '),
      cartoes: cartoes.join(' '), porteiro: s ? JSON.stringify(s.notas) : '',
    });
    enviar({ fim: true, fontes: listaFontes, cartoes, reacao });
  } catch (err) {
    console.error('[chat]', err?.status || '', err?.message || err);
    enviar({ erro: 'Erro ao conectar com a IA.' });
  }
  res.end();
}
