const getCookie = name => {
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";").map(cookie => cookie.trim());
        for (let i = 0; i < cookies.length; i++) {
            if (cookies[i].startsWith(name + "=")) {
                return cookies[i].substring(name.length + 1);
            }
        }
    }
    return null;
};
const csrftoken = getCookie("csrftoken");

document.addEventListener("click", event => {
    if (event.target.matches(".like-btn")) {
        const likeBtn = event.target;
        const url = likeBtn.getAttribute("data-like-url");
        fetch(url, { method: "POST", headers: { "X-CSRFToken": csrftoken } })
            .then(response => response.json())
            .then(response => {
                const likeNum = likeBtn.parentNode.querySelector(".like-num");
                likeNum.textContent = response.like_num;
                likeBtn.textContent = "いいね解除";
                likeBtn.classList.remove("like-btn");
                likeBtn.classList.add("unlike-btn");
                likeBtn.classList.remove("btn-outline-primary");
                likeBtn.classList.add("btn-outline-danger");
            });
    }
});


document.addEventListener("click", event => {
    if (event.target.matches(".unlike-btn")) {
        const unlikeBtn = event.target;
        const url = unlikeBtn.getAttribute("data-unlike-url");
        fetch(url, { method: "POST", headers: { "X-CSRFToken": csrftoken } })
            .then(response => response.json())
            .then(response => {
                const likeNum = unlikeBtn.parentNode.querySelector(".like-num");
                likeNum.textContent = response.like_num;
                unlikeBtn.textContent = "いいね";
                unlikeBtn.classList.remove("unlike-btn");
                unlikeBtn.classList.add("like-btn");
                unlikeBtn.classList.remove("btn-outline-danger");
                unlikeBtn.classList.add("btn-outline-primary");
            });
    }
});
