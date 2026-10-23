// Minimal lightbox for links with class "docent-lightbox". Esc, click or tap closes it.
document.addEventListener("click", function (e) {
  var link = e.target.closest && e.target.closest("a.docent-lightbox");
  if (!link || e.ctrlKey || e.metaKey) return;
  e.preventDefault();
  var box = document.createElement("div");
  box.className = "docent-lb";
  var img = document.createElement("img");
  img.src = link.href;
  img.alt = link.dataset.caption || "";
  box.appendChild(img);
  if (link.dataset.caption) {
    var p = document.createElement("p");
    p.textContent = link.dataset.caption;
    box.appendChild(p);
  }
  function close() { box.remove(); document.removeEventListener("keydown", onKey); }
  function onKey(ev) { if (ev.key === "Escape") close(); }
  box.addEventListener("click", close);
  document.addEventListener("keydown", onKey);
  document.body.appendChild(box);
});
