window.onload = () => {
    let form = document.getElementById("loginform");
    form.onsubmit = async (e) => handleSubmit(e, form);
};

const handleSubmit = async (event, form) => {
    event.preventDefault();
    try {
        await performLogin(form);
        window.location.pathname = "/sender/dashboard";
    } catch(e) {
        form.renderAlert("danger", e);
    }
};

const performLogin = async (data) => {
    let res = await fetch("/sender/login", {
        method: "POST",
        body: new FormData(data),
        redirect: "follow"
    });

    if (res.status === 200 || res.status === 301) {
        return await res.text();
    } else {
        throw await res.text();
    }
};