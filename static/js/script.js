const search = document.querySelector("#search-form");

search.addEventListener("submit", (e) => {
  e.preventDefault();
  let name = (e.target[0].value).replace(/ /g,"_");
  window.location.replace(`/author/${name}`);
});
