let likeBtn = document.querySelectorAll("#like-button");

const apiCall = (url) => {
  fetch(url, {
    method: "POST",
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log(data);
      console.log("liked post");
      //   window.location.reload();
      likeBtn[0].innerHTML = "Liked";
      likeBtn[0].disabled = true;
    })
    .catch((err) => {
      console.log(err);
    });
};

likeBtn[0].addEventListener("click", () => {
  apiCall(likeBtn[0].getAttribute("data-url"));
});
