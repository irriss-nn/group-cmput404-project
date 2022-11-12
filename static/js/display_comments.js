document.getElementById("myBtn").addEventListener("click", myFunction);
      function myFunction() {
        
          window.location.href="/service/authors/{{post.author.id}}/posts/{{post._id}}/comments/view";
       
      }

document.getElementById("lalaBtn").addEventListener("click", goBack);
function goBack() {
   
        window.history.back();
     
    
}