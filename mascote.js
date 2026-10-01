// Urso do Beaba animado por código.
//
//   const urso = await Mascote.criar(document.querySelector('#urso'));
//   urso.reagir('feliz');         // reações curtas voltam sozinhas para "parado"
//   urso.reagir('pensando');      // as outras ficam até a próxima chamada
//   urso.reagir('acolhendo', 8000); // ou por um tempo escolhido, em milissegundos
//
// O desenho e todas as animações moram em mascote.svg; a reação é só o atributo data-reacao do <svg>.
(function () {
  const REACOES = ['parado', 'ouvindo', 'pensando', 'lendo', 'falando', 'acenando', 'feliz', 'acolhendo', 'carinho', 'alerta', 'surpreso', 'duvida'];
  const VOLTA_SOZINHA = { acenando: 2300, feliz: 2100, carinho: 3600, surpreso: 1600, duvida: 3200 };

  async function criar(elemento, arquivo) {
    const resposta = await fetch(arquivo || 'mascote.svg');
    elemento.innerHTML = await resposta.text();
    const svg = elemento.querySelector('svg');
    let relogio;
    function reagir(nome, ms) {
      if (!REACOES.includes(nome)) nome = 'parado';
      clearTimeout(relogio);
      svg.dataset.reacao = nome;
      const tempo = ms === undefined ? VOLTA_SOZINHA[nome] : ms;
      if (tempo) relogio = setTimeout(function () { svg.dataset.reacao = 'parado'; }, tempo);
    }
    reagir('parado');
    return { reagir: reagir, svg: svg, reacoes: REACOES };
  }

  window.Mascote = { criar: criar, reacoes: REACOES };
})();
