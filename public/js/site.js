(function () {
  var menus = Array.prototype.slice.call(document.querySelectorAll('details.menu'));
  menus.forEach(function (m) {
    m.addEventListener('toggle', function () {
      if (m.open) { menus.forEach(function (o) { if (o !== m) { o.open = false; } }); }
    });
  });
  document.addEventListener('click', function (e) {
    menus.forEach(function (m) { if (m.open && !m.contains(e.target)) { m.open = false; } });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') { return; }
    menus.forEach(function (m) { if (m.open) { m.open = false; m.querySelector('summary').focus(); } });
  });
  // Die Google-Karte wird erst geladen, wenn jemand darauf klickt.
  Array.prototype.forEach.call(document.querySelectorAll('[data-gmap]'), function (b) {
    b.addEventListener('click', function () {
      var fig = b.closest('.map');
      var svg = fig.querySelector('.mapsvg');
      var f = document.createElement('iframe');
      f.src = b.getAttribute('data-gmap');
      f.title = 'Google-Karte von Wedel';
      f.loading = 'lazy';
      f.setAttribute('referrerpolicy', 'no-referrer');
      if (svg) { fig.replaceChild(f, svg); }
      b.parentNode.parentNode.removeChild(b.parentNode);
    });
  });
  // Springt ein Link auf einen zugeklappten Bereich, wird er geöffnet.
  function openTarget() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id) { return; }
    var el = document.getElementById(id);
    var first = el;
    while (el) { if (el.tagName === 'DETAILS') { el.open = true; } el = el.parentElement; }
    if (first && first.scrollIntoView) { first.scrollIntoView(); }
  }
  window.addEventListener('hashchange', openTarget);
  openTarget();
})();
