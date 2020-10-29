window.onload = () => {
    let form = document.getElementById("form");
    form.addEventListener("submit", (e) => handleSubmit(e, form))

    let loginField = form.querySelector("input#username");
    loginField.addEventListener("change", () => Promise.resolve(handleLoginChange(loginField)));
}

let postRegister = async (data) => {
    let url = `${BACKEND_PATH}sender/register`;

    const res = await fetch(url, {
        method: "POST",
        body: new FormData(data)
    });
    let answer = Promise.resolve(res);

    if (res.status === 200 || res.status === 201) {
        return answer;
    }  else {
        throw {...res, errorDoc: answer};
    }
}

const handleLoginChange = async(loginField) => {
    let login = loginField.value;
    if (login.length < 8) {
        loginField.renderTooltip("danger", "Login must be longer than 7 characters.");
        loginField.classList.remove("input__box__valid")
        loginField.classList.add("input__box__invalid")

    } else if (login.indexOf(" ") !== -1) {
        loginField.renderTooltip("danger", "Login mustn't contain whitespace.");
        loginField.classList.remove("input__box__valid")
        loginField.classList.add("input__box__invalid")

    } else try {
        let res = await checkLoginAvailable(login);
        if (Object.values(res)[0] !== "available") {
            loginField.renderTooltip("danger", "Login is already taken.");
            loginField.classList.remove("input__box__valid")
            loginField.classList.add("input__box__invalid")
        } else {
            loginField.renderTooltip("success", "Login available!");
            loginField.classList.remove("input__box__invalid")
            loginField.classList.add("input__box__valid")
        }
    } catch(e) {
        document.dispatchEvent(new CustomEvent("failedServerConnection"));
    }
};

const checkLoginAvailable = async(login) => {
    let url = `${BACKEND_PATH}check/${login}`;
    const res = await fetch(url, {
        method: "GET",
    });

    if (res.status === 200) {
        return await res.json();
    } else {
        throw res.status;
    }
}

let toggleElementDisabled = (element, innerText) => {
    if (element.disabled && element.disabled === true) {
        element.setAttribute("disabled", false);
        element.disabled = false;
    } else {
        element.setAttribute("disabled", true);
        element.disabled = true;
    }
    element.innerText = innerText;
};

const handleSubmit = async (event, data) => {
    event.preventDefault();
    let submitBtn =  data.querySelector("button#submit-btn");
    let origText = submitBtn.innerText;
    if (checkPasswords(data.querySelectorAll('input[type="password"]'))) {
        toggleElementDisabled(submitBtn, "Loading...");
        try {
            await postRegister(data);
            alert("You've been successfully registered!");
            window.location.pathname = "/";
        } catch(e) {
            if (e.status === 500) {
                document.dispatchEvent(new CustomEvent("failedServerConnection"));
            } else {
                handleFailedRequest(data, e.errorDoc)
            }
        } finally {
            toggleElementDisabled(submitBtn, origText);
        }
    } else {
        data.querySelector('input[type="password"]').renderTooltip(
            "danger",
            "Passwords must be equal and contain at least 8 characters: at least one capital letter, one digit and one special char."
        );
    }
}

const handleFailedRequest = (formElement, errorDoc) => {

}

const checkPasswords = (passwordFields) => {
    let password = passwordFields[0].value;
    let password_rep = passwordFields[1].value;

    return (
        password.includes(/\d/) &&
        password.includes(/[!@#$%^&*\-_]/) &&
        password.includes(/([A-Z]|[ĄĘĆŃŁÓŻŹ])/) &&
        password === password_rep
    );
};



















