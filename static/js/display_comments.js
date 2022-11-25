// document.getElementById("myBtn").addEventListener("click", myFunction);
// function myFunction() {
//   window.location.href =
//     "/service/authors/{{post.author.id}}/posts/{{post._id}}/comments/view";
// }

// document.getElementById("lalaBtn").addEventListener("click", goBack);
// function goBack() {
//   window.history.back();
// }

var click = 1;
var length = "{{comments.comments|length}}" ;
var size = "{{comments.size}}";
console.log("biu1="+((click-1)*size));
if (length!=0){
    console.log("biu2="+((click-1)*size));
    document.getElementById("myBtn").addEventListener("click", myFunction);
    if((click-1)*size<length){
        function myFunction(){//update function once next is clicked
            click += 1;//page tracker
            let com = {{ comments|tojson }};
            console.log("click="+click);
            console.log("length="+length);
            console.log("biu="+((click-1)*size));
            console.log("size="+size)
            display(click);
        }
    }

}else{
    document.getElementById("comment-box").innerHTML = "No Comment for this post yet";
}
function display(page){//begin to display per page
    console.log("{{comments.comments|length}}");
    //let comments = {{ comments|tojson }};
    let com = {{ comments|tojson }};
    console.log(com.comments);
    if (length != 0){
    //frist page
    document.getElementById("comment-header").innerHTML = "Comment Page "+page;
    document.getElementById("comment-box").innerHTML = "";
    for(i=0;i<=com.size;i++){
    let check = (page-1)*size;
    console.log('check'+check)
    if((check+i) < length){
        let comBox = document.getElementById("comment-box")
        document.getElementById("comment-box").innerHTML += "<br></br>"
        document.getElementById("comment-box").innerHTML +=  com.comments[check+i]['comment'];
        document.getElementById("comment-box").innerHTML +=  " --"
        document.getElementById("comment-box").innerHTML +=  com.comments[check+i]['author'].displayName;
        let likeButton = document.createElement("button");
        likeButton.innerHTML = "Like";
        likeButton.id = com.comments[check+i]['_id'];
        likeButton.classList.add("like-buts");
        comBox.appendChild(likeButton);
    }
    if(i==com.size){
    addListenersToAllButtons();
    }
}
    }
  }
    window.onload = display(1);

      document.getElementById("lalaBtn").addEventListener("click", goBack);
      function goBack() {
        //if statement needed here
        if(click>1){
          click -= 1;
          display(click);
          console.log(click);
        }
    }

    function addListenersToAllButtons () {
      let buttons = document.querySelectorAll('.like-buts');
      for (let i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener('click', function () {
            apiCall("/service/authors/likes/create/comment/"+buttons[i].id)
            buttons[i].innerHTML = "Liked";
            buttons[i].disabled = true;
        });
      }
    }

    const apiCall = (url) => {
        fetch(url, {
          method: "POST",
        })
          .then((response) => {
            return response.json();
          })
          .then((data) => {
            console.log(data);
            console.log("liked comment");
            //   window.location.reload();

          })
          .catch((err) => {
            console.log(err);
          });
  };
