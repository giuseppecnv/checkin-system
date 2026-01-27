window.addEventListener('DOMContentLoaded', function() {

    const tokenInput = document.querySelector('.token-field');

    const toggles = document.querySelectorAll('.toggle-password');

    toggles.forEach(btn => {
        btn.addEventListener('click', function() {
            // 1. Cambia il tipo di input
            const isPassword = tokenInput.type === 'password';
            tokenInput.type = isPassword ? 'text' : 'password';

            // 2. Cambia la visibilità delle icone switchando la classe 'is-active'
            toggles.forEach(svg => svg.classList.toggle('is-active'));
        });
    });


    const loginForm = document.querySelector('.login-form');
    loginForm.addEventListener('submit', function(event){

        event.preventDefault(); //form won't send

        const token = tokenInput.value.trim();

        if (!token) {
            alert('Please enter your personal token!');
            return;
        }
    
        const url = `/api/token-status?token=${token}`;
    
        fetch(url)
            .then(response => response.json()) //convert the answer in json
            .then(data => {
                console.log(data);
                if (data.valid) {
                    data.token = token;
                    data.saved_date = new Date().toISOString().split('T')[0];
                    localStorage.setItem('user_data', JSON.stringify(data));
                    window.location.href = '/';
                } else {
                    alert('Bad token! Try again.');
                }
            })
            .catch(error => {
                console.error('Error fetching token status:', error);
                alert('An error occurred. Please try again later.');
            });
    });
                
});