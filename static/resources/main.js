try {
    document.getElementById("logout-btn").onclick = async (e) => {
        e.preventDefault();
        const url = "/sender/logout";
        const headers = getCORSHeaders(document.cookie.replace("token=", ""));
        await fetch(url, {
            headers,
            method: "GET"
        });
        document.cookie = ""
        window.location.pathname = "/"
    }
} catch(e) {}