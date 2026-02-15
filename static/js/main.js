/**
 * Portfolio Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
    // Navbar mobile toggle
    const navbarToggle = document.querySelector('.navbar-toggle');
    const navbarNav = document.querySelector('.navbar-nav');

    const aboutContainer = document.getElementById('about-container');
    const aboutSection = document.getElementById('about-section');
    const btnClose = document.getElementById('btn-close');

    const firstVisit = localStorage.getItem('firstVisit')

    if (navbarToggle && navbarNav) {
        navbarToggle.addEventListener('click', function () {
            navbarNav.classList.toggle('active');
        });

        // Close menu when clicking on a link
        const navLinks = navbarNav.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function () {
                navbarNav.classList.remove('active');
            });
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                e.preventDefault();
                const target = document.querySelector(targetId);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Animate skill bars on scroll
    const skillBars = document.querySelectorAll('.skill-progress');

    const animateSkills = () => {
        skillBars.forEach(bar => {
            const width = bar.style.width;
            if (width && width !== '0%') {
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = width;
                }, 100);
            }
        });
    };

    // Use Intersection Observer for skill animation
    const skillsSection = document.querySelector('.skills-section');
    if (skillsSection && skillBars.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateSkills();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });

        observer.observe(skillsSection);
    }

    // Add animation class on scroll for project cards
    const projectCards = document.querySelectorAll('.project-card');

    if (projectCards.length > 0) {
        const cardObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, index * 100);
                    cardObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        projectCards.forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            cardObserver.observe(card);
        });
    }

    // Form validation
    const contactForm = document.querySelector('.contact-form');

    if (contactForm) {
        contactForm.addEventListener('submit', function (e) {
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const subject = document.getElementById('subject');
            const message = document.getElementById('message');

            let isValid = true;

            // Simple validation
            if (!name.value.trim()) {
                markAsInvalid(name);
                isValid = false;
            } else {
                markAsValid(name);
            }

            if (!email.value.trim() || !isValidEmail(email.value)) {
                markAsInvalid(email);
                isValid = false;
            } else {
                markAsValid(email);
            }

            if (!subject.value.trim()) {
                markAsInvalid(subject);
                isValid = false;
            } else {
                markAsValid(subject);
            }

            if (!message.value.trim()) {
                markAsInvalid(message);
                isValid = false;
            } else {
                markAsValid(message);
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function markAsInvalid(field) {
        field.style.borderColor = '#e74c3c';
    }

    function markAsValid(field) {
        field.style.borderColor = '#27ae60';
    }

    // Close alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });

    // About section in the page home
    if (!firstVisit) {
        aboutContainer.classList.remove('hidden');
        aboutContainer.classList.add('flex');
        localStorage.setItem('firstVisit', true);
    }

    btnClose?.addEventListener('click', function () {
        aboutContainer.classList.add('hidden');
        aboutContainer.classList.remove('flex');

    });

    window.document.addEventListener('click', function (e) {
        if (aboutContainer === e.target) {
            aboutContainer.classList.add('hidden');
            aboutContainer.classList.remove('flex');
        }
    });
});
