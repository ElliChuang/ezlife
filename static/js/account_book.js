const date = document.querySelector("input[type='date']");
const price = document.querySelector("input[name='price']");
const keyword = document.querySelector("input[name='keyword']");
const contentListContainer = document.querySelector(".content-list-container");
const category_main = document.querySelector("#category_main");
const category_object = document.querySelector("#category_object");
const category_character = document.querySelector("#category_character");

import { showNoticeWindow, closeNoticeWindow } from "./notice.js";
import { indexPage, bookAuth, getStatus } from "./nav.js";

const socket = io();

// 取得帳簿 id
const url = location.href;
const bookId = url.split("account_book/")[1];

// 取得帳簿權限、使用者權限
const bookAuthCheck = bookAuth(bookId);
let user = { name: "", id: "" };
bookAuthCheck.then((data) => {
  if (data.ok) {
    const userAuthCheck = getStatus();
    userAuthCheck.then((data) => {
      user.id = data.id;
      user.name = data.name;
    });
    let dt = new Date();
    let dt_year = dt.getFullYear();
    let dt_month = dt.getMonth() + 1;
    getData(bookId, dt_year, dt_month);
    setObject(data.data);
  }
});

function setObject(datas) {
  let len = datas.length;
  const payableGroup = document.getElementById("payable-group");
  const prepayGroup = document.getElementById("prepay-group");
  for (let i = 0; i < len; i++) {
    // 分攤欄
    let payableSubgroup = document.createElement("div");
    payableSubgroup.className = "subgroup";
    let payableTitle = document.createElement("span");
    payableTitle.className = "title";
    payableTitle.innerText = datas[i].name;
    let payableInput = document.createElement("input");
    payableInput.name = "payable";
    payableInput.id = datas[i].id;
    payableSubgroup.appendChild(payableTitle);
    payableSubgroup.appendChild(payableInput);
    payableGroup.appendChild(payableSubgroup);
    // 代墊欄
    let prepaySubgroup = document.createElement("div");
    prepaySubgroup.className = "subgroup";
    let prepayTitle = document.createElement("span");
    prepayTitle.className = "title";
    prepayTitle.innerText = datas[i].name;
    let prepayInput = document.createElement("input");
    prepayInput.name = "prepay";
    prepayInput.id = datas[i].id;
    // prepayInput.name = datas[i].name;
    prepaySubgroup.appendChild(prepayTitle);
    prepaySubgroup.appendChild(prepayInput);
    prepayGroup.appendChild(prepaySubgroup);
  }
}

async function getData(bookId, year, month) {
  removeJournalList();
  let url = `/api/account_book/${bookId}?year=${year}&month=${month}`;
  let fetchData = await fetch(url, {
    method: "GET",
  });
  let jsonData = await fetchData.json();
  let events = [];
  if (jsonData.data === "請先登入會員") {
    return showNoticeWindow("請登入會員", "", indexPage);
  } else if (jsonData.data.message) {
    let itemDiv = document.createElement("div");
    contentListContainer.appendChild(itemDiv);
    itemDiv.className = "item";
    itemDiv.innerText = jsonData.data.message;
  } else if (jsonData.data[0].journal_list) {
    let len = jsonData.data.length;
    let dict = {};
    for (let i = 0; i < len; i++) {
      let itemDiv = document.createElement("div");
      contentListContainer.appendChild(itemDiv);
      itemDiv.className = "item";
      let itemDescribeDiv = document.createElement("div");
      itemDiv.appendChild(itemDescribeDiv);
      itemDescribeDiv.className = "item-describe";
      let itemContainerDiv = document.createElement("div");
      itemDiv.appendChild(itemContainerDiv);
      itemContainerDiv.className = "item-container";
      let itemDollarDiv = document.createElement("div");
      itemContainerDiv.appendChild(itemDollarDiv);
      itemDollarDiv.className = "item-dollar";
      itemDollarDiv.innerText = jsonData.data[i].journal_list.price;
      let itemDeleteDiv = document.createElement("div");
      itemContainerDiv.appendChild(itemDeleteDiv);
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
      let itemStatusDiv = document.createElement("div");
      categoryDiv.appendChild(itemStatusDiv);
      itemStatusDiv.className = "status";
      itemStatusDiv.innerText = jsonData.data[i].journal_list.status;

      // calendar event
      let eventDate = jsonData.data[i].journal_list.date;
      let eventPrice = jsonData.data[i].journal_list.price;
      if (eventDate in dict) {
        dict[eventDate] = dict[eventDate] + parseInt(eventPrice);
      } else {
        dict[eventDate] = parseInt(eventPrice);
      }
    }

    for (const [key, value] of Object.entries(dict)) {
      events.push({
        title: value + "元",
        start: key,
      });
    }

    // delete journal list
    document.querySelectorAll(".item-delete").forEach((id) => {
      id.addEventListener("click", (elem) => {
        const Id = elem.target.value;
        deleteJournalList(Id);
      });
    });
  }
  calendar(events, year, month);
}

function removeJournalList() {
  const contentListContainer = document.querySelector(
    ".content-list-container"
  );
  const items = document.querySelectorAll(".item");
  items.forEach((item) => {
    contentListContainer.removeChild(item);
  });
}

// 顯示日曆
function calendar(events, year, month) {
  const calendarEl = document.getElementById("calendar");
  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    navLinks: false,
    nextDayThreshold: "09:00:00",
    titleFormat: { year: "numeric", month: "long" },
    headerToolbar: {
      left: "prev,next",
      center: "title",
      right: "today",
    },
    initialDate: new Date(year, month - 1, 1),
    events: events,
    selectable: true,
    eventColor: "#FFE4B5",
    select: function (start) {
      date.value = start.startStr;
    },
  });
  calendar.render();
  const toolBar = document.querySelector(".fc-button-group");
  const today = document.querySelector(".fc-today-button");
  toolBar.addEventListener("click", getCalendarDate);
  today.addEventListener("click", getCalendarDate);
}

// 取得當前日曆年月
function getCalendarDate() {
  const calendarDate = document.getElementById("fc-dom-1");
  let dateValue = calendarDate.innerText;
  let year = dateValue.split(" ")[1];
  let dt = new Date(dateValue);
  let dt_month = dt.getMonth();
  let month = new Array(12);
  month[0] = "1";
  month[1] = "2";
  month[2] = "3";
  month[3] = "4";
  month[4] = "5";
  month[5] = "6";
  month[6] = "7";
  month[7] = "8";
  month[8] = "9";
  month[9] = "10";
  month[10] = "11";
  month[11] = "12";
  getData(bookId, year, month[dt_month]);
}

// 新增日記帳
let requestBody = {
  date: "",
  category_main: "",
  category_object: "",
  category_character: "",
  keyword: "",
  price: "",
  payable: [],
  prepaid: [],
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
  requestBody.price = parseInt(price.value);

  let payableAmount = 0;
  const payablePrice = document.querySelectorAll("input[name='payable']");
  payablePrice.forEach((elem) => {
    payableAmount += parseInt(elem.value);
    requestBody.payable.push({ collaborator_id: elem.id, price: elem.value });
  });

  let prepaidAmount = 0;
  const prepaidPrice = document.querySelectorAll("input[name='prepay']");
  prepaidPrice.forEach((elem) => {
    prepaidAmount += parseInt(elem.value);
    requestBody.prepaid.push({ collaborator_id: elem.id, price: elem.value });
  });

  if (requestBody.price === "") {
    return showNoticeWindow("錯誤訊息", "請輸入金額", closeNoticeWindow);
  } else if (requestBody.date === "") {
    return showNoticeWindow("錯誤訊息", "請輸入日期", closeNoticeWindow);
  } else if (
    requestBody.category_main === "" ||
    requestBody.category_object === "" ||
    requestBody.category_character === ""
  ) {
    return showNoticeWindow("錯誤訊息", "請選擇類別", closeNoticeWindow);
  } else if (requestBody.price !== payableAmount) {
    return showNoticeWindow("錯誤訊息", "分攤金額有誤", closeNoticeWindow);
  } else if (requestBody.price !== prepaidAmount) {
    return showNoticeWindow("錯誤訊息", "代墊金額有誤", closeNoticeWindow);
  }
  console.log(requestBody);
  let url = "/api/account_book/" + bookId;
  let fetchUrl = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(requestBody),
  });
  let jsonData = await fetchUrl.json();
  if (jsonData.ok) {
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
  let url = "/api/account_book/" + bookId;
  let fetchUrl = await fetch(url, {
    method: "DELETE",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(requestBody),
  });
  let jsonData = await fetchUrl.json();
  if (jsonData.data === "請先登入會員") {
    return showNoticeWindow("請登入會員", "", indexPage);
  } else if (jsonData.data === "支出已結算，無法刪除。") {
    return showNoticeWindow("訊息通知", jsonData.data, closeNoticeWindow);
  } else if (jsonData.ok) {
    socket.emit("delete_journal_list", {
      userName: user.name,
    });
  }
}
