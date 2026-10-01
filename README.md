# beaba-ia

Chat do Instituto Beaba sobre câncer: informação de fonte confiável, na linguagem do Beaba, com espaço para apoio emocional.

## Como funciona

1. A pessoa escreve. O front (`index.html`) manda a mensagem e o histórico da conversa para `/api/chat`.
2. O modelo consulta a **base de verbetes** antes de afirmar qualquer informação de saúde:
   - `api/_beaba.js`: verbetes escritos pelo Beaba (Guia Beaba do Câncer). **É aqui que se edita conteúdo.**
   - `api/_inca.js`: páginas do INCA para a população. Arquivo gerado: rode `python3 scripts/coletar_inca.py` para atualizar.
3. Se a base não cobre o assunto, ele busca na web, só em INCA, Ministério da Saúde, ASCO, American Cancer Society, Mayo Clinic e Beaba.
4. As fontes que aparecem embaixo da resposta são montadas pelo código (verbetes lidos e páginas citadas), nunca escritas pelo modelo.
5. Em conversa de risco (ideação suicida, urgência médica) aparece um cartão fixo com CVV 188 ou SAMU 192.
6. O porteiro (`api/_porteiro.js`, Jev) etiqueta cada mensagem (tipo de câncer, tipo de dúvida, quem fala, sentimento) e escolhe a reação do urso.
7. O urso (`mascote.svg` + `mascote.js`) reage à conversa. As 23 reações ficam em `/reacoes`, com aprovação.
8. Cada resposta pode receber 👍, 👎 e comentário. Tudo vai para o banco e aparece em `/admin`, junto com o custo de API.

## Onde roda

- **Teste:** https://beaba.cria.pro, na VPS da Hostinger (`servidor.mjs`, pm2 `beaba`, banco SQLite em `dados/`). Publicar: `scripts/publicar.sh`.
- **Produção antiga:** ia.beaba.org, na Vercel. `api/chat.js` continua compatível com a Vercel, sem banco nem admin.

## Configuração (arquivo `.env` no servidor, ou variáveis de ambiente na Vercel)

| Variável | Obrigatória | Para quê |
|---|---|---|
| `ANTHROPIC_API_KEY` | sim | Chave da API da Anthropic. Trocar aqui quando mudar de conta. |
| `BEABA_MODEL` | não | Modelo. Padrão `claude-opus-5-5`. `claude-sonnet-5-5` responde mais rápido. |
| `BEABA_ESFORCO` | não | `low` (padrão), `medium` ou `high`. |
| `BEABA_CANAL_HUMANO` | não | Texto do canal humano do Beaba, por exemplo `o e-mail hello@beaba.org`. Sem ela, o chat não oferece canal humano. |
| `TYPESAFE_API_KEY` | não | Liga o porteiro (Jev): etiquetas, reação do urso e cartões de crise mais confiáveis. Sem ela, o chat funciona, sem etiquetas. |
| `BEABA_DB` | não | Caminho do banco SQLite, por exemplo `./dados/beaba.db`. Sem ela, não há admin nem comentários. |
| `BEABA_ADMIN_SENHA` | não | Senha do `/admin` (o usuário pode ser qualquer um). |
| `BEABA_MODO_TESTE` | não | `1` mostra o painel de etiquetas no chat. |
| `BEABA_LOGGER_URL` | não | Só sem banco: endereço do Apps Script que grava a planilha de conversas. |

Defina também um limite mensal de gasto na chave da Anthropic: é o teto de custo de verdade.

## Rodar e testar no computador

```bash
npm install
npm start          # lê o .env; abre em http://localhost:3040
npm run teste      # 15 perguntas de gabarito; gasta centavos de API
```

Rode `npm run teste` antes de publicar qualquer mudança no prompt ou na base.

## O urso

`mascote.svg` é a fonte: o desenho e as animações (uma por valor de `data-reacao`) estão dentro dele.
Os scripts em `scripts/mascote/` são os que traçaram o PNG original e montaram o SVG; só são necessários para refazer o traçado.

O que vem pela frente está em `ROADMAP.md`.
