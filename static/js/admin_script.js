const deleteUserBtns = document.querySelectorAll(".delete-user-button");
const modifyButton = document.querySelector(".modify-button-click");

const modifyPostButton = document.querySelector(".modify-post-button");
const deletePostButtons = document.querySelectorAll(".delete-button-posts");
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
for (let i = 0; i < deletePostButtons.length; i++) {
  deletePostButtons[i].addEventListener("click", () => {
    apiCallDelete(deletePostButtons[i].getAttribute("data-url"));
  });
}

if (modifyButton != null) {
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
  });
}
if (modifyPostButton != null) {
  modifyPostButton.addEventListener("click", (e) => {
    e.preventDefault();
    const form = document.querySelector(".mod-pst-frm");

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
        let output = document.querySelector(".post-update-sucess");
        output.innerHTML = "Post updated successfully";
        setTimeout(() => {
          output.innerHTML = "";
        }, 4000);
      })
      .catch((err) => {
        console.log(err);
        output.innerHTML = "Post updated unsuccessfully";
      });
  });
}
