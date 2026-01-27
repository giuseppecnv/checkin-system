window.addEventListener('DOMContentLoaded', function() {
    const datePicker = document.getElementById('datePicker');
    
    datePicker.addEventListener('change', function() {
        const selectedDate = this.value;  // Formato: YYYY-MM-DD
        
        // Reindirizza alla dashboard con la nuova data
        window.location.href = `/dashboard?date_str=${selectedDate}`;
    });
});