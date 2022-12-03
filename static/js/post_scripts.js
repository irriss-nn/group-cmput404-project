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
      // console.log("liked post");
      
      //   window.location.reload();
      likeBtn[0].innerHTML = "Liked";
      likeBtn[0].disabled = true;
    })
    .catch((err) => {
      console.log(err);
    });
};

for (let i =0; i<likeBtn.length; i++) {
  likeBtn[i].addEventListener("click", () => {
    apiCall(likeBtn[i].getAttribute("data-url"));
  });
}

