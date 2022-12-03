const deleteUserBtns = document.querySelectorAll(".delete-user-button");
const modifyButton = document.querySelector(".modify-button-click");
const apiCallPost = (url) => {
  fetch(url, {
    method: "POST",
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log(data);
      window.location.reload();
    })
    .catch((err) => {
      console.log(err);
    });
};

const apiCallGet = (url) => {
  fetch(url, {
    method: "GET",
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log(data);
      window.location.reload();
    })
    .catch((err) => {
      console.log(err);
    });
};

const apiCallDelete = (url) => {
  fetch(url, {
    method: "DELETE",
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log(data);
      window.location.reload();
    })
    .catch((err) => {
      console.log(err);
    });
};

for (let i = 0; i < deleteUserBtns.length; i++) {
  deleteUserBtns[i].addEventListener("click", () => {
    apiCallDelete(deleteUserBtns[i].getAttribute("data-url"));
  });
}

modifyButton.addEventListener("click", (e) => {
  e.preventDefault();
  const form = document.querySelector(".mod-user-form");

  fetch(form.action, {
    method: "post",
    body: new URLSearchParams(new FormData(form)),
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log(data);
      //   window.location.reload();
      let output = document.querySelector(".user-update-sucess");
      output.innerHTML = "User updated successfully";
      setTimeout(() => {
        output.innerHTML = "";
      }, 4000);
    })
    .catch((err) => {
      console.log(err);
      output.innerHTML = "User updated unsuccessfully";
    });
  console.log("defaul prevented");
});
