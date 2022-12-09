const search = document.querySelector("#search-form");
const shareBtn = document.querySelectorAll("#sharebtn");

const sharePopup = document.querySelector("#share-model");
const shareClose = document.querySelector(".popup-close");

const following = document.querySelectorAll(".person-share-btn");

let shareUrl;

search.addEventListener("submit", (e) => {
  e.preventDefault();
  let name = e.target[0].value.replace(/ /g, "_");
  window.location.replace(`/author/${name}`);
});

shareBtn.forEach((share) => {
  share.addEventListener("click", (e) => {
    currentPost = e.target.getAttribute("data-url");
    shareUrl = e.target.getAttribute("data-url");
    sharePopup.show();
  });
});

shareClose.addEventListener("click", () => {
  sharePopup.close();
});

following.forEach((person) => {
  person.addEventListener("click", (e) => {
    shareUrl += e.target.getAttribute("data-author");

    fetch(shareUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        console.log(response);
        person.disabled = true;
      })
      .catch((err) => {
        console.log(err);
      });

    shareUrl = currentPost;
  });
});
