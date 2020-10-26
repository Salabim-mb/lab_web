let respondToScroll = () => {
    const scrollOffset = 20;
    let navbar = document.querySelector("header");
    if (document.body.scrollTop > scrollOffset || document.documentElement.scrollTop > scrollOffset) {
        navbar.classList.remove("")
    }
}