const logout = document.querySelector("#logout");
const userListContent = document.querySelector(".user-list-content");
const date = document.querySelector("input[type='date']");
const price = document.querySelector("input[name='price']");
const remark = document.querySelector("input[name='remark']");
const ezlife = document.querySelector("#ezlife");
const bookName = document.querySelector(".book-name");
const contentList = document.querySelector(".content-list");
const category1 = document.querySelector("#category1");
const category2 = document.querySelector("#category2");
const category3 = document.querySelector("#category3");
const memberList = document.querySelector(".member-list");
const inviteList = document.querySelector(".invite-list");
const inviteEmail = document.querySelector("#invite-email");
const welcomeName = document.querySelector("#welcome-name");
const socket = io();
import { showNoticeWindow, closeNoticeWindow } from "./notice.js";
// export { user, bookId };

// 取得帳簿 id
const url = location.href;
const bookId = url.split("account_book/")[1];

// 取得帳簿權限
bookAuth();
async function bookAuth() {
  let url = "/api/account_book_auth/" + bookId;
  let fetchData = await fetch(url, {
    method: "GET",
  });
  let jsonData = await fetchData.json();
  console.log(jsonData);
  if (jsonData.ok) {
    closeNoticeWindow();
    getStatus();
    getEditor(jsonData);
  } else {
    showNoticeWindow("訊息通知", jsonData.data, homePage);
  }
}

// 取得會員狀態
let user = { name: "", id: "" };
async function getStatus() {
  let url = "/api/user/auth";
  let fetchData = await fetch(url, {
    method: "GET",
  });
  let jsonData = await fetchData.json();
  if (jsonData.data !== null && jsonData.data.id) {
    getBookName();
    welcomeName.innerText = jsonData.data.name;
    user.name = jsonData.data.name;
    user.id = jsonData.data.id;
  } else {
    showNoticeWindow("請登入會員", "", indexPage);
  }
}

function indexPage() {
  window.location.href = "/";
}

function homePage() {
  window.location.href = "/home";
}

ezlife.addEventListener("click", () => {
  window.location.href = "/home";
});

bookName.addEventListener("click", () => {
  window.location.href = `/account_book/${bookId}`;
});

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

// 點擊 barList 顯示功能清單
document.addEventListener("click", (elem) => {
  if (elem.target.matches(".user-list")) {
    userListContent.style.display = "block";
  } else {
    userListContent.style.display = "none";
  }
});

async function getBookName() {
  let fetchUrl = await fetch(`/api/account_book/${bookId}`);
  let jsonData = await fetchUrl.json();
  if (jsonData.data === "請先登入會員") {
    showNoticeWindow("請登入會員", "", indexPage);
  } else if (jsonData.data.book_name) {
    bookName.innerText = jsonData.data.book_name;
    let itemDiv = document.createElement("div");
    contentList.appendChild(itemDiv);
    itemDiv.className = "item";
    itemDiv.innerText = jsonData.data.message;
  } else if (jsonData.data[0].journal_list) {
    bookName.innerText = jsonData.data[0].journal_list.book_name;
    getData(jsonData);
  }
}

function getEditor(data) {
  const len = data.data.length;
  for (let i = 0; i < len; i++) {
    const Div = document.createElement("div");
    memberList.appendChild(Div);
    const deleteDiv = document.createElement("div");
    deleteDiv.className = "member-delete";
    deleteDiv.id = data.data[i].id;
    deleteDiv.value = data.data[i].name;
    Div.appendChild(deleteDiv);
    const memberDiv = document.createElement("div");
    memberDiv.innerText = data.data[i].name;
    memberDiv.className = "collaborator";
    Div.appendChild(memberDiv);
  }

  // delete collaborator
  document.querySelectorAll(".member-delete").forEach((id) => {
    id.addEventListener("click", (elem) => {
      const Id = parseInt(elem.target.id);
      const name = elem.target.value;
      console.log(Id === user.id);
      if (Id === user.id) {
        showNoticeWindow("無法將自己刪除", "", closeNoticeWindow);
      } else {
        deletCollaborator(Id, name);
      }
    });
  });
}

async function deletCollaborator(Id, name) {
  let requestBody = { collaboratorId: Id, bookId: bookId };
  console.log(requestBody);
  let url = "/api/collaborator";
  let fetchUrl = await fetch(url, {
    method: "DELETE",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(requestBody),
  });
  let jsonData = await fetchUrl.json();
  if (jsonData.data === "請先登入會員") {
    showNoticeWindow("請登入會員", "", indexPage);
  } else if (jsonData.data === "無刪除權限") {
    showNoticeWindow("訊息通知", jsonData.data, closeNoticeWindow);
  } else {
    console.log("delete");
    socket.emit("leave_room", {
      collaboratorId: Id,
      collaboratorName: name,
      roomId: bookId,
    });
  }
}

function loadPage() {
  location.reload();
}

// 點擊 成員 顯示清單
document.addEventListener("click", (elem) => {
  if (elem.target.matches(".member")) {
    memberList.style.display = "block";
  } else {
    memberList.style.display = "none";
  }
});

function getData(datas) {
  let len = datas.data.length;
  let events = [];
  for (let i = 0; i < len; i++) {
    let itemDiv = document.createElement("div");
    contentList.appendChild(itemDiv);
    itemDiv.className = "item";
    let itemDescribeDiv = document.createElement("div");
    itemDiv.appendChild(itemDescribeDiv);
    itemDescribeDiv.className = "item-describe";
    let itemDollarDiv = document.createElement("div");
    itemDiv.appendChild(itemDollarDiv);
    itemDollarDiv.className = "item-dollar";
    itemDollarDiv.innerText = datas.data[i].journal_list.price;
    let itemDeleteDiv = document.createElement("div");
    itemDiv.appendChild(itemDeleteDiv);
    itemDeleteDiv.className = "item-delete";
    itemDeleteDiv.value = datas.data[i].journal_list.id;
    let categoryDiv = document.createElement("div");
    itemDescribeDiv.appendChild(categoryDiv);
    categoryDiv.className = "category";
    let remarkDiv = document.createElement("div");
    itemDescribeDiv.appendChild(remarkDiv);
    remarkDiv.className = "remark";
    let date = datas.data[i].journal_list.date;
    let shortDate = date.split("-")[1] + "/" + date.split("-")[2];
    remarkDiv.innerText =
      shortDate +
      " （" +
      datas.data[i].journal_list.day +
      "） " +
      datas.data[i].journal_list.remark;
    let mainCategoryDiv = document.createElement("div");
    categoryDiv.appendChild(mainCategoryDiv);
    mainCategoryDiv.className = "main-category";
    mainCategoryDiv.innerText = datas.data[i].journal_list.category1;
    let subCategoryDiv1 = document.createElement("div");
    categoryDiv.appendChild(subCategoryDiv1);
    subCategoryDiv1.className = "sub-category";
    subCategoryDiv1.innerText = datas.data[i].journal_list.category2;
    let subCategoryDiv2 = document.createElement("div");
    categoryDiv.appendChild(subCategoryDiv2);
    subCategoryDiv2.className = "sub-category";
    subCategoryDiv2.innerText = datas.data[i].journal_list.category3;
    // calendar event
    let event = {
      title: datas.data[i].journal_list.price + "元",
      start: datas.data[i].journal_list.date,
    };
    events.push(event);
  }
  calendar(events);
  // delete journal list
  document.querySelectorAll(".item-delete").forEach((id) => {
    id.addEventListener("click", (elem) => {
      const Id = elem.target.value;
      deleteJournalList(Id);
    });
  });
}

// 顯示日曆
document.addEventListener("DOMContentLoaded", calendar);
function calendar(events) {
  const calendarEl = document.getElementById("calendar");
  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    navLinks: true,
    nextDayThreshold: "09:00:00",
    titleFormat: { year: "numeric", month: "long" },
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      //   right: "dayGridMonth,timeGridWeek,timeGridDay",
      right: "dayGridMonth",
    },
    events: events,
    selectable: true,
    eventColor: "#FFE4B5",
    select: function (start) {
      date.value = start.startStr;
    },
  });
  calendar.render();
}

// 新增日記帳
let requestBody = {
  date: "",
  category1: "",
  category2: "",
  category3: "",
  remark: "",
  price: "",
};
category1.addEventListener("change", (elem) => {
  const value = elem.target.value;
  requestBody.category1 = value;
});

category2.addEventListener("change", (elem) => {
  const value = elem.target.value;
  requestBody.category2 = value;
});

category3.addEventListener("change", (elem) => {
  const value = elem.target.value;
  requestBody.category3 = value;
});

document.querySelector("#submit").addEventListener("click", addJournalList);
async function addJournalList() {
  requestBody.date = date.value;
  requestBody.remark = remark.value;
  requestBody.price = price.value;
  console.log(requestBody);
  if (requestBody.price === "") {
    showNoticeWindow("錯誤訊息", "請輸入金額", closeNoticeWindow);
  } else if (requestBody.date === "") {
    showNoticeWindow("錯誤訊息", "請輸入日期", closeNoticeWindow);
  } else if (
    requestBody.category1 === "" ||
    requestBody.category2 === "" ||
    requestBody.category3 === ""
  ) {
    showNoticeWindow("錯誤訊息", "請選擇類別", closeNoticeWindow);
  }
  let url = "/api/account_book/" + bookId;
  let fetchUrl = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(requestBody),
  });
  let jsonData = await fetchUrl.json();
  if (jsonData.ok) {
    // location.reload();
    // let itemDiv = document.createElement("div");
    // contentList.appendChild(itemDiv);
    // itemDiv.className = "item";
    // let itemDescribeDiv = document.createElement("div");
    // itemDiv.appendChild(itemDescribeDiv);
    // itemDescribeDiv.className = "item-describe";
    // let itemDollarDiv = document.createElement("div");
    // itemDiv.appendChild(itemDollarDiv);
    // itemDollarDiv.className = "item-dollar";
    // itemDollarDiv.innerText = requestBody.price;
    // let itemDeleteDiv = document.createElement("div");
    // itemDiv.appendChild(itemDeleteDiv);
    // itemDeleteDiv.className = "item-delete";
    // itemDeleteDiv.value = requestBody.id;
    // let categoryDiv = document.createElement("div");
    // itemDescribeDiv.appendChild(categoryDiv);
    // categoryDiv.className = "category";
    // let remarkDiv = document.createElement("div");
    // itemDescribeDiv.appendChild(remarkDiv);
    // remarkDiv.className = "remark";
    // let date = requestBody.date;
    // let then = new Date(date);
    // let theDay = then.getDay() + 1;
    // let weekday = new Array(6);
    // weekday[1] = "Sun";
    // weekday[2] = "Mon";
    // weekday[3] = "Tue";
    // weekday[4] = "Wed";
    // weekday[5] = "Thu";
    // weekday[6] = "Fri";
    // weekday[7] = "Sat";
    // let shortDate = date.split("-")[1] + "/" + date.split("-")[2];
    // remarkDiv.innerText =
    //   shortDate + " （" + weekday[theDay] + "） " + requestBody.remark;
    // let mainCategoryDiv = document.createElement("div");
    // categoryDiv.appendChild(mainCategoryDiv);
    // mainCategoryDiv.className = "main-category";
    // mainCategoryDiv.innerText = requestBody.category1;
    // let subCategoryDiv1 = document.createElement("div");
    // categoryDiv.appendChild(subCategoryDiv1);
    // subCategoryDiv1.className = "sub-category";
    // subCategoryDiv1.innerText = requestBody.category2;
    // let subCategoryDiv2 = document.createElement("div");
    // categoryDiv.appendChild(subCategoryDiv2);
    // subCategoryDiv2.className = "sub-category";
    // subCategoryDiv2.innerText = requestBody.category3;
    socket.emit("add_journal_list", {
      userName: user.name,
    });
  } else if (jsonData.data === "欄位填寫不完整") {
    showNoticeWindow("錯誤訊息", jsonData.data, closeNoticeWindow);
  } else if (jsonData.data === "請先登入會員") {
    showNoticeWindow("請登入會員", "", indexPage);
  }
}

async function deleteJournalList(elem) {
  let requestBody = { id: elem };
  console.log(requestBody);
  let url = "/api/account_book/" + bookId;
  let fetchUrl = await fetch(url, {
    method: "DELETE",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(requestBody),
  });
  let jsonData = await fetchUrl.json();
  if (jsonData.data === "請先登入會員") {
    showNoticeWindow("請登入會員", "", indexPage);
  } else if (jsonData.ok) {
    socket.emit("delete_journal_list", {
      userName: user.name,
    });
  }
}

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

// 邀請共同編輯
document
  .querySelector("#invite-button")
  .addEventListener("click", addCollaborator);
async function addCollaborator() {
  if (!inviteEmail.validity.valid) {
    showNoticeWindow("錯誤訊息", "請確認信箱格式", closeNoticeWindow);
  } else {
    let requestBody = { email: inviteEmail.value, bookId: bookId };
    console.log(requestBody);
    let url = "/api/collaborator";
    let fetchUrl = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(requestBody),
    });
    let jsonData = await fetchUrl.json();
    if (jsonData.ok) {
      console.log(jsonData);
      socket.emit("add_collaborator", {
        collaboratorName: jsonData.data,
        roomId: bookId,
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
    roomId: bookId,
  });
  console.log("connect");
});

socket.on("join_room_announcement", function (data) {
  console.log(data);
});

socket.on("leave_room_announcement", function (data) {
  showNoticeWindow(
    "訊息通知",
    `${data.collaboratorName}已無編輯權限`,
    loadPage
  );
});

socket.on("add_collaborator_announcement", function (data) {
  showNoticeWindow("訊息通知", `已邀請${data.collaboratorName}`, loadPage);
});

socket.on("add_journal_list_announcement", function (data) {
  showNoticeWindow("訊息通知", `${data.userName}已新增一筆帳務`, loadPage);
});

socket.on("delete_journal_list_announcement", function (data) {
  showNoticeWindow("訊息通知", `${data.userName}已刪除一筆帳務`, loadPage);
});
