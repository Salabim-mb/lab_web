HTMLDocument.prototype.addElement = (element, props = {}) => {
    let el = document.createElement(element);
    for (let key in props) {
        if (key === "classList") {
            props[key].forEach((item) => {
                el.classList.add(item);
            })
        } else {
            el.setAttribute(key, props[key])
        }
    }
    return el;
}

HTMLElement.prototype.appendAllChildren = (elementList = []) => {
    let parent = this;
    elementList.forEach((el) => {
        parent.appendChild(el);
    });
}