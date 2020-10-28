window.onload = () => {
    document.addEventListener("failedServerConnection", () => dispatchErrorAlert())
}

const BACKEND_PATH = "https://infinite-hamlet-29399.herokuapp.com/";

const getCORSHeaders = () => ({
    "Content-Type": "application/json"
});

const getMultiHeaders = () => ({
   "Content-Type": "multipart/form-data"
});

const dispatchErrorAlert = () => {

};