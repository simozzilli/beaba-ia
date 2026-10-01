# Roadmap do Beaba.ia

Atualizado em 01/10/2026, depois da reunião com a Simone.

## Agora: primeira rodada de testes (só gente de dentro)

- Teste em https://beaba.cria.pro, com comentário em cada resposta e painel de etiquetas.
- Meta: umas 200 conversas da equipe e de pessoas próximas do Beaba.
- Admin em https://beaba.cria.pro/admin: conversas, perguntas, etiquetas, avaliações e custo de API.
- Aprovação das reações do urso em https://beaba.cria.pro/reacoes (a Elisa precisa aprovar arte e design).
- Vídeo curto mostrando à equipe como comentar as respostas.

## Em seguida

- **Ajustar as respostas com o que vier dos comentários.** Cada padrão de crítica vira regra no prompt ou verbete novo, e entra no gabarito (`npm run teste`).
- **Conteúdo do Beaba na base.** Texto do Guia Beaba do Câncer e do site de câncer de mama. Hoje a base tem 33 verbetes do Beaba e 54 páginas do INCA.
- **Alimentação e cuidados durante o tratamento.** Verbetes validados pela nutrição (as dúvidas do Alô Nutrição do ICESP são um bom roteiro).
- **Cartões de crise e emergência.** A equipe do Beaba revisa os textos e define quais situações contam.
- **Canal humano.** Definir para onde o chat encaminha quem quer falar com uma pessoa (`BEABA_CANAL_HUMANO`).
- **Segunda rodada: beta aberto** a pacientes e familiares, depois de acertar as respostas da primeira.
- **Publicar em ia.beaba.org** no lugar da versão antiga.
- **Custos.** Pedir os benefícios de ONG (Goodstack) e créditos de API; comparar Opus e Sonnet no admin.

## Depois

- **Outros personagens.** Nutricionista, médico e os demais com a mesma animação, trocando só a aparência. Dar nome a cada um e deixar o Beaba "chamar" o colega certo ("essa é com a nossa nutricionista"). Depende da Elisa aprovar a arte.
- **Animações para outros conteúdos.** Documentar como usar o urso animado em stories e outras peças.
- **Voz.** Conversa falando e ouvindo, inclusive por telefone, para quem não lê e para pessoas cegas. Só depois que a inteligência das respostas estiver acertada.
- **Página inteira ou widget.** Versão para encaixar em outros sites, com o personagem em destaque.
- **Pesquisa e hospitais.** Escrever o trabalho científico sobre comunicação humanizada com IA e desenhar o framework para hospitais (referências citadas: chat do AC Camargo, Alô Nutrição e Alô Enfermagem do ICESP). Se as conversas forem virar pesquisa, o aviso de registro precisa pedir esse consentimento antes do beta aberto.
- **Privacidade no beta aberto.** As etiquetas e a reação do urso passam pelo Jev (TypeSafe). Decidir com o Beaba se isso continua quando o público for de pacientes.

## Fora deste projeto

- Resumo diário das DMs do Instagram do Beaba.
- Refazer o jogo do Beaba (Alphabet Cancer, 2014), se os assets aparecerem.
