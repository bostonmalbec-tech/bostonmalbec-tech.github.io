(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Miniaturas: si la de alta calidad no existe, usa la normal; si tampoco, la oculta
  window.__thumbErr = function (img) {
    var fb = img.getAttribute('data-fallback');
    if (fb && img.src !== fb) { img.removeAttribute('data-fallback'); img.classList.add('lb'); img.src = fb; return; }
    img.style.visibility = 'hidden';
  };

  // YouTube responde con una imagen gris de 120 px cuando no existe la miniatura grande
  window.__thumbLoad = function (img) { if (img.naturalWidth && img.naturalWidth <= 120) window.__thumbErr(img); };
  document.querySelectorAll('img[data-fallback]').forEach(function (img) { if (img.complete) window.__thumbLoad(img); });

  // Aparición al bajar
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -5% 0px' });
    reveals.forEach(function (el, i) { el.style.transitionDelay = Math.min(i % 8, 6) * 60 + 'ms'; io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('in'); });
  }

  // Filtros de trabajos
  var buttons = document.querySelectorAll('[data-filter]');
  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      var f = b.getAttribute('data-filter');
      buttons.forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
      document.querySelectorAll('.tile').forEach(function (t) {
        var show = (' ' + t.getAttribute('data-cats') + ' ').indexOf(' ' + f + ' ') > -1;
        t.classList.toggle('hide', !show);
        t.classList.remove('pop');
        if (show) { void t.offsetWidth; t.classList.add('pop', 'in'); }
      });
    });
  });

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

  // Formulario de contacto: abre WhatsApp con el mensaje armado
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var note = document.getElementById('form-note');
      var name = form.nombre.value.trim(), reach = form.contacto.value.trim(), msg = form.detalles.value.trim();
      if (!name || !msg) { note.textContent = 'Escribe tu nombre y los detalles del proyecto.'; (name ? form.detalles : form.nombre).focus(); return; }
      var text = 'Hola Boston, soy ' + name + (reach ? ' (' + reach + ')' : '') + '.\n\n' + msg;
      var url = 'https://wa.me/' + form.getAttribute('data-wa') + '?text=' + encodeURIComponent(text);
      window.open(url, '_blank', 'noopener');
      note.textContent = 'Se abrió WhatsApp con tu mensaje. Si no se abrió, escríbeme directo.';
    });
  }

  // Inicio: profundidad que sigue al mouse
  var scene = document.querySelector('.scene');
  if (!scene || reduce) return;
  var layers = [].slice.call(scene.querySelectorAll('[data-depth]'));
  var target = { x: 0, y: 0 }, cur = { x: 0, y: 0 };
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (fine) {
    window.addEventListener('pointermove', function (e) {
      target.x = (e.clientX / window.innerWidth) * 2 - 1;
      target.y = (e.clientY / window.innerHeight) * 2 - 1;
    }, { passive: true });
    document.addEventListener('pointerleave', function () { target.x = 0; target.y = 0; });
  }
  var t0 = performance.now();
  (function loop(now) {
    if (!fine) {
      var t = (now - t0) / 1000;
      target.x = Math.sin(t / 2.6) * 0.55; target.y = Math.cos(t / 3.3) * 0.35;
    }
    cur.x += (target.x - cur.x) * 0.07;
    cur.y += (target.y - cur.y) * 0.07;
    layers.forEach(function (el) {
      var d = parseFloat(el.getAttribute('data-depth')) || 0;
      el.style.translate = (-cur.x * d * 46).toFixed(2) + 'px ' + (-cur.y * d * 26).toFixed(2) + 'px';
    });
    scene.style.setProperty('--tilt', (cur.x * 10).toFixed(2) + 'deg');
    requestAnimationFrame(loop);
  })(t0);
})();
