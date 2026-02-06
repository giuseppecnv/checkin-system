const pad2 = (value) => String(value).padStart(2, '0');

function updateHeaderTime({
    greetingEl,
    dayWeekEl,
    currentTimeEl,
    monthEl,
    dateEl,
}) {
    const now = new Date();
    const hour = now.getHours();

    greetingEl.textContent = hour < 12 ? 'Good Morning,' : hour < 18 ? 'Good Afternoon,' : 'Good Evening,';
    dayWeekEl.textContent = now.toLocaleString('default', { weekday: 'long' });
    currentTimeEl.textContent = `${pad2(hour)}:${pad2(now.getMinutes())}`;
    monthEl.textContent = now.toLocaleString('default', { month: 'long' });
    dateEl.textContent = now.getDate();
}

function setShiftState({
    button,
    dot,
    shiftLabel,
    shiftTime,
    labelActive,
    vdashName,
    data,
}) {
    if (!data.has_checked_in) {
        button.textContent = 'Check In';
        vdashName.style.color = 'hsla(246, 80%, 60%, 1)';
        shiftLabel.textContent = 'READY TO CHECK IN?';
        labelActive.textContent = 'Inactive';
        dot.classList.remove('active');
        return;
    }

    if (!data.has_checked_out) {
        button.textContent = 'Check Out';
        button.style.backgroundColor = '#FF7518';
        vdashName.style.color = '#FF7518';
        shiftLabel.textContent = 'CHECKED AT';
        shiftTime.textContent = data.checkin_time;
        labelActive.textContent = 'Active';
        dot.classList.add('active');
        return;
    }

    shiftTime.textContent = data.checkout_time;
    shiftLabel.textContent = 'CHECKED OUT AT';
    labelActive.textContent = 'Inactive';
    button.textContent = 'Logout';
    dot.classList.remove('active');
    vdashName.style.color = 'hsla(246, 80%, 60%, 1)';
}

window.addEventListener('DOMContentLoaded', () => {
    const greetingEl = document.querySelector('.greeting');
    const dayWeekEl = document.querySelector('#day-week');
    const currentTimeEl = document.querySelector('.current-time');
    const monthEl = document.querySelector('.month');
    const dateEl = document.querySelector('.date-month');

    if (!greetingEl || !dayWeekEl || !currentTimeEl || !monthEl || !dateEl) {
        return;
    }

    updateHeaderTime({ greetingEl, dayWeekEl, currentTimeEl, monthEl, dateEl });
    setInterval(() => {
        updateHeaderTime({ greetingEl, dayWeekEl, currentTimeEl, monthEl, dateEl });
    }, 1000);

    const userDataString = localStorage.getItem('user_data');
    if (!userDataString) {
        window.location.href = '/login';
        return;
    }

    const userData = JSON.parse(userDataString);
    if (!userData.token) {
        localStorage.removeItem('user_data');
        window.location.href = '/login';
        return;
    }

    const today = new Date().toISOString().split('T')[0];
    if (userData.saved_date !== today) {
        localStorage.removeItem('user_data');
        window.location.href = '/login';
        return;
    }

    fetch(`/api/token-status?token=${userData.token}`)
        .then((response) => response.json())
        .then((freshData) => {
            if (!freshData.valid) {
                window.location.href = '/login';
                return;
            }

            freshData.token = userData.token;
            freshData.saved_date = userData.saved_date;
            localStorage.setItem('user_data', JSON.stringify(freshData));

            const vdashInput = document.querySelector('.vdash-input');
            const vdashName = document.querySelector('.vdash-span');
            const button = document.querySelector('button[type="submit"]');
            const dot = document.querySelector('.dot');
            const shiftLabel = document.querySelector('.shift-label');
            const shiftTime = document.querySelector('.shift-time');
            const labelActive = document.querySelector('.label-active');
            const form = document.querySelector('.card-container');
            const banner = document.querySelector('.show-banner');

            if (
                !vdashInput ||
                !vdashName ||
                !button ||
                !dot ||
                !shiftLabel ||
                !shiftTime ||
                !labelActive ||
                !form ||
                !banner
            ) {
                return;
            }

            vdashInput.value = freshData.vdash;
            vdashName.textContent = `${freshData.full_name.split(' ')[0]}.`;

            setShiftState({
                button,
                dot,
                shiftLabel,
                shiftTime,
                labelActive,
                vdashName,
                data: freshData,
            });

            if (freshData.has_checked_in && freshData.has_checked_out) {
                button.onclick = (event) => {
                    event.preventDefault();
                    localStorage.removeItem('user_data');
                    window.location.href = '/login';
                };
            }

            form.addEventListener('submit', (event) => {
                event.preventDefault();

                if (!freshData.has_checked_in) {
                    banner.textContent = 'Check-in successful! 🎉';
                    banner.classList.add('show');
                } else if (!freshData.has_checked_out) {
                    banner.textContent = 'Check-Out successful! 🎉';
                    banner.classList.add('show');
                }

                confetti({
                    particleCount: 100,
                    spread: 70,
                    origin: { y: 0.6 },
                });

                setTimeout(() => {
                    banner.classList.remove('show');
                    form.submit();
                }, 1200);
            });
        })
        .catch((error) => {
            console.error('Error fetching token status:', error);
            window.location.href = '/login';
        });
});
