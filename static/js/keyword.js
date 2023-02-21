const keyword = document.querySelector("input[name='keyword']");
const ul = document.querySelector(".keyword-ul");
keyword.addEventListener("keyup", searchKeyword);
async function searchKeyword() {
  removeUl();
  const url = `/api/keywords?keyword=${keyword.value}`;
  const fetchData = await fetch(url, { method: "GET" });
  const jsonData = await fetchData.json();
  console.log(jsonData);
  if (!jsonData.data) {
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
  const li = document.querySelectorAll(".keyword-li");
  li.forEach((item) => {
    ul.removeChild(item);
  });
}

document.addEventListener("click", (elem) => {
  if (elem.target.matches(".keyword-ul")) {
    ul.style.display = "block";
  } else {
    ul.style.display = "none";
  }
});
