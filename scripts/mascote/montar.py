"""Monta mascote.svg: peças traçadas do original + camadas de expressão (escondidas) + animações por data-reacao."""
import json, sys
P = json.load(open('pecas.json')); M = P['medidas']
BR = '#603813'
def contornada(nome):
    p = P[nome]
    return f'<path class="contorno" d="{p["d"]}" fill="{p["fill"]}" stroke-width="{p["w"] * 2}"/>'
def cheia(nome, extra=''):
    return f'<path d="{P[nome]["d"]}" fill="{BR}"{extra}/>'
def olho(lado):
    cx, cy = M['anel_' + lado][:2]
    s = -1 if lado == 'e' else 1
    return f'''<g class="p-olho p-olho-{lado}">
     <g class="olho-aberto"><g class="pisca"><circle cx="{cx}" cy="{cy}" r="29.35" fill="#fff" stroke="{BR}" stroke-width="4.5"/><circle class="p-pupila" cx="{cx}" cy="{cy}" r="15.3" fill="{BR}"/></g></g>
     <path class="extra olho-feliz" d="M{cx - 21} {cy + 9}Q{cx} {cy - 19} {cx + 21} {cy + 9}"/>
     <path class="extra olho-calmo" d="M{cx - 21} {cy - 4}Q{cx} {cy + 20} {cx + 21} {cy - 4}"/>
     <path class="extra sobrancelha" d="M{cx + s * 20} {cy - 37}L{cx - s * 15} {cy - 45}"/>
     <path class="extra sobrancelha-reta" d="M{cx - 19} {cy - 42}L{cx + 19} {cy - 42}"/>
     <g class="adereco olho-coracao" style="transform-origin:{cx}px {cy}px"><path transform="translate({cx} {cy - 2}) scale(2.7)" d="{CORACAOZINHO}" fill="#eb4247" stroke="{BR}" stroke-width="1.8" stroke-linejoin="round"/></g>
    </g>'''
def bochecha(lado):
    cx, cy, rx, ry = M['bochecha_' + lado]
    return f'<ellipse class="p-bochecha" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#f4afbd"/>'
fx, fy, frx, fry = M['focinho']; mx, my, mr, _ = M['miolo']
CORACAOZINHO = 'M0 -3C-2 -8 -9 -7 -9 -1C-9 4 -3 8 0 10C3 8 9 4 9 -1C9 -7 2 -8 0 -3Z'

CSS = '''
.urso{overflow:visible}
.urso .contorno{stroke:#603813;stroke-linejoin:round;paint-order:stroke}
.urso .extra{fill:none;stroke:#603813;stroke-width:6.2;stroke-linecap:round;stroke-linejoin:round;opacity:0;transition:opacity .18s}
.urso .adereco{opacity:0}
.urso g,.urso path,.urso circle,.urso ellipse{transform-box:view-box}
/* poses: mudam com transição suave quando a reação troca */
.urso .p-urso,.urso .p-cabeca,.urso .p-braco-e,.urso .p-braco-d,.urso .p-orelha-e,.urso .p-orelha-d,.urso .p-pupila,.urso .p-bochecha,.urso .olho-aberto,.urso .p-boca,.urso .p-tronco{transition:transform .45s cubic-bezier(.3,1.4,.5,1),opacity .18s}
.urso .p-urso,.urso .m-urso{transform-origin:250px 546px}
.urso .p-cabeca,.urso .m-cabeca{transform-origin:250px 396px}
.urso .p-tronco,.urso .m-tronco{transform-origin:250px 500px}
.urso .p-braco-e,.urso .m-braco-e{transform-origin:162px 412px}
.urso .p-braco-d,.urso .m-braco-d{transform-origin:338px 412px}
.urso .p-orelha-e,.urso .m-orelha-e{transform-origin:92px 138px}
.urso .p-orelha-d,.urso .m-orelha-d{transform-origin:408px 138px}
.urso .p-coracao{transform-origin:301px 431px}
.urso .p-boca{transform-origin:250px 304px}
.urso .p-olho-e .olho-aberto,.urso .p-olho-e .pisca{transform-origin:161px 273px}
.urso .p-olho-d .olho-aberto,.urso .p-olho-d .pisca{transform-origin:339px 273px}

@keyframes urso-respira{50%{transform:scaleY(1.022)}}
@keyframes urso-cabeca-respira{50%{transform:translateY(-3px)}}
@keyframes urso-pisca{0%,93%,100%{transform:scaleY(1)}96%{transform:scaleY(.06)}}
@keyframes urso-balanca{0%,100%{transform:rotate(-2.2deg)}50%{transform:rotate(2.2deg)}}
@keyframes urso-acena{0%,100%{transform:rotate(-30deg)}50%{transform:rotate(-58deg)}}
@keyframes urso-pulo{0%,100%{transform:translateY(0) scale(1,1)}12%{transform:translateY(0) scale(1.05,.93)}45%{transform:translateY(-34px) scale(.97,1.04)}80%{transform:translateY(0) scale(1.04,.95)}}
@keyframes urso-susto{0%{transform:translateY(0) scale(1,1)}30%{transform:translateY(-18px) scale(.97,1.05)}60%{transform:translateY(0) scale(1.03,.96)}100%{transform:translateY(0) scale(1,1)}}
@keyframes urso-fala{0%,100%{transform:scaleY(1)}50%{transform:scaleY(1.55)}}
@keyframes urso-acena-cabeca{0%,100%{transform:rotate(0)}50%{transform:translateY(2.5px)}}
@keyframes urso-le{0%,100%{transform:translate(-7px,5px)}45%{transform:translate(7px,5px)}55%{transform:translate(7px,7px)}}
@keyframes urso-pensa{0%,100%{transform:translate(6px,-8px)}50%{transform:translate(-4px,-9px)}}
@keyframes urso-coracao{0%,100%{transform:scale(1)}18%{transform:scale(1.22)}36%{transform:scale(1)}54%{transform:scale(1.14)}}
@keyframes urso-coracao-lento{0%,100%{transform:scale(1)}50%{transform:scale(1.16)}}
@keyframes urso-sobe{0%{opacity:0;transform:translate(var(--x),var(--y)) scale(.4)}20%{opacity:1}100%{opacity:0;transform:translate(calc(var(--x) + var(--dx)),calc(var(--y) - 150px)) scale(1.5)}}
@keyframes urso-orelha{0%,100%{transform:rotate(0)}50%{transform:rotate(var(--giro))}}
@keyframes urso-aparece{0%{opacity:0;transform:translate(468px,40px) scale(.3) rotate(-20deg)}60%{opacity:1;transform:translate(468px,22px) scale(1.5) rotate(8deg)}100%{opacity:1;transform:translate(468px,26px) scale(1.35) rotate(0)}}
@keyframes urso-abraco-e{0%,100%{transform:rotate(26deg)}50%{transform:rotate(32deg)}}
@keyframes urso-abraco-d{0%,100%{transform:rotate(-26deg)}50%{transform:rotate(-32deg)}}
@keyframes urso-atencao{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}

/* 1 parado: respira e pisca */
.urso[data-reacao] .m-tronco{animation:urso-respira 3.6s ease-in-out infinite}
.urso[data-reacao] .m-cabeca{animation:urso-cabeca-respira 3.6s ease-in-out infinite}
.urso[data-reacao] .pisca{animation:urso-pisca 4.4s infinite}

/* 2 ouvindo: inclina a cabeça, orelhas de pé, olha para a pessoa */
.urso[data-reacao=ouvindo] .p-cabeca{transform:rotate(-5deg)}
.urso[data-reacao=ouvindo] .p-orelha-e{transform:rotate(-7deg) scale(1.05)}
.urso[data-reacao=ouvindo] .p-orelha-d{transform:rotate(7deg) scale(1.05)}
.urso[data-reacao=ouvindo] .p-pupila{transform:translate(0,5px) }

/* 3 pensando: olha para cima, balança devagar */
.urso[data-reacao=pensando] .m-cabeca{animation:urso-balanca 2.6s ease-in-out infinite}
.urso[data-reacao=pensando] .p-pupila{animation:urso-pensa 2.6s ease-in-out infinite}
.urso[data-reacao=pensando] .p-braco-d{transform:rotate(-24deg)}

/* 4 lendo: os olhos correm a linha, como quem consulta um livro */
.urso[data-reacao=lendo] .p-pupila{animation:urso-le 1.5s ease-in-out infinite}
.urso[data-reacao=lendo] .p-cabeca{transform:rotate(3deg) translateY(3px)}
.urso[data-reacao=lendo] .pisca{animation:none}

/* 5 falando: a boca mexe, a cabeça acompanha */
.urso[data-reacao=falando] .p-boca{animation:urso-fala .34s ease-in-out infinite}
.urso[data-reacao=falando] .m-cabeca{animation:urso-acena-cabeca .68s ease-in-out infinite}
.urso[data-reacao=falando] .p-braco-e{transform:rotate(8deg)}
.urso[data-reacao=falando] .p-braco-d{transform:rotate(-8deg)}

/* 6 acenando: tchauzinho com o braço, olhos sorrindo */
.urso[data-reacao=acenando] .m-braco-d{animation:urso-acena .42s ease-in-out infinite}
.urso[data-reacao=acenando] .p-cabeca{transform:rotate(4deg)}
.urso[data-reacao=acenando] .olho-aberto,.urso[data-reacao=feliz] .olho-aberto,.urso[data-reacao=acolhendo] .olho-aberto,.urso[data-reacao=carinho] .olho-aberto{opacity:0}
.urso[data-reacao=acenando] .olho-feliz,.urso[data-reacao=feliz] .olho-feliz,.urso[data-reacao=carinho] .olho-feliz{opacity:1}

/* 7 feliz: pulinho, braços abertos, bochechas acesas */
.urso[data-reacao=feliz] .m-urso{animation:urso-pulo .7s ease-in-out infinite}
.urso[data-reacao=feliz] .p-braco-e{transform:rotate(42deg)}
.urso[data-reacao=feliz] .p-braco-d{transform:rotate(-42deg)}
.urso[data-reacao=feliz] .p-bochecha,.urso[data-reacao=carinho] .p-bochecha,.urso[data-reacao=acolhendo] .p-bochecha{fill:#f08fa6}

/* 8 acolhendo: olhos calmos, braços abertos, coração devagar */
.urso[data-reacao=acolhendo] .olho-calmo{opacity:1}
.urso[data-reacao=acolhendo] .p-cabeca{transform:rotate(-3deg) translateY(2px)}
.urso[data-reacao=acolhendo] .m-braco-e{animation:urso-abraco-e 4.2s ease-in-out infinite}
.urso[data-reacao=acolhendo] .m-braco-d{animation:urso-abraco-d 4.2s ease-in-out infinite}
.urso[data-reacao=acolhendo] .p-coracao{animation:urso-coracao-lento 2.1s ease-in-out infinite}
.urso[data-reacao=acolhendo] .m-tronco{animation-duration:4.2s}
.urso[data-reacao=acolhendo] .m-cabeca{animation-duration:4.2s}

/* 9 carinho: o coração bate e solta coraçõezinhos */
.urso[data-reacao=carinho] .p-coracao{animation:urso-coracao 1s ease-in-out infinite}
.urso[data-reacao=carinho] .coracaozinho{animation:urso-sobe 1.8s ease-out infinite}
.urso[data-reacao=carinho] .coracaozinho:nth-child(2){animation-delay:.6s}
.urso[data-reacao=carinho] .coracaozinho:nth-child(3){animation-delay:1.2s}
.urso[data-reacao=carinho] .p-cabeca{transform:rotate(4deg)}

/* 10 alerta: atento e sério, sobrancelhas, coração acelerado */
.urso[data-reacao=alerta] .sobrancelha{opacity:1}
.urso[data-reacao=alerta] .olho-aberto{transform:scale(1.07)}
.urso[data-reacao=alerta] .p-orelha-e{transform:rotate(-9deg) scale(1.06)}
.urso[data-reacao=alerta] .p-orelha-d{transform:rotate(9deg) scale(1.06)}
.urso[data-reacao=alerta] .p-coracao{animation:urso-coracao .6s ease-in-out infinite}
.urso[data-reacao=alerta] .m-urso{animation:urso-atencao .6s ease-in-out infinite}
.urso[data-reacao=alerta] .p-braco-e{transform:rotate(14deg)}
.urso[data-reacao=alerta] .p-braco-d{transform:rotate(-14deg)}

/* 11 surpreso: sustinho, boca em "o", olhos arregalados */
.urso[data-reacao=surpreso] .m-urso{animation:urso-susto .5s ease-out 1}
.urso[data-reacao=surpreso] .p-boca{opacity:0}
.urso[data-reacao=surpreso] .boca-o{opacity:1}
.urso[data-reacao=surpreso] .olho-aberto{transform:scale(1.12)}
.urso[data-reacao=surpreso] .p-pupila{transform:scale(.78)}
.urso[data-reacao=surpreso] .p-orelha-e{transform:rotate(-12deg)}
.urso[data-reacao=surpreso] .p-orelha-d{transform:rotate(12deg)}
.urso[data-reacao=surpreso] .p-braco-e{transform:rotate(30deg)}
.urso[data-reacao=surpreso] .p-braco-d{transform:rotate(-30deg)}

/* 12 duvida: cabeça de lado, interrogação, uma orelha cai */
.urso[data-reacao=duvida] .p-cabeca{transform:rotate(9deg)}
.urso[data-reacao=duvida] .p-pupila{transform:translate(6px,-6px)}
.urso[data-reacao=duvida] .interrogacao{animation:urso-aparece .5s cubic-bezier(.3,1.4,.5,1) forwards}
.urso[data-reacao=duvida] .m-orelha-e{--giro:-10deg;animation:urso-orelha 1.6s ease-in-out infinite}
.urso[data-reacao=duvida] .p-braco-e{transform:rotate(18deg)}
.urso[data-reacao=duvida] .p-braco-d{transform:rotate(-18deg)}

@keyframes urso-sim{0%,100%{transform:translateY(0) scaleY(1)}50%{transform:translateY(9px) scaleY(.985)}}
@keyframes urso-nao{0%,100%{transform:rotate(-4.5deg)}50%{transform:rotate(4.5deg)}}
@keyframes urso-inspira{0%,100%{transform:scale(1,1)}45%,55%{transform:scale(1.06,1.1)}}
@keyframes urso-inspira-cabeca{0%,100%{transform:translateY(0)}45%,55%{transform:translateY(-9px)}}
@keyframes urso-inspira-e{0%,100%{transform:rotate(0)}45%,55%{transform:rotate(16deg)}}
@keyframes urso-inspira-d{0%,100%{transform:rotate(0)}45%,55%{transform:rotate(-16deg)}}
@keyframes urso-bate{0%,100%{transform:scale(1)}50%{transform:scale(1.16)}}
@keyframes urso-brilha{0%,100%{opacity:0;transform:translate(var(--x),var(--y)) scale(.4) rotate(0)}50%{opacity:1;transform:translate(var(--x),var(--y)) scale(2.3) rotate(45deg)}}
@keyframes urso-cai{0%{opacity:0;transform:translate(var(--x),-60px) rotate(0)}12%{opacity:1}100%{opacity:0;transform:translate(calc(var(--x) + var(--dx)),330px) rotate(var(--r))}}
@keyframes urso-zzz{0%{opacity:0;transform:translate(430px,90px) scale(.5)}25%{opacity:1}100%{opacity:0;transform:translate(500px,-40px) scale(1.5)}}
@keyframes urso-timido{0%,100%{transform:rotate(-1.2deg)}50%{transform:rotate(1.2deg)}}

/* 13 apaixonado: olhos de coração */
.urso[data-reacao=apaixonado] .olho-aberto,.urso[data-reacao=respirando] .olho-aberto,.urso[data-reacao=comemorando] .olho-aberto,.urso[data-reacao=dormindo] .olho-aberto,.urso[data-reacao=concordando] .olho-aberto{opacity:0}
.urso[data-reacao=apaixonado] .olho-coracao{opacity:1;animation:urso-bate .7s ease-in-out infinite}
.urso[data-reacao=apaixonado] .p-cabeca{transform:rotate(-4deg)}
.urso[data-reacao=apaixonado] .p-bochecha{fill:#f08fa6;transform:scale(1.15)}
.urso[data-reacao=apaixonado] .p-coracao{animation:urso-coracao 1s ease-in-out infinite}
.urso[data-reacao=apaixonado] .p-braco-e{transform:rotate(20deg)}
.urso[data-reacao=apaixonado] .p-braco-d{transform:rotate(-20deg)}

/* 14 piscadinha: fecha um olho só */
.urso[data-reacao=piscadinha] .p-olho-d .olho-aberto{opacity:0}
.urso[data-reacao=piscadinha] .p-olho-d .olho-feliz{opacity:1}
.urso[data-reacao=piscadinha] .p-cabeca{transform:rotate(5deg)}
.urso[data-reacao=piscadinha] .pisca{animation:none}

/* 15 envergonhado: bochechas acesas, olha para baixo, encolhe */
.urso[data-reacao=envergonhado] .p-bochecha{fill:#f08fa6;transform:scale(1.4)}
.urso[data-reacao=envergonhado] .p-pupila{transform:translate(-5px,7px)}
.urso[data-reacao=envergonhado] .p-cabeca{transform:rotate(-4deg) translateY(4px)}
.urso[data-reacao=envergonhado] .p-braco-e{transform:rotate(-12deg)}
.urso[data-reacao=envergonhado] .p-braco-d{transform:rotate(12deg)}
.urso[data-reacao=envergonhado] .m-urso{animation:urso-timido 1.8s ease-in-out infinite}

/* 16 triste: cabeça baixa, orelhas caídas, sente junto */
.urso[data-reacao=triste] .p-cabeca{transform:translateY(8px) rotate(-3deg)}
.urso[data-reacao=triste] .p-orelha-e{transform:rotate(-17deg)}
.urso[data-reacao=triste] .p-orelha-d{transform:rotate(17deg)}
.urso[data-reacao=triste] .p-pupila{transform:translate(0,8px)}
.urso[data-reacao=triste] .sobrancelha{opacity:1}
.urso[data-reacao=triste] .p-boca{opacity:0}
.urso[data-reacao=triste] .boca-triste{opacity:1}
.urso[data-reacao=triste] .m-tronco,.urso[data-reacao=triste] .m-cabeca{animation-duration:5s}
.urso[data-reacao=triste] .p-braco-e{transform:rotate(-8deg)}
.urso[data-reacao=triste] .p-braco-d{transform:rotate(8deg)}

/* 17 concordando: faz que sim */
.urso[data-reacao=concordando] .m-cabeca{animation:urso-sim .55s ease-in-out infinite}
.urso[data-reacao=concordando] .olho-feliz{opacity:1}

/* 18 negando: faz que não, com delicadeza */
.urso[data-reacao=negando] .m-cabeca{animation:urso-nao .5s ease-in-out infinite}
.urso[data-reacao=negando] .p-braco-e{transform:rotate(10deg)}
.urso[data-reacao=negando] .p-braco-d{transform:rotate(-10deg)}

/* 19 respirando: inspira em 4 segundos, solta em 4 ("respira comigo") */
.urso[data-reacao=respirando] .olho-calmo,.urso[data-reacao=dormindo] .olho-calmo{opacity:1}
.urso[data-reacao=respirando] .m-tronco{animation:urso-inspira 8s ease-in-out infinite}
.urso[data-reacao=respirando] .m-cabeca{animation:urso-inspira-cabeca 8s ease-in-out infinite}
.urso[data-reacao=respirando] .m-braco-e{animation:urso-inspira-e 8s ease-in-out infinite}
.urso[data-reacao=respirando] .m-braco-d{animation:urso-inspira-d 8s ease-in-out infinite}

/* 20 comemorando: pula com confete */
.urso[data-reacao=comemorando] .m-urso{animation:urso-pulo .62s ease-in-out infinite}
.urso[data-reacao=comemorando] .olho-feliz{opacity:1}
.urso[data-reacao=comemorando] .p-braco-e{transform:rotate(48deg)}
.urso[data-reacao=comemorando] .p-braco-d{transform:rotate(-48deg)}
.urso[data-reacao=comemorando] .confete rect{animation:urso-cai 1.7s linear infinite}
.urso[data-reacao=comemorando] .p-bochecha{fill:#f08fa6}

/* 21 ideia: olha para cima, brilhos */
.urso[data-reacao=ideia] .brilho{animation:urso-brilha 1.1s ease-in-out infinite}
.urso[data-reacao=ideia] .brilho:nth-child(2){animation-delay:.35s}
.urso[data-reacao=ideia] .brilho:nth-child(3){animation-delay:.7s}
.urso[data-reacao=ideia] .p-pupila{transform:translate(0,-8px)}
.urso[data-reacao=ideia] .olho-aberto{transform:scale(1.08)}
.urso[data-reacao=ideia] .p-orelha-e{transform:rotate(-8deg) scale(1.06)}
.urso[data-reacao=ideia] .p-orelha-d{transform:rotate(8deg) scale(1.06)}
.urso[data-reacao=ideia] .m-urso{animation:urso-susto .5s ease-out 1}
.urso[data-reacao=ideia] .p-braco-d{transform:rotate(-44deg)}

/* 22 dormindo: quando a conversa fica parada muito tempo */
.urso[data-reacao=dormindo] .p-cabeca{transform:rotate(6deg) translateY(5px)}
.urso[data-reacao=dormindo] .p-orelha-e{transform:rotate(-8deg)}
.urso[data-reacao=dormindo] .p-orelha-d{transform:rotate(8deg)}
.urso[data-reacao=dormindo] .m-tronco,.urso[data-reacao=dormindo] .m-cabeca{animation-duration:5.4s}
.urso[data-reacao=dormindo] .zzz path{animation:urso-zzz 3s ease-out infinite}
.urso[data-reacao=dormindo] .zzz path:nth-child(2){animation-delay:1s}
.urso[data-reacao=dormindo] .zzz path:nth-child(3){animation-delay:2s}

/* 23 firme: sério e presente, para orientar com clareza */
.urso[data-reacao=firme] .sobrancelha-reta{opacity:1}
.urso[data-reacao=firme] .p-braco-e{transform:rotate(12deg)}
.urso[data-reacao=firme] .p-braco-d{transform:rotate(-12deg)}
.urso[data-reacao=firme] .m-cabeca{animation:urso-sim 1.6s ease-in-out infinite}
.urso[data-reacao=firme] .pisca{animation-duration:6s}

.urso .p-pupila{transform-box:fill-box;transform-origin:center;transform:translate(var(--olhar-x,0px),var(--olhar-y,0px))}
.urso .p-bochecha{transform-box:fill-box;transform-origin:center}
@media (prefers-reduced-motion:reduce){.urso *{animation:none!important;transition:none!important}}
'''

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 558" class="urso" role="img" aria-label="Urso do Beaba">
<style>{CSS}</style>
<defs>
 <clipPath id="urso-recorte-nariz"><rect x="220" y="280" width="60" height="24.4"/></clipPath>
 <clipPath id="urso-recorte-boca"><rect x="220" y="304" width="60" height="20"/></clipPath>
</defs>
<g class="p-urso"><g class="m-urso">
 <g class="p-perna-e">{contornada('perna-e')}</g>
 <g class="p-perna-d">{contornada('perna-d')}</g>
 <g class="p-braco-e"><g class="m-braco-e">{contornada('braco-e')}</g></g>
 <g class="p-braco-d"><g class="m-braco-d">{contornada('braco-d')}</g></g>
 <g class="p-tronco"><g class="m-tronco">
  {contornada('corpo')}
  <g class="p-costura-corpo">{cheia('pontos-corpo')}</g>
  <g class="p-coracao">
   {contornada('coracao')}
   <circle cx="{mx}" cy="{my}" r="{mr + 2.25}" fill="#f8c311" stroke="{BR}" stroke-width="4.5"/>
  </g>
  <g class="p-cateter" fill="none" stroke="{BR}" stroke-linecap="round" stroke-linejoin="round">
   <path d="M302 432.6C310 430.4 316 428.6 322 428.1C330 427.6 338 429.3 344 434C350.5 439.5 355.5 448 360 458" stroke-width="6.2"/>
   <path d="M360.6 459.6L365.1 474.2" stroke-width="8.2"/>
  </g>
 </g></g>
 <g class="p-cabeca"><g class="m-cabeca">
  <g class="p-orelha-e"><g class="m-orelha-e">{contornada('orelha-e')}{cheia('arco-orelha-e')}</g></g>
  <g class="p-orelha-d"><g class="m-orelha-d">{contornada('orelha-d')}{cheia('arco-orelha-d')}</g></g>
  <g class="p-capuz">{contornada('capuz')}<g class="p-costura-capuz">{cheia('pontos-capuz')}</g></g>
  <g class="p-rosto">
   {contornada('rosto')}
   {bochecha('e')}{bochecha('d')}
   <g class="p-focinho"><ellipse cx="{fx}" cy="{fy}" rx="{frx}" ry="{fry}" fill="#e2f3fa"/>
    <g class="p-nariz" clip-path="url(#urso-recorte-nariz)">{cheia('nariz-boca')}</g>
    <g class="p-boca"><g clip-path="url(#urso-recorte-boca)">{cheia('nariz-boca')}</g></g>
    <path class="extra boca-triste" d="M240.5 314Q250 306.5 259.5 314" style="stroke-width:4.6"/>
    <ellipse class="boca-o adereco" cx="250" cy="312" rx="5.8" ry="6.8" fill="{BR}" style="transition:opacity .15s"/>
   </g>
   {olho('e')}{olho('d')}
  </g>
  <g class="interrogacao adereco" fill="none" stroke="{BR}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><path d="M-9 -13C-9 -24 9 -24 9 -13C9 -5 0 -5 0 4"/><circle cx="0" cy="15" r="1.2"/></g>
 </g></g>
 <g class="confete"><rect x="-11" y="-7" width="22" height="14" rx="3" fill="#32c0c5" stroke="{BR}" stroke-width="2.4" class="adereco" style="--x:40px;--dx:26px;--r:220deg;animation-delay:0.00s"/><rect x="-6" y="-4" width="12" height="8" rx="2" fill="#f8c311" stroke="{BR}" stroke-width="1.6" class="adereco" style="--x:87px;--dx:-26px;--r:440deg;animation-delay:0.37s"/><rect x="-6" y="-4" width="12" height="8" rx="2" fill="#f4afbd" stroke="{BR}" stroke-width="1.6" class="adereco" style="--x:134px;--dx:26px;--r:660deg;animation-delay:0.74s"/><rect x="-6" y="-4" width="12" height="8" rx="2" fill="#eb4247" stroke="{BR}" stroke-width="1.6" class="adereco" style="--x:181px;--dx:-26px;--r:220deg;animation-delay:1.11s"/><rect x="-6" y="-4" width="12" height="8" rx="2" fill="#32c0c5" stroke="{BR}" stroke-width="1.6" class="adereco" style="--x:228px;--dx:26px;--r:440deg;animation-delay:1.48s"/><rect x="-6" y="-4" width="12" height="8" rx="2" fill="#f8c311" stroke="{BR}" stroke-width="1.6" class="adereco" style="--x:275px;--dx:-26px;--r:660deg;animation-delay:0.15s"/><rect x="-6" y="-4" width="12" height="8" rx="2" fill="#f4afbd" stroke="{BR}" stroke-width="1.6" class="adereco" style="--x:322px;--dx:26px;--r:220deg;animation-delay:0.52s"/><rect x="-6" y="-4" width="12" height="8" rx="2" fill="#eb4247" stroke="{BR}" stroke-width="1.6" class="adereco" style="--x:369px;--dx:-26px;--r:440deg;animation-delay:0.89s"/><rect x="-6" y="-4" width="12" height="8" rx="2" fill="#32c0c5" stroke="{BR}" stroke-width="1.6" class="adereco" style="--x:416px;--dx:26px;--r:660deg;animation-delay:1.26s"/><rect x="-6" y="-4" width="12" height="8" rx="2" fill="#f8c311" stroke="{BR}" stroke-width="1.6" class="adereco" style="--x:463px;--dx:-26px;--r:220deg;animation-delay:1.63s"/></g>
 <g class="brilhos">
  <path class="brilho adereco" style="--x:36px;--y:36px" d="M0 -15C2 -4 4 -2 15 0C4 2 2 4 0 15C-2 4 -4 2 -15 0C-4 -2 -2 -4 0 -15Z" fill="#f8c311" stroke="{BR}" stroke-width="2.6" stroke-linejoin="round"/>
  <path class="brilho adereco" style="--x:470px;--y:26px" d="M0 -15C2 -4 4 -2 15 0C4 2 2 4 0 15C-2 4 -4 2 -15 0C-4 -2 -2 -4 0 -15Z" fill="#f8c311" stroke="{BR}" stroke-width="2.6" stroke-linejoin="round"/>
  <path class="brilho adereco" style="--x:250px;--y:-14px" d="M0 -15C2 -4 4 -2 15 0C4 2 2 4 0 15C-2 4 -4 2 -15 0C-4 -2 -2 -4 0 -15Z" fill="#f8c311" stroke="{BR}" stroke-width="2.6" stroke-linejoin="round"/>
 </g>
 <g class="zzz" fill="none" stroke="{BR}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
  <path class="adereco" d="M-10 -10H10L-10 10H10"/><path class="adereco" d="M-10 -10H10L-10 10H10"/><path class="adereco" d="M-10 -10H10L-10 10H10"/>
 </g>
 <g class="coracoezinhos">
  <path class="coracaozinho adereco" style="--x:372px;--y:404px;--dx:40px" d="{CORACAOZINHO}" fill="#eb4247" stroke="{BR}" stroke-width="2.4" stroke-linejoin="round"/>
  <path class="coracaozinho adereco" style="--x:128px;--y:404px;--dx:-40px" d="{CORACAOZINHO}" fill="#eb4247" stroke="{BR}" stroke-width="2.4" stroke-linejoin="round"/>
  <path class="coracaozinho adereco" style="--x:392px;--y:380px;--dx:70px" d="{CORACAOZINHO}" fill="#eb4247" stroke="{BR}" stroke-width="2.4" stroke-linejoin="round"/>
 </g>
</g></g>
</svg>
'''
dest = sys.argv[1] if len(sys.argv) > 1 else 'mascote.svg'
open(dest, 'w').write(svg); print(len(svg), 'bytes ->', dest)
