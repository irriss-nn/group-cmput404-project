const openModal = document.querySelector("#create-post-btn");
const modal = document.querySelector("#create-post-modal");
const closeModal = document.querySelector("#close-create-post-btn");
const submitModel = document.querySelector("#submit-create-post-btn");

const followingBtn = document.querySelector("#following-btn");
const followingPopup = document.querySelector("#following-popup");
const followingClose = document.querySelector("#popup-close-follow");

const followerBtn = document.querySelector("#follower-btn");
const followerPopup = document.querySelector("#follower-popup");
const followerClose = document.querySelector("#popup-close-follower");

const contentType = document.querySelector("#contenttype-create-post-textarea");
const contentTextInput = document.querySelector(
  "#content-create-post-textarea"
);
const contentFileInput = document.querySelector("#content-create-post-file");

const followBtn = document.querySelector("#follow-user-btn");
let userid;

if (openModal) {
  openModal.addEventListener("click", () => {
    modal.showModal();
  });
}

followerBtn.addEventListener("click", () => {
  followerPopup.style = "display:flex;";
});

followerClose.addEventListener("click", () => {
  followerPopup.style = "display:none;";
});

followingBtn.addEventListener("click", () => {
  followingPopup.style = "display:flex;";
});

followingClose.addEventListener("click", () => {
  followingPopup.style = "display:none;";
});

if (contentType) {
  contentType.addEventListener("change", (e) => {
    if (e.target.value === "text/markdown" || e.target.value === "text/plain") {
      contentTextInput.style.display = "block";
      contentFileInput.style.display = "none";
    } else {
      contentTextInput.style.display = "none";
      contentFileInput.style.display = "block";
    }
    // console.log(e);
  });
}

if (closeModal) {
  closeModal.addEventListener("click", () => {
    //fetch user's post content
    let title = document.querySelector("#title-create-post-textarea");
    let description = document.querySelector(
      "#description-create-post-textarea"
    );
    let content = document.querySelector("#content-create-post-textarea");
    // console.log(title.value);
    // console.log(description.value);
    // console.log(content.value);

    //clear value in textarea
    document.querySelector("#source-create-post-textarea").value = "";
    document.querySelector("#origin-create-post-textarea").value = "";
    document.querySelector("#categories-create-post-textarea").value = "";
    document.querySelector("#title-create-post-textarea").value = "";
    document.querySelector("#description-create-post-textarea").value = "";
    document.querySelector("#content-create-post-textarea").value = "";
    modal.close();
  });
}

if (submitModel) {
  // pass user_id to javascript
  userid = submitModel.getAttribute("userid");
  submitModel.addEventListener("click", () => {
    let title = document.querySelector("#title-create-post-textarea");
    let description = document.querySelector(
      "#description-create-post-textarea"
    );
    let page = document.querySelector("#source-create-post-textarea");
    let size = document.querySelector("#origin-create-post-textarea");
    let contentType = document.querySelector(
      "#contenttype-create-post-textarea"
    );
    let content;
    let categories = document.querySelector("#categories-create-post-textarea");
    let unlisted = document.querySelector('input[name="visibility-create-post-select"]:checked');
    let visibility = document.querySelector('input[name="se"]:checked');
    
    let author = title.getAttribute("data-author");
    let date = new Date().toISOString();
    let payload;
    if (contentType.value === "text/markdown" ||contentType.value === "text/plain") {
      content = document.querySelector("#content-create-post-textarea");
      content = content.value;
      try {
        console.log(content);
        console.log(typeof content);
        // create post without id, payload needs append post id in backend
        payload = {
          title: title.value,
          origin: location.hostname,
          source: location.hostname,
          description: description.value,
          contentType: contentType.value,
          content: content,
          author: { id: author },
          categories: categories.value.split(",").map((x) => x.trim()),
          count: parseInt(size.value)*parseInt(page.value),
          comments: location.hostname,
          commentsSrc: {
            size: parseInt(size.value),
            page: parseInt(page.value),
            type: "comments",
            comments: []
          },
          published: date,
          visibility: visibility.value,
          unlisted: unlisted.value,
          likes: [],
        };
      } catch (e) {
        console.log(e);
        alert(e);
        return;
    }
  
      document.querySelector("#source-create-post-textarea").value = "";
      document.querySelector("#origin-create-post-textarea").value = "";
      document.querySelector("#categories-create-post-textarea").value = "";
      document.querySelector("#title-create-post-textarea").value = "";
      document.querySelector("#description-create-post-textarea").value = "";
      document.querySelector("#content-create-post-textarea").value = "";
      modal.close();
      fetch(submitModel.getAttribute("data-url"), {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })
        .then((response) => {
          return response.json(payload);
        })
        .then((data) => {
          console.log(data);
        })
        .catch((err) => {
          console.log(err);
        });
    } 
    else {
      content = document.querySelector("#content-create-post-file");
      content = content.files[0];
      const reader = new FileReader();
      reader.readAsDataURL(content);
      
      reader.addEventListener("load", ()=> {
        content = reader.result;
  
        try {
          console.log(content);
          console.log(typeof content);
          // create post without id, payload needs append post id in backend
          payload = {
            title: title.value,
            origin: location.hostname,
            source: location.hostname,
            description: description.value,
            contentType: contentType.value,
            content: content,
            author: { id: author },
            categories: categories.value.split(",").map((x) => x.trim()),
            count: parseInt(size.value)*parseInt(page.value),
            comments: location.hostname,
            commentsSrc: {
              size: parseInt(size.value),
              page: parseInt(page.value),
              type: "comments",
              comments: []
            },
            published: date,
            visibility: visibility.value,
            unlisted: unlisted.value,
            likes: [],
          };
        } catch (e) {
          console.log(e);
          alert(e);
          return;
      }
    
        document.querySelector("#source-create-post-textarea").value = "";
        document.querySelector("#origin-create-post-textarea").value = "";
        document.querySelector("#categories-create-post-textarea").value = "";
        document.querySelector("#title-create-post-textarea").value = "";
        document.querySelector("#description-create-post-textarea").value = "";
        document.querySelector("#content-create-post-textarea").value = "";
        modal.close();
        fetch(submitModel.getAttribute("data-url"), {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        })
          .then((response) => {
            return response.json(payload);
          })
          .then((data) => {
            console.log(data);
          })
          .catch((err) => {
            console.log(err);
          });
      });
      
    }
  });

}

if (followBtn) {
  followBtn.addEventListener("click", (e) => {
    e.preventDefault();
    console.log("clicked follow button");
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
}
