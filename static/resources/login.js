window.onload = () => {
    let form = document.getElementById("loginform");
    form.onsubmit = async (e) => handleSubmit(e, form);
};

const handleSubmit = async (event, form) => {
    event.preventDefault();
    try {
        let {token} = await performLogin( getFormValues(form) );
        document.cookie = 'token=' + token;
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