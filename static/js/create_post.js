const openModal = document.querySelector("#create-post-btn");
const modal = document.querySelector("#create-post-modal");
const closeModal = document.querySelector("#close-create-post-btn");

const followBtn = document.querySelector("#follow-user-btn");

if (openModal) {
  openModal.addEventListener("click", () => {
    modal.showModal();
  });
}

closeModal.addEventListener("click", () => {
  //fetch user's post content
  let title = document.querySelector("#title-create-post-textarea");
  let description = document.querySelector("#description-create-post-textarea");
  let content = document.querySelector("#content-create-post-textarea");
  console.log(title.value);
  console.log(description.value);
  console.log(content.value);

  //clear value in textarea
  document.querySelector("#title-create-post-textarea").value = "";
  document.querySelector("#description-create-post-textarea").value = "";
  document.querySelector("#content-create-post-textarea").value = "";
  modal.close();
});

followBtn.addEventListener("click", (e) => {
  e.preventDefault();

  fetch(followBtn.getAttribute("data-url"), {
    method: "POST",
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      document.getElementById("follow-user-btn").disabled = true;
      document.getElementById("follow-user-btn").innerHTML = "Sent Request";
      document.getElementById("follow-user-btn").style.pointerEvents = "none";
      console.log(data);
    })
    .catch((err) => {
      console.log(err);
    });
});
