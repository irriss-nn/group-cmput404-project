let likeBtn = document.querySelectorAll("#like-button");
const apiCall = (url, buttonNum) => {
  //Check before giving a like:
  
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
      likeBtn[buttonNum].innerHTML = "Liked";
      likeBtn[buttonNum].disabled = true;
    })
    .catch((err) => {
      console.log(err);
    });
  
};

function checkLike(buttonNum) {
  let authorid = likeBtn[buttonNum].getAttribute("authorid");
  let postid = likeBtn[buttonNum].getAttribute("postid");
  fetch(`/service/authors/likes/${authorid}/${postid}/${"post"}/like_already`).then((response)=> response.json())
  .then((result)=>{
    
    console.log(result);
    if (result == "false"){
      // likeBtn[buttonNum].innerHTML = "Like Post";
      // likeBtn[buttonNum].disabled = false;
    } else {
      likeBtn[buttonNum].innerHTML = "Liked";
      likeBtn[buttonNum].disabled = true;
      
    }
  });
}

for (let i =0; i<likeBtn.length; i++) {
  checkLike(i);
  likeBtn[i].addEventListener("click", () => {
    apiCall(likeBtn[i].getAttribute("data-url"), i);
  });
}

