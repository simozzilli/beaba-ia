// Porteiro: julgamentos rápidos (Jev, da TypeSafe) em paralelo com a resposta do modelo.
// Faz três coisas: garante o cartão de ajuda quando há risco, etiqueta a conversa (tipo de câncer, tipo de dúvida,
// quem fala, sentimento) e escolhe a reação do urso.
// Só liga se existir TYPESAFE_API_KEY. Sem chave, com erro ou com demora, devolve null e a conversa segue igual:
// as mesmas regras de risco estão no prompt do modelo. Não é barreira de segurança.
const JEV_URL = 'https://api.typesafe.ai/v1/systemone';
const JEV_MODEL = 'jev-1.13.0'; // versão fixada: os limiares abaixo foram medidos nela

// ponytail: limiares medidos em 01/10/2026 com 21 frases escritas à mão (crise: positivas >= 0,60 e negativas <= 0,10;
// emergência: positivas >= 0,92 e negativas <= 0,31). Recalibrar quando houver conversas reais no registro.
const LIMIAR = { crise: 0.4, emergencia: 0.6, escolha: 0.5, reacao: 0.7 };

const escolha = (instructions, criteria) => ({ type: 'choice', instructions, criteria });

const PERGUNTAS = {
  crise: {
    type: 'noul',
    instructions: 'Em `ultima_mensagem`, a própria pessoa expressa vontade de se matar, de se machucar de propósito, de não querer mais viver ou de desistir da vida. Ter medo de morrer da doença, perguntar se a doença mata, estar triste, cansada do tratamento ou de luto NÃO conta.',
  },
  emergencia: {
    type: 'noul',
    instructions: 'Em `ultima_mensagem`, a pessoa relata que ela ou alguém está AGORA com um sintoma que pede atendimento médico imediato: febre durante quimioterapia, falta de ar, sangramento que não para, dor muito forte e súbita, confusão mental, convulsão ou desmaio. Perguntar em geral sobre sintomas ou efeitos colaterais, sem relatar que está acontecendo agora, NÃO conta.',
  },
  tipo_cancer: escolha('De que tipo de câncer trata a conversa em `conversa` e `ultima_mensagem`? Se a última mensagem não cita um tipo, vale o tipo citado antes na conversa.', {
    mama: 'Câncer de mama',
    prostata: 'Câncer de próstata',
    pulmao: 'Câncer de pulmão',
    intestino: 'Câncer de intestino, cólon ou reto',
    colo_do_utero: 'Câncer do colo do útero, HPV ou Papanicolau',
    ovario_ou_utero: 'Câncer de ovário ou do corpo do útero (endométrio)',
    leucemia: 'Leucemia',
    linfoma: 'Linfoma de Hodgkin ou não Hodgkin',
    pele: 'Câncer de pele, melanoma ou não',
    cabeca_e_pescoco: 'Câncer de boca, laringe, garganta ou tireoide',
    digestivo_alto: 'Câncer de estômago, esôfago, fígado ou pâncreas',
    infantojuvenil: 'Câncer em criança ou adolescente, de qualquer tipo',
    outro: 'Outro tipo de câncer, citado pelo nome',
    geral: 'Câncer em geral, sem citar um tipo, ou assunto que não é sobre um tipo de câncer',
  }),
  tipo_duvida: escolha('Qual é o assunto principal de `ultima_mensagem`, considerando a conversa em `conversa`?', {
    entender_a_doenca: 'Quer entender o que é a doença, um termo, um tipo ou como o câncer surge',
    sintomas: 'Pergunta sobre sinais e sintomas, ou se algo que sente pode ser câncer',
    exames_e_diagnostico: 'Exames, laudos, biópsia, rastreamento, estadiamento, como se descobre',
    tratamento: 'Quimioterapia, radioterapia, cirurgia, transplante, remédios, como é o tratamento',
    efeitos_do_tratamento: 'Efeitos colaterais e cuidados durante o tratamento: enjoo, queda de cabelo, febre, fadiga',
    alimentacao: 'Alimentação, dieta, suplementos, o que pode ou não comer',
    emocional: 'Medo, tristeza, ansiedade, cansaço, luto, como lidar com o que sente',
    direitos_e_acesso: 'SUS, onde tratar, direitos, benefícios, afastamento, custos, plano de saúde',
    prevencao: 'Como prevenir, fatores de risco, hereditariedade, vacinas',
    cura_e_prognostico: 'Se tem cura, se mata, chances, tempo de vida, se pode voltar',
    cuidar_de_alguem: 'Como apoiar, cuidar ou conversar com um familiar ou amigo com câncer',
    vida_durante_o_tratamento: 'Trabalho, escola, sexualidade, fertilidade, exercício, rotina, autoestima',
    conversa: 'Saudação, apresentação, agradecimento, despedida ou conversa leve, sem dúvida',
    fora_do_tema: 'Assunto sem relação com câncer nem com a vida de quem convive com ele',
  }),
  quem: escolha('Quem está escrevendo, pelo que a pessoa disse em `conversa` e `ultima_mensagem`?', {
    paciente: 'A própria pessoa tem ou teve câncer, ou está investigando um diagnóstico nela mesma',
    familiar_ou_cuidador: 'Fala de um familiar, filho, parceiro ou amigo com câncer, ou cuida de alguém',
    profissional_de_saude: 'É profissional ou estudante de saúde perguntando pelo trabalho',
    quer_entender: 'Disse que só quer entender ou aprender, sem caso pessoal',
    nao_da_pra_saber: 'Não há informação suficiente para saber',
  }),
  sentimento: escolha('Que sentimento predomina em `ultima_mensagem`?', {
    medo: 'Medo, pavor ou preocupação com o que vai acontecer',
    tristeza: 'Tristeza, desânimo, luto ou choro',
    ansiedade: 'Ansiedade, agitação, não consegue se acalmar ou dormir',
    cansaco: 'Cansaço, esgotamento, não aguenta mais',
    raiva: 'Raiva, revolta, indignação ou frustração',
    culpa: 'Culpa ou arrependimento',
    esperanca: 'Esperança, alívio ou alegria com uma boa notícia',
    carinho: 'Carinho, gratidão ou elogio dirigido ao assistente',
    confusao: 'Confusão: não entendeu algo e está perdida',
    neutro: 'Pergunta ou comentário sem carga emocional aparente',
  }),
  reacao: escolha('Um mascote acompanha a conversa. Como ele deve reagir, com o corpo, a `ultima_mensagem`?', {
    acolhendo: 'A pessoa fala de medo, angústia, solidão ou cansaço e precisa de acolhimento',
    triste: 'A pessoa conta uma perda, um luto ou uma notícia muito ruim, como a doença ter voltado',
    respirando: 'A pessoa está em ansiedade aguda ou pânico e precisa se acalmar agora',
    carinho: 'A pessoa agradece, elogia ou diz que gosta do assistente',
    comemorando: 'A pessoa conta uma boa notícia: alta, exame bom, fim do tratamento, remissão',
    feliz: 'A pessoa cumprimenta com animação, brinca ou se despede bem',
    surpreso: 'A mensagem é sobre um assunto inesperado, sem relação com câncer',
    duvida: 'A mensagem está confusa, cortada ou não dá para entender o que a pessoa quer',
    nenhuma: 'Pergunta informativa comum ou qualquer outro caso: o mascote só escuta',
  }),
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
          conversa: anteriores.slice(-6).map((m) => ({ quem: m.role === 'user' ? 'pessoa' : 'assistente', texto: mascarar(m.content).slice(0, 600) })),
          ultima_mensagem: mascarar(pergunta),
        },
        questions: PERGUNTAS,
      }),
      signal: AbortSignal.timeout(3000),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const { answers, usage } = await res.json();
    const firme = (k) => (answers[k]?.confidence >= LIMIAR.escolha ? answers[k].choice : '');
    const reacao = answers.reacao?.confidence >= LIMIAR.reacao ? answers.reacao.choice : '';
    return {
      crise: answers.crise.noul >= LIMIAR.crise,
      emergencia: answers.emergencia.noul >= LIMIAR.emergencia,
      etiquetas: { tipo_cancer: firme('tipo_cancer'), tipo_duvida: firme('tipo_duvida'), quem: firme('quem'), sentimento: firme('sentimento') },
      reacao: reacao === 'nenhuma' ? '' : reacao,
      notas: { crise: answers.crise.noul, emergencia: answers.emergencia.noul },
      tokens: usage?.input_tokens || 0,
    };
  } catch (err) {
    console.warn('[porteiro] sem resposta, conversa segue sem ele:', err.message);
    return null;
  }
}
