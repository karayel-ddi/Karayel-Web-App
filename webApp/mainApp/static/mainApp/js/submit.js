document.addEventListener('DOMContentLoaded', function () {
    const progressBoxes = document.querySelectorAll('.progress-box');
    const submitButton = document.querySelector('.form-submit-btn');

    let currentStep = getCookie('progress') || 0;
    updateProgress(currentStep);

    submitButton.addEventListener('click', function (event) {
        event.preventDefault(); // Sayfanın yenilenmesini engelle

        const formData = new FormData(document.querySelector('.form'));
        fetch('/submit/', {  // '/submit/' URL'sini doğru olduğundan emin olun
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentStep = data.progress_count;
                    setCookie('progress', currentStep, 0.25);
                    updateProgress(currentStep);
                } else {
                    console.error('Error:', data.error);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    });

    function updateProgress(step) {
        progressBoxes.forEach((box, index) => {
            if (index < step) {
                box.classList.add('active');
                box.querySelector('.progress-text').textContent = `${index + 1}. Soru Girildi`;
            } else if (index === step) {
                box.querySelector('.progress-text').textContent = 'Şu an';
            } else {
                box.classList.remove('active');
                box.querySelector('.progress-text').textContent = `${index + 1}. Soru`;
            }
        });

        if (step >= 5) {
            alert('Teşekkürler!');
        }
    }

    function setCookie(name, value, days) {
        let date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        const expires = "expires=" + date.toUTCString();
        document.cookie = name + "=" + value + ";" + expires + ";path=/";
    }

    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }
});
