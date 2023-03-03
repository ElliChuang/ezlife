const keyword = document.querySelector("input[name='keyword']");
const ul = document.querySelector(".keyword-ul");
let removing = false;
keyword.addEventListener("keyup", searchKeyword);
async function searchKeyword() {
  if (removing) return;
  removeUl();
  removing = true;
  console.log("remove");
  const url = `/api/keywords?keyword=${keyword.value}`;
  const fetchData = await fetch(url, { method: "GET" });
  const jsonData = await fetchData.json();
  console.log(jsonData);
  if (!jsonData.data) {
    removing = false;
    return;
  }
  if (jsonData.ok) {
    const ul = document.querySelector(".keyword-ul");
    let len = jsonData.data.length;
    for (let i = 0; i < len; i++) {
      let li = document.createElement("li");
      ul.appendChild(li);
      li.className = "keyword-li";
      li.innerText = jsonData.data[i];
    }
    ul.style.display = "block";
    removing = false;
  }
  const options = document.querySelectorAll(".keyword-li");
  options.forEach((elem) => {
    elem.addEventListener("click", function choose() {
      keyword.value = this.innerText;
      ul.style.display = "none";
    });
  });
}

function removeUl() {
  return new Promise((resolve) => {
    const li = document.querySelectorAll(".keyword-li");
    li.forEach((item) => {
      ul.removeChild(item);
    });
    resolve(); // resolve the promise when the list is removed
  });
}

document.addEventListener("click", (elem) => {
  if (elem.target.matches(".keyword-ul")) {
    ul.style.display = "block";
  } else {
    ul.style.display = "none";
  }
});
