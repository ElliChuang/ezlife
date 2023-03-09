const ezlife = document.querySelector("#ezlife");
const welcomeName = document.querySelector("#welcome-name");
const logout = document.querySelector("#logout");
const userListContent = document.querySelector(".user-list-content");
const add = document.querySelector(".add");
const popupTitle = document.querySelector(".popup-title");
const popupWindowOuter = document.querySelector(".popup-window-outer");
const popupCloseButton = document.querySelector(".popup-closed");
const popupMessage = document.querySelector(".popup-message");
const popupButton = document.querySelector(".popup-button");
const popupStatus = document.querySelector(".popup-status");
const bookList = document.querySelector(".book-list");
const userList = document.querySelector(".user-list");
import { showNoticeWindow, closeNoticeWindow } from "./notice.js";

ezlife.addEventListener("click", () => {
  window.location.href = "/home";
});
const book = { bookId: "" };

// 取得會員狀態
getStatus();
let user = { id: "", name: "", email: "", profile: "" };
async function getStatus() {
  let url = "/api/user/auth";
  let fetchData = await fetch(url, {
    method: "GET",
  });
  let jsonData = await fetchData.json();
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

// popup message
function showPopup(elem1, elem2, elem3) {
  popupButton.removeEventListener("click", verifyBeforeAdd);
  popupButton.removeEventListener("click", verifyBeforeEdit);
  popupWindowOuter.style.display = "block";
  popupTitle.innerText = elem1;
  popupMessage.value = elem2;
  popupButton.addEventListener("click", elem3);
  popupCloseButton.addEventListener("click", closePopup);
}

function closePopup() {
  popupWindowOuter.style.display = "none";
  popupMessage.value = "";
  popupStatus.innerText = "";
}

function verifyBeforeAdd() {
  let message = popupMessage.value.trim();
  if (message.length === 0) {
    popupButton.disable = true;
    popupStatus.innerText = "請輸入帳簿名稱";
  } else {
    addBook(message);
  }
}

function verifyBeforeEdit() {
  let message = popupMessage.value.trim();
  if (message.length === 0) {
    popupButton.disable = true;
    popupStatus.innerText = "請輸入帳簿名稱";
  } else {
    editBook(message);
  }
}

popupMessage.addEventListener("focus", () => {
  popupStatus.innerText = "";
});

// 新增帳簿
add.addEventListener("click", () => {
  showPopup("建立帳簿", "", verifyBeforeAdd);
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
    popupStatus.innerText = jsonData.data;
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
    let editFileDiv = document.createElement("div");
    bookListFileDiv.appendChild(editFileDiv);
    editFileDiv.className = "edit-file";
    editFileDiv.id = `edit-${datas.data[i].account_book.id}`;
    let fileDiv = document.createElement("div");
    bookListFileDiv.appendChild(fileDiv);
    fileDiv.className = "file";
    fileDiv.value = datas.data[i].account_book.id;
    let fileNameDiv = document.createElement("div");
    bookListFileDiv.appendChild(fileNameDiv);
    fileNameDiv.className = "file-name";
    fileNameDiv.id = `file-name-${datas.data[i].account_book.id}`;
    fileNameDiv.value = datas.data[i].account_book.id;
    fileNameDiv.innerText = datas.data[i].account_book.book_name;
    if (datas.data[i].account_book.created_member_id === user.id) {
      let hostDiv = document.createElement("div");
      bookListFileDiv.appendChild(hostDiv);
      hostDiv.className = "crown";
    }
  }

  // delete
  document.querySelectorAll(".delete-file").forEach((file) => {
    file.addEventListener("click", (elem) => {
      const bookId = elem.target.id;
      deleteBook(bookId);
    });
  });

  // edit
  document.querySelectorAll(".edit-file").forEach((file) => {
    file.addEventListener("click", (elem) => {
      const fileId = elem.target.id;
      const bookId = fileId.split("-")[1];
      book.bookId = bookId;
      const bookName = document.getElementById(`file-name-${bookId}`);
      let value = bookName.innerText;
      showPopup("編輯帳簿名稱", value, verifyBeforeEdit);
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

// edit book name
async function editBook(msg) {
  let requestBody = { bookName: msg, bookId: book.bookId };
  console.log(requestBody);
  let url = "/api/account_books";
  let fetchUrl = await fetch(url, {
    method: "PUT",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(requestBody),
  });
  let jsonData = await fetchUrl.json();
  if (jsonData.ok) {
    const bookTitle = document.getElementById(
      `file-name-${jsonData.data.book_id}`
    );
    bookTitle.innerText = jsonData.data.book_name;
    closePopup();
    showNoticeWindow("訊息通知", "更新成功", closeNoticeWindow);
  } else if (jsonData.data === "請先登入會員") {
    showNoticeWindow("請登入會員", "", indexPage);
  } else {
    popupStatus.innerText = jsonData.data;
  }
  popupButton.disable = false;
}
