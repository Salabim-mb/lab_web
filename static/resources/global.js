const BACKEND_PATH = "https://infinite-hamlet-29399.herokuapp.com/";

const getCORSHeaders = (token = null) => {
    let res = {
        "Content-Type": "application/json"
    };

    return token ? {...res, Authorization: "Token " + token} : res;
};

const getMultiHeaders = () => ({
   "Content-Type": "multipart/form-data"
});

const dispatchErrorAlert = () => {
    alert("There was a problem with connecting to the server, please try again later");
};

const getFormValues = (formElement) => {
    let inputArray = [...formElement.querySelectorAll("input"), ...formElement.querySelectorAll("select")];
    let res = {};
    inputArray.forEach((item) => {
        res = {...res, [item.getAttribute("name")]: item.value}
    });
    return res;
};