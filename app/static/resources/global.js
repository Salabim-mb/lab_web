const BACKEND_PATH = "https://infinite-hamlet-29399.herokuapp.com/";

const getCORSHeaders = () => ({
    "Content-Type": "application/json"
});

const getMultiHeaders = () => ({
   "Content-Type": "multipart/form-data"
});

const dispatchErrorAlert = () => {
    alert("There was a problem with connecting to the server, please try again later");
};