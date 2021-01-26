const url = "/sender/dashboard"

window.onload = () => {
    let form = document.getElementById("parcelform");
    form.addEventListener("submit", async (e) => handleSubmit(e, form));
    let deleteButtonList = document.querySelectorAll("td#delete-btn");
    deleteButtonList.forEach((el) => {
        el.firstElementChild.addEventListener(
            "click", async (e) => deleteEntry(e, el.parentElement)
        );
    });
    handleNotifications();
}

const deleteEntry = async(event, element) => {
    event.preventDefault();
    const id = element.getAttribute("id");
    try {
        await performDeletion(id)
        window.location.reload(true);
    } catch(e) {
        element.renderAlert("danger", e.message);
    }
}

const handleSubmit = async (event, form) => {
    event.preventDefault();
    const token = document.cookie.replace("token=", '');
    try {
        await addParcel(getFormValues(form), token);
        await pushMessage(token);
        window.location.reload(true);
    } catch(e) {
        console.log(e)
        event.preventDefault();
        form.renderAlert("danger", e.message)
    }
}

const pushMessage = async(token) => {
    let notif_url = "/notifications";
    let res = await fetch(notif_url, {
        method: "POST",
        headers: getCORSHeaders(token),
        body: JSON.stringify({
            receiver: "any_courier",
            message: "New parcel added!",
            date: (new Date()).toISOString()
        })
    })

    if (res.status === 200) {
        return await res.json();
    } else {
        throw await res.json();
    }
};

const addParcel = async (data, token) => {
    const res = await fetch(url, {
        method: "POST",
        body: JSON.stringify(data),
        headers: getCORSHeaders(token)
    });

    if (res.status === 200) {
        return await res.text();
    } else {
        throw await res.text();
    }
}

const performDeletion = async(id, token) => {
    const res = await fetch(url, {
        method: "DELETE",
        headers: {
            ...getCORSHeaders(token),
            "Parcel": id
        }
    });

    if (res.status === 200) {
        return await res.json();
    } else {
        throw await res.json();
    }
};
