try {
    document.getElementById("logout-btn").onclick = async (e) => {
        e.preventDefault();
        const url = "/sender/logout";
        const headers = getCORSHeaders(document.cookie.replace("token=", ""));
        const res = await fetch(url, {
            headers,
            method: "GET"
        });
        if (res.status === 303) {
            let {oauth_logout} = await res.json();
            await logoutOauth(oauth_logout)
        }
        window.location.pathname = "/"
    }
} catch(e) {}

const logoutOauth = async(url) => {
    await fetch(url, {mode: "no-cors"})
};