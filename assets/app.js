(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Miniaturas: si la de alta calidad no existe, usa la normal (recortando sus franjas negras)
  window.__thumbErr = function (img) {
    var fb = img.getAttribute('data-fallback');
    if (fb && img.src !== fb) { img.removeAttribute('data-fallback'); img.classList.add('lb'); img.src = fb; return; }
    img.style.visibility = 'hidden';
  };
  // YouTube responde con una imagen gris de 120 px cuando no existe la miniatura grande
  window.__thumbLoad = function (img) { if (img.naturalWidth && img.naturalWidth <= 120) window.__thumbErr(img); };
  document.querySelectorAll('img[data-fallback]').forEach(function (img) { if (img.complete) window.__thumbLoad(img); });

  // Aparición al bajar (también dibuja los recuadros de selección)
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { threshold: 0.15, rootMargin: '0px 0px -6% 0px' });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('in'); });
  }

  // La tele de la portada pasa tus videos como si fuera un canal
  var screen = document.querySelector('.tv-screen');
  if (screen && !reduce) {
    var slides = [].slice.call(screen.querySelectorAll('.slide'));
    var k = 0;
    if (slides.length > 1) {
      setInterval(function () {
        slides[k].classList.remove('on');
        k = (k + 1) % slides.length;
        slides[k].classList.add('on');
        screen.classList.remove('glitch'); void screen.offsetWidth; screen.classList.add('glitch');
      }, 2400);
    }
  }

  // "Gracias por ver" se escribe solo al llegar
  var tw = document.querySelector('.typewrite');
  if (tw && !reduce && 'IntersectionObserver' in window) {
    var span = tw.querySelector('.tw-text');
    var text = tw.getAttribute('data-text');
    span.textContent = '';
    tw.setAttribute('aria-label', text);
    var tio = new IntersectionObserver(function (entries) {
      if (!entries[0].isIntersecting) return;
      tio.disconnect();
      var i = 0;
      (function type() {
        span.textContent = text.slice(0, ++i);
        if (i < text.length) setTimeout(type, 90 + Math.random() * 70);
      })();
    }, { threshold: 0.6 });
    tio.observe(tw);
  }

  // Reproductor de video al tocar
  document.querySelectorAll('.frame[data-yt], .frame[data-ig]').forEach(function (fr) {
    var play = function () {
      var f = document.createElement('iframe');
      f.src = fr.dataset.yt
        ? 'https://www.youtube-nocookie.com/embed/' + fr.dataset.yt + '?autoplay=1&rel=0'
        : 'https://www.instagram.com/reel/' + fr.dataset.ig + '/embed/';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      f.title = fr.getAttribute('aria-label') || 'Video';
      fr.innerHTML = ''; fr.appendChild(f);
      fr.removeAttribute('role'); fr.removeAttribute('tabindex'); fr.style.cursor = 'auto';
    };
    fr.addEventListener('click', play, { once: true });
    fr.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); play(); } });
  });

  // Portada: la tele y el título se mueven un poco con el mouse
  var cover = document.querySelector('.cover');
  if (cover && !reduce && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    var tv = cover.querySelector('.tv-body'), mega = cover.querySelector('.mega span');
    cover.addEventListener('pointermove', function (e) {
      var x = e.clientX / window.innerWidth - .5, y = e.clientY / window.innerHeight - .5;
      tv.style.transform = 'rotateY(' + (x * 10).toFixed(2) + 'deg) rotateX(' + (-y * 8).toFixed(2) + 'deg)';
      mega.style.translate = (x * -24).toFixed(1) + 'px ' + (y * -10).toFixed(1) + 'px';
    });
    cover.style.perspective = '1200px';
  }
})();
