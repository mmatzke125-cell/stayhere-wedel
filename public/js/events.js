(function () {
  var buttons = document.querySelectorAll('.filter button');
  var events = document.querySelectorAll('.event');
  buttons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var kind = btn.getAttribute('data-filter');
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
      events.forEach(function (ev) {
        ev.hidden = kind !== 'alle' && ev.getAttribute('data-kind') !== kind;
      });
    });
  });
})();
