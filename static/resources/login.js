// window.onload = () => {
//     let form = document.getElementById("loginform");
//     form.onsubmit = async (e) => handleSubmit(e, form);
// };

const handleSubmit = async (event, form) => {
    try {
        await performLogin(form);
        window.location.pathname = "/sender/dashboard";
    } catch(e) {
        event.preventDefault();
        form.renderAlert("error", e);
    }
};

const performLogin = async (data) => {
    let res = await fetch("/sender/login", {
        method: "POST",
        body: new FormData(data),
        redirect: "follow"
    });

    if (res.status !== 301) {
        throw await res.text();
    }
};