let respondToScroll = () => {
    const scrollOffset = 20;
    let navbar = document.querySelector("header");
    if (document.body.scrollTop > scrollOffset || document.documentElement.scrollTop > scrollOffset) {
        navbar.classList.remove("")
    }
}

const BACKEND_PATH = "https://infinite-hamlet-29399.herokuapp.com/";

const getCORSHeaders = () => ({
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    Origin: "https://parcelexpress.herokuapp.com/"
});

const getMultiHeaders = () => ({
   "Content-Type": "multipart/form-data"
});

const renderTooltip = (variant, text) => {

};