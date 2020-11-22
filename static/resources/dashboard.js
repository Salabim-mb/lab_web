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
}

const deleteEntry = async(event, element) => {
    event.preventDefault();
    const id = element.getAttribute("id");
    try {
        await performDeletion(id)
        window.location.reload(true);
    } catch(e) {
        element.renderAlert("danger", e);
    }
}

const handleSubmit = async (event, form) => {
    event.preventDefault();
    try {
        await addParcel(form);
        window.location.reload(true);
    } catch(e) {
        event.preventDefault();
        form.renderAlert("danger", e)
    }
}

const addParcel = async (data) => {
    const res = await fetch(url, {
        method: "POST",
        body: new FormData(data),
    });

    if (res.status === 200) {
        return await res.text();
    } else {
        throw await res.text();
    }
}

const performDeletion = async(id) => {
    const res = await fetch(url, {
        method: "DELETE",
        headers: {
            "Parcel": id
        }
    });

    if (res.status === 200) {
        return await res.text();
    } else {
        throw await res.text();
    }
};
