const ezlife = document.querySelector("#ezlife");
const home = document.querySelector("#home-page");
const accountBookes = document.querySelector("#account-books");
const bookName = document.querySelector(".book-name");
const chart = document.querySelector("#chart");
const accountSettlement = document.querySelector("#account-settlement");
const logout = document.querySelector("#logout");
const userListContent = document.querySelector(".user-list-content");
const inviteList = document.querySelector(".invite-list");
const memberList = document.querySelector(".member-list");
const inviteEmail = document.querySelector("#invite-email");

import { showNoticeWindow, closeNoticeWindow } from "./notice.js";
export { indexPage, loadPage, bookAuth, getStatus };
const socket = io();

ezlife.addEventListener("click", homePage);
home.addEventListener("click", homePage);
accountBookes.addEventListener("click", () => {
  window.location.href = `/account_book/${book.id}`;
});

function indexPage() {
  window.location.href = "/";
}

function homePage() {
  window.location.href = "/home";
}

function loadPage() {
  location.reload();
}

// 點擊 barList 顯示功能清單
document.addEventListener("click", (elem) => {
  if (elem.target.matches(".user-list")) {
    userListContent.style.display = "block";
  } else {
    userListContent.style.display = "none";
  }
});

// 點擊 成員 顯示清單
document.addEventListener("click", (elem) => {
  if (elem.target.matches(".member")) {
    memberList.style.display = "block";
  } else {
    memberList.style.display = "none";
  }
});

// 點擊 邀請 顯示清單
document.addEventListener("click", (elem) => {
  if (
    elem.target.matches(".invite") ||
    elem.target.matches(".invite-email") ||
    elem.target.matches(".invite-button")
  ) {
    inviteList.style.display = "block";
  } else {
    inviteList.style.display = "none";
    inviteEmail.value = "";
  }
});

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

// 取得帳簿權限
const book = { id: "" };
async function bookAuth(bookId) {
  book.id = bookId;
  let url = "/api/account_book_auth/" + bookId;
  let fetchData = await fetch(url, {
    method: "GET",
  });
  let jsonData = await fetchData.json();
  if (jsonData.ok) {
    getBookName(jsonData);
    getEditor(jsonData);
    return jsonData;
  } else if (jsonData.data === "請先登入會員") {
    showNoticeWindow("訊息通知", jsonData.data, indexPage);
  } else {
    showNoticeWindow("訊息通知", jsonData.data, homePage);
  }
}

// 取得會員狀態
const user = { name: "", id: "", email: "", profile: "" };
async function getStatus() {
  let url = "/api/user/auth";
  let fetchData = await fetch(url, {
    method: "GET",
  });
  let jsonData = await fetchData.json();
  if (jsonData.data !== null && jsonData.data.id) {
    user.name = jsonData.data.name;
    user.id = jsonData.data.id;
    user.email = jsonData.data.email;
    user.profile = jsonData.data.profile;
    return user;
  } else {
    showNoticeWindow("訊息通知", "請登入會員", indexPage);
  }
}

function getBookName(Data) {
  bookName.innerText = " > " + Data.data[0].book_name;
}

bookName.addEventListener("click", () => {
  window.location.href = `/account_book/${book.id}`;
});

chart.addEventListener("click", () => {
  window.location.href = `/account_book/${book.id}/chart`;
});

accountSettlement.addEventListener("click", () => {
  window.location.href = `/account_book/${book.id}/account_settlement`;
});

// 取得共同編輯
function getEditor(data) {
  const len = data.data.length;
  for (let i = 0; i < len; i++) {
    const Div = document.createElement("div");
    Div.classList.add("nav-member-group");
    memberList.appendChild(Div);
    const deleteDiv = document.createElement("div");
    deleteDiv.className = "member-delete";
    deleteDiv.id = data.data[i].id;
    deleteDiv.value = data.data[i].name;
    Div.appendChild(deleteDiv);
    const memberDiv = document.createElement("div");
    memberDiv.innerText = data.data[i].name;
    memberDiv.className = "collaborator";
    memberDiv.id = `member-${data.data[i].id}`;
    Div.appendChild(memberDiv);
    if (data.data[i].name === data.data[i].host_member) {
      const hostDiv = document.createElement("div");
      hostDiv.className = "host";
      Div.appendChild(hostDiv);
    }
  }

  // delete collaborator
  document.querySelectorAll(".member-delete").forEach((id) => {
    id.addEventListener("click", (elem) => {
      const Id = elem.target.id;
      const name = elem.target.value;
      if (parseInt(Id) === parseInt(user.id)) {
        showNoticeWindow("無法將自己刪除", "", closeNoticeWindow);
      } else {
        deletCollaborator(Id, name);
      }
    });
  });
}

async function deletCollaborator(Id, name) {
  let requestBody = { collaboratorId: Id, bookId: book.id };
  let url = "/api/collaborator";
  let fetchUrl = await fetch(url, {
    method: "DELETE",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(requestBody),
  });
  let jsonData = await fetchUrl.json();
  if (jsonData.data === "請先登入會員") {
    showNoticeWindow("請登入會員", "", indexPage);
  } else if (jsonData.data === "無刪除權限，請洽帳簿管理員") {
    showNoticeWindow("訊息通知", jsonData.data, closeNoticeWindow);
  } else {
    socket.emit("leave_room", {
      collaboratorId: Id,
      collaboratorName: name,
      roomId: book.id,
    });
  }
}

// 邀請共同編輯
document
  .querySelector("#invite-button")
  .addEventListener("click", addCollaborator);
async function addCollaborator() {
  if (!inviteEmail.validity.valid) {
    showNoticeWindow("錯誤訊息", "請確認信箱格式", closeNoticeWindow);
  } else {
    let requestBody = { email: inviteEmail.value, bookId: book.id };
    let url = "/api/collaborator";
    let fetchUrl = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(requestBody),
    });
    let jsonData = await fetchUrl.json();
    if (jsonData.ok) {
      socket.emit("add_collaborator", {
        collaboratorName: jsonData.data.name,
        roomId: book.id,
      });
    } else if (jsonData.data === "請先登入會員") {
      showNoticeWindow("請登入會員", "", indexPage);
    } else {
      showNoticeWindow("錯誤訊息", jsonData.data, closeNoticeWindow);
    }
  }
}

socket.on("connect", function () {
  socket.emit("join_room", {
    username: user.name,
    roomId: book.id,
  });
});

socket.on("leave_room_announcement", function (data) {
  showNoticeWindow(
    "訊息通知",
    `${data.collaboratorName} 已無編輯權限`,
    loadPage
  );
});

socket.on("join_room_announcement", function (data) {
  console.log(data);
});

socket.on("add_collaborator_announcement", function (data) {
  showNoticeWindow("訊息通知", `已邀請 ${data.collaboratorName}`, loadPage);
});

socket.on("add_journal_list_announcement", function (data) {
  showNoticeWindow("訊息通知", `${data.userName} 已新增一筆帳務`, loadPage);
});

socket.on("delete_journal_list_announcement", function (data) {
  showNoticeWindow("訊息通知", `${data.userName} 已刪除一筆帳務`, loadPage);
});

socket.on("checkout_announcement", function (data) {
  showNoticeWindow(
    "結算成功",
    `${data.collaboratorName} 已將 ${data.year}-${data.month}月 送出結算`,
    loadPage
  );
});

socket.on("modify_journal_list_announcement", function (data) {
  showNoticeWindow(
    "訊息通知",
    `${data.userName} 已更新了一筆帳務明細`,
    loadPage
  );
});
