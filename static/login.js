const apiver = 1;

let login_button = document.getElementById('loginB');
login_button.addEventListener("click",function(){
  console.log("fired");

  let password_value = document.getElementById("password").value;
  let email_value = document.getElementById("email").value;

  if( password_value == "" || email_value == "" ){
    console.log("Not valid...")
    return;
  }

  fetch(`/api/v${apiver}/login`, {
    method: "POST",
    body: JSON.stringify({
      password: password_value,
      email: email_value,
    }),
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
  })
    .then(response => response.json())
    .then((data) => {
      if( data['url_target'] ){
        window.location.href = data['url_target'];
      }else{
        alert(data);
      };
    });
});