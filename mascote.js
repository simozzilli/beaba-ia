// Urso do Beaba animado por código.
//
//   const urso = await Mascote.criar(document.querySelector('#urso'));
//   urso.reagir('feliz');           // reações curtas voltam sozinhas para "parado"
//   urso.reagir('pensando');        // as outras ficam até a próxima chamada
//   urso.reagir('acolhendo', 8000); // ou por um tempo escolhido, em milissegundos
//   urso.seguirPonteiro();          // os olhos acompanham o mouse ou o dedo
//
// O desenho e todas as animações moram em mascote.svg; a reação é só o atributo data-reacao do <svg>.
(function () {
  const REACOES = ['parado', 'ouvindo', 'pensando', 'lendo', 'falando', 'acenando', 'feliz', 'acolhendo', 'carinho', 'alerta',
    'surpreso', 'duvida', 'apaixonado', 'piscadinha', 'envergonhado', 'triste', 'concordando', 'negando', 'respirando',
    'comemorando', 'ideia', 'dormindo', 'firme'];
  const VOLTA_SOZINHA = { acenando: 2300, feliz: 2100, carinho: 3600, surpreso: 1600, duvida: 3200, apaixonado: 3600,
    piscadinha: 1500, envergonhado: 3200, concordando: 1700, negando: 1600, comemorando: 3400, ideia: 2400 };

  let svgEmCache;
  async function criar(elemento, arquivo) {
    svgEmCache = svgEmCache || fetch(arquivo || 'mascote.svg').then(function (r) { return r.text(); });
    elemento.innerHTML = await svgEmCache;
    const svg = elemento.querySelector('svg');
    let relogio;
    function reagir(nome, ms) {
      if (!REACOES.includes(nome)) nome = 'parado';
      clearTimeout(relogio);
      svg.dataset.reacao = nome;
      const tempo = ms === undefined ? VOLTA_SOZINHA[nome] : ms;
      if (tempo) relogio = setTimeout(function () { svg.dataset.reacao = 'parado'; }, tempo);
    }
    function olhar(x, y) { // x e y de -1 a 1
      svg.style.setProperty('--olhar-x', (Math.max(-1, Math.min(1, x)) * 9).toFixed(1) + 'px');
      svg.style.setProperty('--olhar-y', (Math.max(-1, Math.min(1, y)) * 8).toFixed(1) + 'px');
    }
    function seguirPonteiro() {
      window.addEventListener('pointermove', function (e) {
        const c = svg.getBoundingClientRect();
        olhar((e.clientX - (c.left + c.width / 2)) / 260, (e.clientY - (c.top + c.height * 0.48)) / 260);
      }, { passive: true });
    }
    reagir('parado');
    return { reagir: reagir, olhar: olhar, seguirPonteiro: seguirPonteiro, svg: svg, reacoes: REACOES };
  }

  window.Mascote = { criar: criar, reacoes: REACOES };
})();
