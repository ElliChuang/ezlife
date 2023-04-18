const keyword = document.querySelector("input[name='keyword']");
const ul = document.querySelector(".keyword-ul");
const url = location.href;
const bookId = url.split("account_book/")[1].split("/")[0];

let removing = false;
keyword.addEventListener("keyup", searchKeyword);
async function searchKeyword() {
  if (removing) return;
  removeUl();
  removing = true;
  const url = `/api/keywords?bookId=${bookId}&keyword=${keyword.value}`;
  const fetchData = await fetch(url, { method: "GET" });
  const jsonData = await fetchData.json();
  console.log(jsonData);
  if (!jsonData.data) {
    removing = false;
    return;
  }
  if (jsonData.ok) {
    const len = jsonData.data.length;
    for (let i = 0; i < len; i++) {
      const li = document.createElement("li");
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
    resolve();
  });
}

document.addEventListener("click", (elem) => {
  if (elem.target.matches(".keyword-ul")) {
    ul.style.display = "block";
  } else {
    ul.style.display = "none";
  }
});
