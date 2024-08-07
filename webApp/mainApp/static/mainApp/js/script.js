document.addEventListener("DOMContentLoaded", function () {
    const cardContainers = document.querySelectorAll(".card-container");

    cardContainers.forEach((container) => {
        container.addEventListener("mouseenter", function () {
            cardContainers.forEach((c) => {
                if (c !== container) {
                    c.style.flex = "0.6";
                }
            });
            container.style.flex = "2";
        });

        container.addEventListener("mouseleave", function () {
            cardContainers.forEach((c) => {
                c.style.flex = "1";
            });
        });
    });

    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.display = 'none';
        }, 5000);
    });

    const waves = document.querySelectorAll('.wave');
    waves.forEach(wave => {
        wave.addEventListener('animationiteration', () => {
            wave.style.transform = `translateX(${Math.random() * 150}px)`;
        });
    });
}); document.addEventListener("DOMContentLoaded", function () {
    const scrollLink = document.querySelector('.scroll-link');

    scrollLink.addEventListener('click', function (event) {
        event.preventDefault();

        const targetId = this.getAttribute('href').substring(1);
        const currentPath = window.location.pathname;

        if (currentPath !== '/') {
            window.location.href = '/?scrollTo=' + targetId;
        } else {
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - (window.innerHeight / 2 - targetElement.clientHeight / 2),
                    behavior: 'smooth'
                });
            }
        }
    });

    const params = new URLSearchParams(window.location.search);
    const scrollToId = params.get('scrollTo');

    if (scrollToId) {
        const targetElement = document.getElementById(scrollToId);

        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - (window.innerHeight / 2 - targetElement.clientHeight / 2),
                behavior: 'smooth'
            });
        }
    }
});