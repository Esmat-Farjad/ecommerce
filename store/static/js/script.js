function getCSRFToken() {
    const name = 'csrftoken=';
    const cookies = document.cookie.split(';');

    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name)) {
            return cookie.substring(name.length);
        }
    }
    return '';
}


const cartButtons = document.querySelectorAll(".add-item");
cartButtons.forEach(add => {
    add.addEventListener("click", (e)=>{
        let endPointUrl = e.target.dataset.endPoint;
        const csrfToken = getCSRFToken();
        fetch(endPointUrl,{
            method: 'POST',
            headers: {
                'content-Type': 'application/json',
                'X-CSRFToken': csrfToken     
            }
        }).then(response => response.json().then(data =>{
            console.log(data);
            document.getElementById('num_item').innerHTML = data.num_item;
        })).catch(error =>{console.log("Error: "+error);})
    });
});

