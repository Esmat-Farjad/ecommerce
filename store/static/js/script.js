// store csrf token
function getCSRFToken() {
    const name = 'csrftoken=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookies = decodedCookie.split(';');
  
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.indexOf(name) === 0) {
        return cookie.substring(name.length, cookie.length);
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