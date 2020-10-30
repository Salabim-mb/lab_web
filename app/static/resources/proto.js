HTMLDocument.prototype.addElement = (element, elProps = {}, objectProps = {}) => {
    let el = document.createElement(element);
    for (let key in elProps) {
        if (key === "classList") {
            elProps[key].forEach((item) => {
                el.classList.add(item);
            })
        } else {
            el.setAttribute(key, elProps[key])
        }
    }
    for (let key in objectProps) {
        el[key] = objectProps[key];
    }
    return el;
}

HTMLElement.prototype.appendAllChildren = function (elementList = []) {
    let parent = this;
    elementList.forEach((el) => {
        parent.appendChild(el);
    });
}

HTMLElement.prototype.renderAlert = function (variant, text) {
    let hideAlert = () => document.removeChild(alertWrapper);

    let alertWrapper = document.addElement("div", {
        classList: ["alert__" + variant, "alert"]
    });
    let closeButton = document.addElement("span", {
        class: "close__btn"
    });
    closeButton.innerHTML = "&times;"
    closeButton.onclick = () => hideAlert();
    let alertMsg = document.addElement("span");
    alertMsg.innerText = text;

    alertWrapper.appendAllChildren([closeButton, alertMsg]);
    document.getElementsByTagName("body")[0].appendChild(alertWrapper);
    setTimeout(() => hideAlert(), 3000);
}