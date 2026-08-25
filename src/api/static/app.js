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
