const observer = new IntersectionObserver((items) => {
    items.forEach((item) => {
        if (item.isIntersecting) {
            item.target.classList.add('item-show');
        }
    });
});

const animateItems = document.querySelectorAll('.sam');
animateItems.forEach((item) => observer.observe(item));

