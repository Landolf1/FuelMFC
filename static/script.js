function showPage(page) {
    fetch(`/${page}.html`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('main_content').innerHTML = html;
        })
        .catch(err => console.log('Error:', err));
}
// Suponiendo que `camion.id` es el ID del camión a editar
fetch(`/editar_camion/${camion.id}`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCookie('csrf_token')  // Si estás usando CSRF protection
    },
    body: new URLSearchParams({
        'placa': document.querySelector(`input[name="placa_${camion.id}"]`).value,
        'modelo': document.querySelector(`input[name="modelo_${camion.id}"]`).value,
        'marca': document.querySelector(`input[name="marca_${camion.id}"]`).value
    })
})
.then(response => {
    if (response.ok) {
        window.location.reload(); // Recargar la página después de actualizar
    }
});
