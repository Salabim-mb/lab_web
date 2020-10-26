let postRegister = async (data) => {
    let url = "";
    let headers = {
        "Content-Type": ""
    };

    const res = await fetch(url, {
        headers,
        method: "POST",
        body: new FormData(data)
    });

    if (res.status === 200 || res.status === 201) {
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

const handleSubmit = async (event, data) => {
    event.preventDefault();
    let submitBtn =  document.querySelector("button#submitButton");
    let origText = submitBtn.innerHTML;
    toggleElementDisabled(submitBtn, "Loading...");
    try {
        let res = await postRegister(data)
    } catch(e) {

    } finally {
        toggleElementDisabled(submitBtn, origText);
    }
}