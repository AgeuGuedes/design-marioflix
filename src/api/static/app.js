document.addEventListener("DOMContentLoaded", () => {
  initHeroCarousel();
  initRowCarousels();
});

function initHeroCarousel() {
  const slides = document.querySelectorAll(".hero-slide");
  const dots = document.querySelectorAll(".hero-dot");
  const prev = document.querySelector(".hero-arrow-left");
  const next = document.querySelector(".hero-arrow-right");
  if (!slides.length) return;

  let index = 0;
  let timer = null;

  function show(i) {
    index = (i + slides.length) % slides.length;
    slides.forEach((slide, n) => slide.classList.toggle("active", n === index));
    dots.forEach((dot, n) => dot.classList.toggle("active", n === index));
  }

  function restartAutoplay() {
    if (timer) clearInterval(timer);
    timer = setInterval(() => show(index + 1), 6000);
  }

  dots.forEach((dot) => {
    dot.addEventListener("click", () => {
      show(parseInt(dot.dataset.index, 10));
      restartAutoplay();
    });
  });

  if (prev) prev.addEventListener("click", () => { show(index - 1); restartAutoplay(); });
  if (next) next.addEventListener("click", () => { show(index + 1); restartAutoplay(); });

  restartAutoplay();
}

function initRowCarousels() {
  document.querySelectorAll(".row-track-wrap").forEach((wrap) => {
    const track = wrap.querySelector(".row-track");
    const left = wrap.querySelector(".row-arrow-left");
    const right = wrap.querySelector(".row-arrow-right");
    if (!track) return;

    const scrollAmount = () => track.clientWidth * 0.8;
    if (left) left.addEventListener("click", () => track.scrollBy({ left: -scrollAmount(), behavior: "smooth" }));
    if (right) right.addEventListener("click", () => track.scrollBy({ left: scrollAmount(), behavior: "smooth" }));

    function updateArrows() {
      const canScroll = track.scrollWidth > track.clientWidth + 1;
      const atStart = track.scrollLeft <= 0;
      const atEnd = track.scrollLeft + track.clientWidth >= track.scrollWidth - 1;

      if (left) left.style.display = canScroll && !atStart ? "flex" : "none";
      if (right) right.style.display = canScroll && !atEnd ? "flex" : "none";
    }

    track.addEventListener("scroll", updateArrows);
    window.addEventListener("resize", updateArrows);
    updateArrows();
  });
}

document.addEventListener("DOMContentLoaded", initAvaliacao);

function initAvaliacao() {
  const form = document.querySelector(".avaliar");
  if (!form) return;

  const caixa = form.querySelector(".estrelas");
  const estrelas = Array.from(caixa.querySelectorAll(".estrela"));
  const rotulo = form.querySelector(".avaliar-rotulo");
  const padrao = rotulo.dataset.padrao;

  function mostrarRotulo(texto) {
    rotulo.classList.add("trocando");
    setTimeout(() => {
      rotulo.textContent = texto;
      rotulo.classList.remove("trocando");
    }, 90);
  }

  // Ao passar o mouse, as estrelas de 1 até a escolhida acendem em onda.
  function previa(estrela) {
    const nota = Number(estrela.dataset.nota);
    caixa.classList.add("em-previa");
    estrelas.forEach((outra) => outra.classList.toggle("previa", Number(outra.dataset.nota) <= nota));
    mostrarRotulo(`${nota} de 5 · ${estrela.dataset.rotulo}`);
  }

  function limparPrevia() {
    caixa.classList.remove("em-previa");
    estrelas.forEach((outra) => outra.classList.remove("previa"));
    mostrarRotulo(padrao);
  }

  estrelas.forEach((estrela) => {
    estrela.addEventListener("mouseenter", () => previa(estrela));
    estrela.addEventListener("focus", () => previa(estrela));
    estrela.addEventListener("blur", limparPrevia);

    // No clique, acende da 1 até a nota escolhida e só depois envia, pra animação aparecer.
    estrela.addEventListener("click", (evento) => {
      evento.preventDefault();
      if (form.classList.contains("enviando")) return;

      const nota = Number(estrela.dataset.nota);
      estrela.blur();
      caixa.classList.remove("em-previa");
      estrelas.forEach((outra) => {
        outra.classList.remove("previa");
        outra.classList.toggle("acesa", Number(outra.dataset.nota) <= nota);
      });
      mostrarRotulo(`${nota} de 5 · ${estrela.dataset.rotulo}`);

      form.classList.remove("avaliado");
      void form.offsetWidth;  // reinicia a animação
      form.classList.add("enviando");

      let campo = form.querySelector('input[type="hidden"][name="nota"]');
      if (!campo) {
        campo = document.createElement("input");
        campo.type = "hidden";
        campo.name = "nota";
        form.appendChild(campo);
      }
      campo.value = nota;
      setTimeout(() => form.submit(), nota * 110 + 700);
    });
  });

  caixa.addEventListener("mouseleave", limparPrevia);
}
