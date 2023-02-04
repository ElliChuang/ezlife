const date = document.querySelector("input[type='date']");
const price = document.querySelector("input[name='price']");
const keyword = document.querySelector("input[name='keyword']");
const contentListContainer = document.querySelector(".content-list-container");
const category_main = document.querySelector("#category_main");
const category_object = document.querySelector("#category_object");
const category_character = document.querySelector("#category_character");

import { showNoticeWindow, closeNoticeWindow } from "./notice.js";
import { indexPage, loadPage, bookAuth, getStatus } from "./nav.js";

const socket = io();

// 取得帳簿 id
const url = location.href;
const bookId = url.split("account_book/")[1];

// 取得帳簿權限、使用者權限
const bookAuthCheck = bookAuth(bookId);
const userAuthCheck = getStatus();
let user = { name: "", id: "" };
bookAuthCheck.then((data) => {
  if (data === "ok") {
    userAuthCheck.then((data) => {
      user.id = data.id;
      user.name = data.name;
    });
    getData();
  }
});

async function getData() {
  let url = "/api/account_book/" + bookId;
  let fetchData = await fetch(url, {
    method: "GET",
  });
  let jsonData = await fetchData.json();
  if (jsonData.data === "請先登入會員") {
    showNoticeWindow("請登入會員", "", indexPage);
  } else if (jsonData.data.message) {
    let itemDiv = document.createElement("div");
    contentListContainer.appendChild(itemDiv);
    itemDiv.className = "item";
    itemDiv.innerText = jsonData.data.message;
  } else if (jsonData.data[0].journal_list) {
    let len = jsonData.data.length;
    let events = [];
    for (let i = 0; i < len; i++) {
      let itemDiv = document.createElement("div");
      contentListContainer.appendChild(itemDiv);
      itemDiv.className = "item";
      let itemDescribeDiv = document.createElement("div");
      itemDiv.appendChild(itemDescribeDiv);
      itemDescribeDiv.className = "item-describe";
      let itemDollarDiv = document.createElement("div");
      itemDiv.appendChild(itemDollarDiv);
      itemDollarDiv.className = "item-dollar";
      itemDollarDiv.innerText = jsonData.data[i].journal_list.price;
      let itemDeleteDiv = document.createElement("div");
      itemDiv.appendChild(itemDeleteDiv);
      itemDeleteDiv.className = "item-delete";
      itemDeleteDiv.value = jsonData.data[i].journal_list.id;
      let categoryDiv = document.createElement("div");
      itemDescribeDiv.appendChild(categoryDiv);
      categoryDiv.className = "category";
      let keywordDiv = document.createElement("div");
      itemDescribeDiv.appendChild(keywordDiv);
      keywordDiv.className = "keyword";
      let date = jsonData.data[i].journal_list.date;
      let shortDate = date.split("-")[1] + "/" + date.split("-")[2];
      keywordDiv.innerText =
        shortDate +
        " （" +
        jsonData.data[i].journal_list.day +
        "） " +
        jsonData.data[i].journal_list.keyword;
      let mainCategoryDiv = document.createElement("div");
      categoryDiv.appendChild(mainCategoryDiv);
      mainCategoryDiv.className = "main-category";
      mainCategoryDiv.innerText = jsonData.data[i].journal_list.category_main;
      let subCategoryDiv1 = document.createElement("div");
      categoryDiv.appendChild(subCategoryDiv1);
      subCategoryDiv1.className = "sub-category";
      subCategoryDiv1.innerText = jsonData.data[i].journal_list.category_object;
      let subCategoryDiv2 = document.createElement("div");
      categoryDiv.appendChild(subCategoryDiv2);
      subCategoryDiv2.className = "sub-category";
      subCategoryDiv2.innerText =
        jsonData.data[i].journal_list.category_character;
      // calendar event
      let event = {
        title: jsonData.data[i].journal_list.price + "元",
        start: jsonData.data[i].journal_list.date,
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
  category_main: "",
  category_object: "",
  category_character: "",
  keyword: "",
  price: "",
};
category_main.addEventListener("change", (elem) => {
  const value = elem.target.value;
  requestBody.category_main = value;
});

category_object.addEventListener("change", (elem) => {
  const value = elem.target.value;
  requestBody.category_object = value;
});

category_character.addEventListener("change", (elem) => {
  const value = elem.target.value;
  requestBody.category_character = value;
});

document.querySelector("#submit").addEventListener("click", addJournalList);
async function addJournalList() {
  requestBody.date = date.value;
  requestBody.keyword = keyword.value;
  requestBody.price = price.value;
  console.log(requestBody);
  if (requestBody.price === "") {
    showNoticeWindow("錯誤訊息", "請輸入金額", closeNoticeWindow);
  } else if (requestBody.date === "") {
    showNoticeWindow("錯誤訊息", "請輸入日期", closeNoticeWindow);
  } else if (
    requestBody.category_main === "" ||
    requestBody.category_object === "" ||
    requestBody.category_character === ""
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
    // contentListContainer.appendChild(itemDiv);
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
    // let keywordDiv = document.createElement("div");
    // itemDescribeDiv.appendChild(keywordDiv);
    // keywordDiv.className = "keyword";
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
    // keywordDiv.innerText =
    //   shortDate + " （" + weekday[theDay] + "） " + requestBody.keyword;
    // let mainCategoryDiv = document.createElement("div");
    // categoryDiv.appendChild(mainCategoryDiv);
    // mainCategoryDiv.className = "main-category";
    // mainCategoryDiv.innerText = requestBody.category_main;
    // let subCategoryDiv1 = document.createElement("div");
    // categoryDiv.appendChild(subCategoryDiv1);
    // subCategoryDiv1.className = "sub-category";
    // subCategoryDiv1.innerText = requestBody.category_object;
    // let subCategoryDiv2 = document.createElement("div");
    // categoryDiv.appendChild(subCategoryDiv2);
    // subCategoryDiv2.className = "sub-category";
    // subCategoryDiv2.innerText = requestBody.category_character;
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

socket.on("add_journal_list_announcement", function (data) {
  showNoticeWindow("訊息通知", `${data.userName}已新增一筆帳務`, loadPage);
});

socket.on("delete_journal_list_announcement", function (data) {
  showNoticeWindow("訊息通知", `${data.userName}已刪除一筆帳務`, loadPage);
});
