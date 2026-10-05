document.getElementById('burger')?.addEventListener('click', () => document.body.classList.toggle('menu-hidden'));
const all = document.getElementById('check-all');
all?.addEventListener('change', () => document.querySelectorAll('.row-check').forEach(c => { c.checked = all.checked; c.closest('tr').classList.toggle('selected', c.checked); }));
document.querySelectorAll('.row-check').forEach(c => c.addEventListener('change', () => c.closest('tr').classList.toggle('selected', c.checked)));
