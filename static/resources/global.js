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

const handleNotifications = () => {
    const innerFunc = async () => {
        const el = document.querySelector("div#notification-wrapper")
        try {
            const {notifications} = await fetchNotifications();
            for (let notification of notifications) {
                el.renderAlert("success", `${notification.sender}\n${notification.message}\ndate: ${notification.date}`)
            }
        } catch (e) {
            if (e && e.message) {
                document.querySelector("body").renderAlert("danger", e.message);
            }
        } finally {
            handleNotifications();
        }
    };
    innerFunc();
}

const fetchNotifications = async () => {
    let url = "/notifications";
    const res = await fetch(url, {
        method: "GET",
        headers: getCORSHeaders()
    });

    if (res.status === 200) {
        return await res.json();
    } else {
        throw await res.json();
    }
};