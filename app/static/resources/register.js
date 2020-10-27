window.onload = () => {
    let form = document.getElementById("form");
    form.addEventListener("submit", (e) => handleSubmit(e, getInputData(form)))

    let loginField = form.querySelector("input#username");
    loginField.addEventListener("change", () => Promise.resolve(handleLoginChange(loginField)));
}

let postRegister = async (data) => {
    let url = "";
    let headers = getMultiHeaders();

    const res = await fetch(url, {
        headers,
        method: "POST",
        body: (new FormData()).appendAll(data)
    });

    if (res.status === 200 || res.status === 201) {
        return await res.json();
    } else {
        throw res.status;
    }
}

const handleLoginChange = async(loginField) => {
    let login = loginField.value;
    if (login.length < 4) {
        renderTooltip("danger", "Login must be longer than 3 characters.");
        loginField.classList.remove("input__box__valid")
        loginField.classList.add("input__box__invalid")

    } else if (login.indexOf(" ") !== -1) {
        renderTooltip("danger", "Login mustn't contain whitespace.");
        loginField.classList.remove("input__box__valid")
        loginField.classList.add("input__box__invalid")

    } else {
        let res = await checkLoginAvailable(login);
        console.log(res);
    }
};

const checkLoginAvailable = async(login) => {
    let url = `${BACKEND_PATH}check/${login}`;
    const res = await fetch(url, {
        method: "GET",
        //headers: getCORSHeaders(),
        //mode: "no-cors",
        // body: JSON.stringify({login: login})
    });

    if (res.status === 200) {
        console.log(res);
        return await res.json();
    } else {
        throw res.status;
    }
}

let toggleElementDisabled = (element, innerText) => {
    if (element.disabled && element.disabled === true) {
        element.setAttribute("disabled", false);
    } else {
        element.setAttribute("disabled", true);
    }
    element.innerHTML = innerText;
};

let checkFormValidity = (form) => {
    let elementList = form.querySelectorAll("input");
    elementList.forEach((item) => {
        if ([null, undefined, ""].includes(item.value)) {
            alert(`${item.name} field cannot be empty!`);
            return false;
        }
    });
    return true;
};

const mapData = (data) => ({

});

const getInputData = (formElement) => {
    let inputList = formElement.querySelectorAll("input") || [];
    let data = {};
    inputList.forEach((element) => {
        data = {
            ...data,
            [element.name]: element.value
        }
    })

    return data;
};

const _handleSubmit = async (event, data) => {
    event.preventDefault();
    let submitBtn =  document.querySelector("button#submitButton");
    let origText = submitBtn.innerHTML;
    toggleElementDisabled(submitBtn, "Loading...");
    try {
        let res = await postRegister(data)
    } catch(e) {
        console.log(e);
        document.dispatchEvent(new CustomEvent("failedRegister"));
    } finally {
        toggleElementDisabled(submitBtn, origText);
    }
}

const onSubmit = async (event) => {
    event.preventDefault();
    const form = document.getElementsByTagName("form");
    if (checkFormValidity(form) === false) {
        event.stopPropagation();
    } else {

    }
};

const renderForm = () => {
    document.addElement("form", {

    })
};

const _sendRegister = function() {

}

const sendRegister = async (login) => {
    const url = BACKEND_PATH + "/check/" + login;
    const res = await fetch(url, {
        method: "GET",

    });

    if (res.status === 200) {
        return await res.json();
    } else {
        throw res.status;
    }
};

const handleSubmit = (e) => {
    e.preventDefault();
    let form = document.getElementById("form");

};


const checkLoginOK = () => {

};




















