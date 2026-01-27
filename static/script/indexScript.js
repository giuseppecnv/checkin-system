function displayGreeting() { 
    const time = new Date();
    const greeting = time.getHours() < 12 ? "Good Morning," : time.getHours() < 18 ? "Good Afternoon," : "Good Evening,";
    document.querySelector(".greeting").textContent = greeting; 
}

function displayDayWeek() { 
    const time = new Date();
    document.querySelector("#day-week").textContent = time.toLocaleString('default', { weekday: 'long' }); 
}

function displayHour() { 
    const time = new Date();
    document.querySelector(".current-time").textContent = ("0" + time.getHours()).slice(-2) + ":" + ("0" + time.getMinutes()).slice(-2); 
}

function displayMonth() { 
    const time = new Date();
    document.querySelector('.month').textContent = time.toLocaleString('default', { month: 'long' }); 
}

function displayTodayDate() { 
    const time = new Date();
    document.querySelector('.date-month').textContent = time.getDate(); 
}



window.addEventListener('DOMContentLoaded', function() {

    displayGreeting();
    displayDayWeek();
    displayHour();
    setInterval(displayHour, 1000);
    displayMonth();
    displayTodayDate();
    
    const userDataString = localStorage.getItem('user_data');
    
    if (userDataString) {
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
            .then(response => response.json())
            .then(freshData => {
                if (freshData.valid) {
                    freshData.token = userData.token;
                    freshData.saved_date = userData.saved_date;
                    localStorage.setItem('user_data', JSON.stringify(freshData));
                    document.querySelector('.vdash-input').value = freshData.vdash;
                    
                    const vdashName = document.querySelector('.vdash-span');
                    vdashName.textContent = freshData.full_name.split(' ')[0] + '.';

                    const button = document.querySelector('button[type="submit"]');
                    const dot = document.querySelector('.dot');

                    if (!freshData.has_checked_in) {
                        button.textContent = 'Check In';
                        vdashName.style.color = 'hsla(246, 80%, 60%, 1)';
                        document.querySelector('.shift-label').textContent = "READY TO CHECK IN?";
                        document.querySelector('.label-active').textContent = "Inactive";
                        dot.classList.remove('active');
                    } else if (!freshData.has_checked_out) {
                        button.textContent = 'Check Out';
                        button.style.backgroundColor = '#FF7518';
                        vdashName.style.color = '#FF7518';
                        document.querySelector('.shift-label').textContent = "CHECKED AT";
                        document.querySelector('.shift-time').textContent = freshData.checkin_time;
                        document.querySelector('.label-active').textContent = "Active";
                        dot.classList.add('active');
                    } else {
                        document.querySelector('.shift-time').textContent = freshData.checkout_time;
                        document.querySelector('.shift-label').textContent = "CHECKED OUT AT";
                        document.querySelector('.label-active').textContent = "Inactive";
                        button.textContent = 'Logout';
                        dot.classList.remove('active');
                        vdashName.style.color = 'hsla(246, 80%, 60%, 1)';

                        button.onclick = function(e) {
                            e.preventDefault();
                            localStorage.removeItem('user_data');
                            window.location.href = '/login';
                        }
                    }

                    const form = document.querySelector('.card-container');
                    form.addEventListener('submit', function(e) {
                        e.preventDefault();

                        const banner = document.querySelector('.show-banner');

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
                            origin: {y: 0.6}
                        });

                        setTimeout(() => {
                            banner.classList.remove('show');
                            form.submit();
                        }, 1200);

                    });

                }
            })
            
            .catch(error => {
                console.error('Error fetching token status:', error);
                window.location.href = '/login';
            });


    } else { window.location.href = '/login'; }
});

