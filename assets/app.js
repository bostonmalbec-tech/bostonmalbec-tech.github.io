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

  // Inicio: anillo 3D de miniaturas alrededor de la pieza central
  var scene = document.getElementById('scene');
  if (!scene) return;
  var items = [].slice.call(scene.querySelectorAll('.ring-item'));
  var n = items.length;
  if (!n) return;
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var rot = 0, vel = reduce ? 0 : 0.12;          // giro automático (radianes por segundo)
  var mouse = { x: 0, y: 0 }, cur = { x: 0, y: 0 };
  var hovering = false, drag = null, t0 = performance.now(), last = t0;
  items.forEach(function (it) {
    it.addEventListener('mouseenter', function () { hovering = true; });
    it.addEventListener('mouseleave', function () { hovering = false; });
  });
  if (fine) {
    window.addEventListener('pointermove', function (e) {
      mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.y = (e.clientY / window.innerHeight) * 2 - 1;
    }, { passive: true });
  }
  // Arrastrar con el dedo o el mouse hace girar el anillo
  scene.addEventListener('pointerdown', function (e) { drag = { x: e.clientX, rot: rot, moved: false }; });
  window.addEventListener('pointermove', function (e) {
    if (!drag) return;
    var dx = e.clientX - drag.x;
    if (Math.abs(dx) > 6) drag.moved = true;
    rot = drag.rot + dx / (scene.clientWidth * 0.35);
  }, { passive: true });
  window.addEventListener('pointerup', function () { setTimeout(function () { drag = null; }, 0); });
  scene.addEventListener('click', function (e) { if (drag && drag.moved) { e.preventDefault(); } }, true);

  function frame(now) {
    var dt = Math.min(0.05, (now - last) / 1000); last = now;
    if (!drag && !hovering) rot += vel * dt;
    cur.x += (mouse.x - cur.x) * 0.06;
    cur.y += (mouse.y - cur.y) * 0.06;
    var w = scene.clientWidth, h = scene.clientHeight;
    var rx = w < 700 ? w * 0.47 : Math.min(w * 0.4, 600);   // radio horizontal del anillo
    var lift = Math.min(h * 0.06, 42);                        // las de atrás quedan un poco más arriba
    var tilt = cur.y * 0.6;                       // inclinación con el mouse
    items.forEach(function (it, i) {
      var a = rot + cur.x * 0.45 + (i / n) * Math.PI * 2;
      var d = Math.cos(a);                        // 1 = al frente, -1 = atrás
      var x = Math.sin(a) * rx;
      var y = -(1 - d) * lift * (1 + tilt) + cur.y * 26 * d + (w < 700 ? h * 0.1 : 0);
      var sc = 0.32 + 0.31 * (1 + d);
      var intro = reduce ? 1 : Math.max(0, Math.min(1, (now - t0 - 150 - i * 70) / 700));
      var ease = 1 - Math.pow(1 - intro, 3);
      it.style.transform = 'translate(-50%, -50%) translate3d(' + (x * ease).toFixed(1) + 'px,' + (y * ease).toFixed(1) + 'px,0) scale(' + (sc * (0.4 + 0.6 * ease)).toFixed(3) + ')';
      it.style.zIndex = d > 0.2 ? 60 + Math.round(d * 20) : 10 + Math.round((d + 1) * 10);
      it.style.opacity = (ease * (0.55 + 0.45 * (d + 1) / 2)).toFixed(3);
      it.style.filter = d < -0.2 ? 'blur(' + ((-d - 0.2) * 2).toFixed(1) + 'px)' : 'none';
    });
    if (!reduce || now - t0 < 100) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
