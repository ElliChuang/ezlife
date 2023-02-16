const ezlife = document.querySelector("#ezlife");
const welcomeName = document.querySelector("#welcome-name");
const logout = document.querySelector("#logout");
const userListContent = document.querySelector(".user-list-content");
const add = document.querySelector(".add");
const popupWindowOuter = document.querySelector(".popup-window-outer");
const popupClose = document.querySelector(".popup-closed");
const popupMessage = document.querySelector(".popup-message");
const popupButton = document.querySelector(".popup-button");
const bookList = document.querySelector(".book-list");
const userList = document.querySelector(".user-list");
import { showNoticeWindow, closeNoticeWindow } from "./notice.js";

ezlife.addEventListener("click", () => {
  window.location.href = "/home";
});

// 取得會員狀態
getStatus();
let user = { id: "", name: "", email: "", profile: "" };
async function getStatus() {
  let url = "/api/user/auth";
  let fetchData = await fetch(url, {
    method: "GET",
  });
  let jsonData = await fetchData.json();
  console.log(jsonData);
  if (jsonData.data !== null && jsonData.data.id) {
    welcomeName.innerText = jsonData.data.name;
    user.id = jsonData.data.id;
    user.name = jsonData.data.name;
    user.email = jsonData.data.email;
    user.profile = jsonData.data.profile;
    userList.src = user.profile;
    userList.id = user.id;
    userList.value = user.email;
    getBook();
  } else {
    showNoticeWindow("請重新登入", "", indexPage);
  }
}

// 會員登出
logout.addEventListener("click", memberLogout);
async function memberLogout() {
  let url = "/api/user/auth";
  let fetchUrl = await fetch(url, {
    method: "DELETE",
  });
  let jsonData = await fetchUrl.json();
  console.log("登出", jsonData);
  if (jsonData.ok) {
    indexPage();
  }
}

function indexPage() {
  window.location.href = "/";
}

// 點擊 barList 顯示功能清單
document.addEventListener("click", (elem) => {
  if (elem.target.matches(".user-list")) {
    userListContent.style.display = "block";
  } else {
    userListContent.style.display = "none";
  }
});

// 新增帳簿
add.addEventListener("click", () => {
  popupWindowOuter.style.display = "block";
});

popupClose.addEventListener("click", Close);

function Close() {
  popupWindowOuter.style.display = "none";
  popupMessage.value = "";
}

popupButton.addEventListener("click", () => {
  let message = popupMessage.value;
  if (message === "") {
    popupButton.disable = true;
  } else {
    popupButton.disable = false;
    Close();
    addBook(message);
  }
});

async function getBook() {
  let url = "/api/account_books";
  let fetchUrl = await fetch(url, {
    method: "GET",
  });
  let jsonData = await fetchUrl.json();
  console.log("getBook", jsonData);
  if (jsonData.data !== null && jsonData.data[0].account_book) {
    showBook(jsonData);
  } else if (jsonData.data === "請先登入會員") {
    showNoticeWindow("請登入會員", "", indexPage);
  }
}

async function addBook(msg) {
  let requestBody = { bookName: msg };
  console.log(requestBody);
  let url = "/api/account_books";
  let fetchUrl = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(requestBody),
  });
  let jsonData = await fetchUrl.json();
  if (jsonData.ok) {
    location.reload();
  } else if (jsonData.data === "請先登入會員") {
    showNoticeWindow("請登入會員", "", indexPage);
  } else {
    showNoticeWindow("錯誤訊息", jsonData.data, closeNoticeWindow);
  }
}

function showBook(datas) {
  let len = datas.data.length;
  // show
  for (let i = 0; i < len; i++) {
    let bookListFileDiv = document.createElement("div");
    bookList.appendChild(bookListFileDiv);
    bookListFileDiv.className = "book-list-file";
    let deleteFileDiv = document.createElement("div");
    bookListFileDiv.appendChild(deleteFileDiv);
    deleteFileDiv.className = "delete-file";
    deleteFileDiv.id = datas.data[i].account_book.id;
    let fileDiv = document.createElement("div");
    bookListFileDiv.appendChild(fileDiv);
    fileDiv.className = "file";
    fileDiv.value = datas.data[i].account_book.id;
    let fileNameDiv = document.createElement("div");
    bookListFileDiv.appendChild(fileNameDiv);
    fileNameDiv.className = "file-name";
    fileNameDiv.value = datas.data[i].account_book.id;
    fileNameDiv.innerText = datas.data[i].account_book.book_name;
  }

  // delete
  document.querySelectorAll(".delete-file").forEach((file) => {
    file.addEventListener("click", (elem) => {
      const bookId = elem.target.id;
      deleteBook(bookId);
    });
  });

  // 進入帳簿
  document.querySelectorAll(".file").forEach((file) => {
    file.addEventListener("click", (elem) => {
      const bookId = elem.target.value;
      openBook(bookId);
    });
  });
  document.querySelectorAll(".file-name").forEach((file) => {
    file.addEventListener("click", (elem) => {
      const bookId = elem.target.value;
      openBook(bookId);
    });
  });
}

async function deleteBook(Id) {
  let requestBody = { bookId: Id };
  let url = "/api/account_books";
  let fetchUrl = await fetch(url, {
    method: "DELETE",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(requestBody),
  });
  let jsonData = await fetchUrl.json();
  if (jsonData.ok) {
    location.reload();
  } else {
    showNoticeWindow("訊息通知", jsonData.data, closeNoticeWindow);
  }
}

function openBook(Id) {
  window.location.href = "/account_book/" + Id;
}
