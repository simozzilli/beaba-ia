# beaba-ia

Chat do Instituto Beaba sobre câncer: informação de fonte confiável, na linguagem do Beaba, com espaço para apoio emocional.

## Como funciona

1. A pessoa escreve. O front (`index.html`) manda a mensagem, a aba escolhida e o histórico da conversa para `/api/chat`.
2. O modelo consulta a **base de verbetes** antes de afirmar qualquer informação de saúde:
   - `api/_beaba.js`: verbetes escritos pelo Beaba (Guia Beaba do Câncer). **É aqui que se edita conteúdo.**
   - `api/_inca.js`: páginas do INCA para a população. Arquivo gerado: rode `python3 scripts/coletar_inca.py` para atualizar.
3. Se a base não cobre o assunto, ele busca na web, só em INCA, Ministério da Saúde, ASCO, American Cancer Society, Mayo Clinic e Beaba.
4. As fontes que aparecem embaixo da resposta são montadas pelo código (verbetes lidos e páginas citadas), nunca escritas pelo modelo.
5. Em conversa de risco (ideação suicida, urgência médica) aparece um cartão fixo com CVV 188 ou SAMU 192.
6. O urso (`mascote.svg` + `mascote.js`) reage à conversa. Demonstração das 12 reações em `/mascote.html`.

## Configuração (Vercel → Settings → Environment Variables)

| Variável | Obrigatória | Para quê |
|---|---|---|
| `ANTHROPIC_API_KEY` | sim | Chave da API da Anthropic. Trocar aqui quando mudar de conta. |
| `BEABA_MODEL` | não | Modelo. Padrão `claude-opus-5-5`. `claude-sonnet-5-5` responde mais rápido. |
| `BEABA_ESFORCO` | não | `low` (padrão), `medium` ou `high`. |
| `BEABA_CANAL_HUMANO` | não | Texto do canal humano do Beaba, por exemplo `o e-mail hello@beaba.org`. Sem ela, o chat não oferece canal humano. |
| `TYPESAFE_API_KEY` | não | Liga o porteiro (Jev): cartões de crise mais confiáveis e etiquetas no registro. Sem ela, o chat funciona igual. |
| `BEABA_LOGGER_URL` | não | Endereço do Apps Script que grava a planilha de conversas. |

Defina também um limite mensal de gasto na chave da Anthropic: é o teto de custo de verdade.

## Rodar e testar no computador

```bash
npm install
ANTHROPIC_API_KEY=... npm run dev      # http://localhost:3040
ANTHROPIC_API_KEY=... npm run teste    # 13 perguntas de gabarito; gasta centavos de API
```

Rode `npm run teste` antes de publicar qualquer mudança no prompt ou na base.
