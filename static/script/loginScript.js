window.addEventListener('DOMContentLoaded', () => {
    const tokenInput = document.querySelector('.token-field');
    const toggles = document.querySelectorAll('.toggle-password');
    const loginForm = document.querySelector('.login-form');

    if (!tokenInput || !loginForm) {
        return;
    }

    toggles.forEach((btn) => {
        btn.addEventListener('click', () => {
            const isPassword = tokenInput.type === 'password';
            tokenInput.type = isPassword ? 'text' : 'password';
            toggles.forEach((svg) => svg.classList.toggle('is-active'));
        });
    });

    loginForm.addEventListener('submit', (event) => {
        event.preventDefault();

        const token = tokenInput.value.trim();
        if (!token) {
            alert('Please enter your personal token!');
            return;
        }

        fetch(`/api/token-status?token=${token}`)
            .then((response) => response.json())
            .then((data) => {
                if (data.valid) {
                    data.token = token;
                    data.saved_date = new Date().toISOString().split('T')[0];
                    localStorage.setItem('user_data', JSON.stringify(data));
                    window.location.href = '/';
                } else {
                    alert('Bad token! Try again.');
                }
            })
            .catch((error) => {
                console.error('Error fetching token status:', error);
                alert('An error occurred. Please try again later.');
            });
    });
});
