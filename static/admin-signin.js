const apiver = 1;

let login_button = document.getElementById('logBtn');
login_button.addEventListener("click",function(){
  let password_value = document.getElementById("password").value;
  let username_value = document.getElementById("username").value;

  if( password_value == "" || username_value == "" ){
    console.log("Not valid...")
    return;
  }

  fetch(`/api/v${apiver}/admin-auth`, {
    method: "POST",
    body: JSON.stringify({
      password: password_value,
      username: username_value,
    }),
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
  })
    .then((response) => response.json())
    .then((json) => console.log(json));
});