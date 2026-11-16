document.querySelectorAll('.more-toggle').forEach((button) => {
  const panel = document.getElementById(button.getAttribute('aria-controls'));
  if (!panel) return;

  panel.hidden = true;
  button.hidden = false;
  button.addEventListener('click', () => {
    const expanded = panel.hidden;
    panel.hidden = !expanded;
    button.setAttribute('aria-expanded', String(expanded));
    button.textContent = expanded ? '− 보충' : '+ 보충';
  });
});
