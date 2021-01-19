window.onload = () => {
    let form = document.getElementById("loginform").firstElementChild;
    form.onsubmit = async (e) => handleSubmit(e, form);
    document.querySelector("button#login-oauth-btn").addEventListener("click", async (e) => handleOAuth(e))
};

const handleSubmit = async (event, form) => {
    event.preventDefault();
    try {
        await performLogin( getFormValues(form) );
        window.location.pathname = "/sender/dashboard";
    } catch(e) {
        form.renderAlert("danger", e.message);
    }
};

const performLogin = async (data) => {
    let res = await fetch("/sender/login", {
        method: "POST",
        body: JSON.stringify(data),
        headers: getCORSHeaders()
    });

    if (res.status === 200 || res.status === 301) {
        return await res.json();
    } else {
        throw await res.json();
    }
};

const handleOAuth = async (e) => {
    e.preventDefault();
    console.log("oauth attempt")
    window.location.replace('/login/oauth')
};