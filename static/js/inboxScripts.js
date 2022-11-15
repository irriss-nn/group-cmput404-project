const acceptBtns = document.querySelectorAll(".req-accept-btn");
const rejectBtns = document.querySelectorAll(".req-reject-btn");
const dismissBtns = document.querySelectorAll(".req-dismiss-btn");

const apiCall = (url) => {
  fetch(url, {
    method: "POST",
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log(data);
    })
    .catch((err) => {
      console.log(err);
    });
};

for (let i = 0; i < acceptBtns.length; i++) {
  acceptBtns[i].addEventListener("click", () => {
    apiCall(acceptBtns[i].getAttribute("data-url"));
  });

  rejectBtns[i].addEventListener("click", () => {
    apiCall(acceptBtns[i].getAttribute("data-url"));
  });
}

for (let i = 0; i < dismissBtns.length; i++) {
  dismissBtns[i].addEventListener("click", () => {
    apiCall(acceptBtns[i].getAttribute("data-url"));
  });
}
