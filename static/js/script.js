const search = document.querySelector("#search-form");

search.addEventListener("submit", (e) => {
  e.preventDefault();
  console.log(e.target[0].value); // replace with get request for author page url
});
