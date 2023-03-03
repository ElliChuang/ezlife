const date = document.querySelector("#input-date");
const amount = document.querySelector("#input-price");
const keyword = document.querySelector(".keyword-input");
const contentListContainer = document.querySelector(".content-list-container");
const category_main = document.querySelector("#category_main");
const category_object = document.querySelector("#category_object");
const category_character = document.querySelector("#category_character");
const userList = document.querySelector(".user-list");
const welcomeName = document.querySelector("#welcome-name");
const editZone = document.querySelector(".edit-zone");
const closeEditButton = document.querySelector(".close-edit-button");
const editCategoryMain = document.getElementById("edit-category-main");
const editCategoryObject = document.getElementById("edit-category-object");
const editCategoryCharacter = document.getElementById(
  "edit-category-character"
);
const editKeyword = document.getElementById("edit-keyword");
const editPrice = document.getElementById("edit-price");
const editDate = document.getElementById("edit-date");

import { showNoticeWindow, closeNoticeWindow } from "./notice.js";
import { indexPage, bookAuth, getStatus } from "./nav.js";

const socket = io();

// 取得帳簿 id
const url = location.href;
const bookId = url.split("account_book/")[1];

// 取得帳簿權限、使用者權限
const bookAuthCheck = bookAuth(bookId);
let user = { name: "", id: "", email: "", profile: "" };
bookAuthCheck.then((data) => {
  if (data.ok) {
    const userAuthCheck = getStatus();
    userAuthCheck.then((data) => {
      welcomeName.innerText = data.name;
      user.id = data.id;
      user.name = data.name;
      user.email = data.email;
      user.profile = data.profile;
      userList.src = user.profile;
      userList.id = user.id;
      userList.value = user.email;
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
    payableTitle.innerText = datas[i].name;
    payableTitle.id = `payableTitle-${datas[i].id}`;
    let payableInput = document.createElement("input");
    payableInput.name = "payable";
    payableInput.className = "input";
    payableInput.id = datas[i].id;
    payableSubgroup.appendChild(payableTitle);
    payableSubgroup.appendChild(payableInput);
    payableGroup.appendChild(payableSubgroup);
    // 代墊欄
    let prepaySubgroup = document.createElement("div");
    prepaySubgroup.className = "subgroup";
    let prepayTitle = document.createElement("span");
    prepayTitle.innerText = datas[i].name;
    prepayTitle.id = `prepayTitle-${datas[i].id}`;
    let prepayInput = document.createElement("input");
    prepayInput.name = "prepay";
    prepayInput.className = "input";
    prepayInput.id = datas[i].id;
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
  console.log(jsonData);
  let events = [];
  if (jsonData.data === "請先登入會員") {
    return showNoticeWindow("請登入會員", "", indexPage);
  } else if (jsonData.data === "尚無新增項目") {
    let itemDiv = document.createElement("div");
    contentListContainer.appendChild(itemDiv);
    itemDiv.className = "item";
    itemDiv.innerText = jsonData.data;
    calendar(events, year, month);
    return;
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
      itemDollarDiv.innerText = jsonData.data[i].journal_list.amount;
      itemDollarDiv.id = `${jsonData.data[i].journal_list.id}-dollar`;
      itemDollarDiv.value = jsonData.data[i].journal_list.situation;
      let itemEditDiv = document.createElement("div");
      itemContainerDiv.appendChild(itemEditDiv);
      itemEditDiv.className = "item-edit";
      itemEditDiv.value = jsonData.data[i].journal_list.id;
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
      keywordDiv.value = date.split("-")[0];
      keywordDiv.innerText =
        shortDate +
        " （" +
        jsonData.data[i].journal_list.day +
        "） " +
        jsonData.data[i].journal_list.keyword;
      keywordDiv.id = `${jsonData.data[i].journal_list.id}-keyword`;
      let mainCategoryDiv = document.createElement("div");
      categoryDiv.appendChild(mainCategoryDiv);
      mainCategoryDiv.className = "main-category";
      mainCategoryDiv.innerText = jsonData.data[i].journal_list.category_main;
      mainCategoryDiv.id = `${jsonData.data[i].journal_list.id}-mainCategory`;
      let subCategoryDiv1 = document.createElement("div");
      categoryDiv.appendChild(subCategoryDiv1);
      subCategoryDiv1.className = "sub-category";
      subCategoryDiv1.innerText = jsonData.data[i].journal_list.category_object;
      subCategoryDiv1.id = `${jsonData.data[i].journal_list.id}-objectCategory`;
      let subCategoryDiv2 = document.createElement("div");
      categoryDiv.appendChild(subCategoryDiv2);
      subCategoryDiv2.className = "sub-category";
      subCategoryDiv2.innerText =
        jsonData.data[i].journal_list.category_character;
      subCategoryDiv2.id = `${jsonData.data[i].journal_list.id}-characterCategory`;
      let itemStatusDiv = document.createElement("div");
      categoryDiv.appendChild(itemStatusDiv);
      itemStatusDiv.className = "status";
      itemStatusDiv.innerText = jsonData.data[i].journal_list.status;
      itemStatusDiv.id = `${jsonData.data[i].journal_list.id}-status`;

      // calendar event
      let eventDate = jsonData.data[i].journal_list.date;
      let eventPrice = jsonData.data[i].journal_list.amount;
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
    // edit journal list
    document.querySelectorAll(".item-edit").forEach((id) => {
      id.addEventListener("click", (elem) => {
        const Id = elem.target.value;
        showSpecificJournal(Id);
      });
    });

    calendar(events, year, month);
  }
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
  let dt = new Date(Date.parse("01" + dateValue));
  let dt_month = dt.getMonth() + 1;
  getData(bookId, year, dt_month);
}

// 新增日記帳
let requestBody = {
  date: "",
  category_main: "",
  category_object: "",
  category_character: "",
  keyword: "",
  amount: "",
  payable: [],
  prepaid: [],
};

const addButton = document.querySelector("#submit");
addButton.addEventListener("click", addJournalList);
async function addJournalList() {
  requestBody.date = date.value;
  requestBody.keyword = keyword.value.trim();
  requestBody.amount = parseInt(amount.value);
  requestBody.category_main = category_main.value;
  requestBody.category_object = category_object.value;
  requestBody.category_character = category_character.value;

  let payableAmount = 0;
  const payablePrice = document.querySelectorAll("input[name='payable']");
  payablePrice.forEach((elem) => {
    if (elem.value.trim().length === 0) {
      elem.value = 0;
    }
    payableAmount += parseInt(elem.value);
    requestBody.payable.push({ collaborator_id: elem.id, price: elem.value });
  });

  let prepaidAmount = 0;
  const prepaidPrice = document.querySelectorAll("input[name='prepay']");
  prepaidPrice.forEach((elem) => {
    if (elem.value.trim().length === 0) {
      elem.value = 0;
    }
    prepaidAmount += parseInt(elem.value);
    requestBody.prepaid.push({ collaborator_id: elem.id, price: elem.value });
  });

  if (requestBody.amount === "") {
    return showNoticeWindow("錯誤訊息", "請輸入金額", closeNoticeWindow);
  } else if (requestBody.amount <= 0) {
    return showNoticeWindow("錯誤訊息", "輸入的金額有誤", closeNoticeWindow);
  } else if (/[^\d]/g.test(requestBody.amount)) {
    return showNoticeWindow(
      "錯誤訊息",
      "輸入的金額格式有誤",
      closeNoticeWindow
    );
  } else if (requestBody.date === "") {
    return showNoticeWindow("錯誤訊息", "請輸入日期", closeNoticeWindow);
  } else if (
    requestBody.category_main === "" ||
    requestBody.category_object === "" ||
    requestBody.category_character === ""
  ) {
    return showNoticeWindow("錯誤訊息", "請選擇類別", closeNoticeWindow);
  } else if (requestBody.keyword.length > 15) {
    return showNoticeWindow(
      "錯誤訊息",
      "備註以15個字為上限",
      closeNoticeWindow
    );
  } else if (/[^\d]/g.test(payableAmount)) {
    return showNoticeWindow("錯誤訊息", "分攤金額格式有誤", closeNoticeWindow);
  } else if (requestBody.amount !== payableAmount) {
    return showNoticeWindow("錯誤訊息", "分攤金額有誤", closeNoticeWindow);
  } else if (/[^\d]/g.test(prepaidAmount)) {
    return showNoticeWindow("錯誤訊息", "代墊金額格式有誤", closeNoticeWindow);
  } else if (requestBody.amount !== prepaidAmount) {
    return showNoticeWindow("錯誤訊息", "代墊金額有誤", closeNoticeWindow);
  }
  console.log(requestBody);
  addButton.disabled = true;
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
      roomId: bookId,
    });
  } else if (jsonData.data === "欄位填寫不完整") {
    showNoticeWindow("錯誤訊息", jsonData.data, closeNoticeWindow);
  } else if (jsonData.data === "請先登入會員") {
    showNoticeWindow("請登入會員", "", indexPage);
  }
}

// 刪除明細賬
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
      roomId: bookId,
    });
  }
}

// 顯示欲修改的明細內容
async function showSpecificJournal(Id) {
  removeEdit();
  editZone.style.display = "block";
  //取得原明細帳內容
  const mainCategory = document.getElementById(`${Id}-mainCategory`).innerText;
  const objectCategory = document.getElementById(
    `${Id}-objectCategory`
  ).innerText;
  const characterCategory = document.getElementById(
    `${Id}-characterCategory`
  ).innerText;
  const dollar = document.getElementById(`${Id}-dollar`).innerText;
  const keyword = document.getElementById(`${Id}-keyword`).innerText;
  const situation = document.getElementById(`${Id}-dollar`).value;

  //填入編輯框
  const calendarDate = document.getElementById("fc-dom-1");
  let dateValue = calendarDate.innerText;
  let year = dateValue.split(" ")[1];
  let date = keyword.split("（")[0];
  let month = date.split("/")[0].trim();
  let day = date.split("/")[1].trim();
  editDate.value = `${year}-${month}-${day}`;
  editPrice.value = dollar;
  editCategoryMain.value = mainCategory;
  editCategoryObject.value = objectCategory;
  editCategoryCharacter.value = characterCategory;
  editKeyword.value = keyword.split("）")[1].trim();
  closeEditButton.name = Id;

  const payableGroup = document.getElementById("edit-payable-group");
  const prepayGroup = document.getElementById("edit-prepay-group");
  let len = situation.length;
  for (let i = 0; i < len; i++) {
    // 分攤欄
    let payableTitle = document.createElement("span");
    payableTitle.innerText = situation[i].member_name;
    payableTitle.className = "edit-payable-title";
    let payableInput = document.createElement("input");
    payableInput.value = situation[i].payable;
    payableInput.className = "edit-payable-input";
    payableInput.id = `payable-${situation[i].member_id}`;
    payableInput.name = "edit-payable";
    payableGroup.appendChild(payableTitle);
    payableGroup.appendChild(payableInput);
    // 代墊欄
    let prepayTitle = document.createElement("span");
    prepayTitle.innerText = situation[i].member_name;
    prepayTitle.className = "edit-prepay-title";
    let prepayInput = document.createElement("input");
    prepayInput.value = situation[i].prepaid;
    prepayInput.className = "edit-prepay-input";
    prepayInput.id = `prepay-${situation[i].member_id}`;
    prepayInput.name = "edit-prepay";
    prepayGroup.appendChild(prepayTitle);
    prepayGroup.appendChild(prepayInput);
  }
}

closeEditButton.addEventListener("click", () => {
  editZone.style.display = "none";
});

// 修改日記帳
const confirmToEdit = document.querySelector(".confirmToEditJournal");
confirmToEdit.addEventListener("click", editJournalList);

async function editJournalList() {
  requestBody.date = editDate.value;
  requestBody.keyword = editKeyword.value.trim();
  requestBody.amount = parseInt(editPrice.value);
  requestBody.category_main = editCategoryMain.value;
  requestBody.category_object = editCategoryObject.value;
  requestBody.category_character = editCategoryCharacter.value;
  requestBody.journal_list_id = closeEditButton.name;

  let payableAmount = 0;
  const payablePrice = document.querySelectorAll("input[name='edit-payable']");
  payablePrice.forEach((elem) => {
    if (elem.value.trim().length === 0) {
      elem.value = 0;
    }
    payableAmount += parseInt(elem.value);
    let id = elem.id.split("-")[1];
    requestBody.payable.push({ collaborator_id: id, price: elem.value });
  });

  let prepaidAmount = 0;
  const prepaidPrice = document.querySelectorAll("input[name='edit-prepay']");
  prepaidPrice.forEach((elem) => {
    if (elem.value.trim().length === 0) {
      elem.value = 0;
    }
    prepaidAmount += parseInt(elem.value);
    let id = elem.id.split("-")[1];
    requestBody.prepaid.push({ collaborator_id: id, price: elem.value });
  });

  if (requestBody.amount === "") {
    return showNoticeWindow("錯誤訊息", "請輸入金額", closeNoticeWindow);
  } else if (requestBody.amount <= 0) {
    return showNoticeWindow("錯誤訊息", "輸入的金額有誤", closeNoticeWindow);
  } else if (/[^\d]/g.test(requestBody.amount)) {
    return showNoticeWindow(
      "錯誤訊息",
      "輸入的金額格式有誤",
      closeNoticeWindow
    );
  } else if (requestBody.date === "") {
    return showNoticeWindow("錯誤訊息", "請輸入日期", closeNoticeWindow);
  } else if (
    requestBody.category_main === "" ||
    requestBody.category_object === "" ||
    requestBody.category_character === ""
  ) {
    return showNoticeWindow("錯誤訊息", "請選擇類別", closeNoticeWindow);
  } else if (requestBody.keyword.length > 15) {
    return showNoticeWindow(
      "錯誤訊息",
      "備註以15個字為上限",
      closeNoticeWindow
    );
  } else if (/[^\d]/g.test(payableAmount)) {
    return showNoticeWindow("錯誤訊息", "分攤金額格式有誤", closeNoticeWindow);
  } else if (requestBody.amount !== payableAmount) {
    return showNoticeWindow("錯誤訊息", "分攤金額有誤", closeNoticeWindow);
  } else if (/[^\d]/g.test(prepaidAmount)) {
    return showNoticeWindow("錯誤訊息", "代墊金額格式有誤", closeNoticeWindow);
  } else if (requestBody.amount !== prepaidAmount) {
    return showNoticeWindow("錯誤訊息", "代墊金額有誤", closeNoticeWindow);
  }
  console.log(requestBody);
  confirmToEdit.disabled = true;
  let url = "/api/account_book/" + bookId;
  let fetchUrl = await fetch(url, {
    method: "PATCH",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(requestBody),
  });
  let jsonData = await fetchUrl.json();
  if (jsonData.ok) {
    socket.emit("modify_journal_list", {
      userName: user.name,
      roomId: bookId,
    });
    return;
  } else if (jsonData.data === "欄位填寫不完整") {
    return showNoticeWindow("錯誤訊息", jsonData.data, closeNoticeWindow);
  } else if (jsonData.data === "請先登入會員") {
    return showNoticeWindow("請登入會員", "", indexPage);
  } else if (jsonData.data === "支出已結算，無法編輯。") {
    editZone.style.display = "none";
    return showNoticeWindow("訊息通知", jsonData.data, closeNoticeWindow);
  }
}

function removeEdit() {
  const payableGroup = document.getElementById("edit-payable-group");
  const prepayGroup = document.getElementById("edit-prepay-group");
  const payableTitle = document.querySelectorAll(".edit-payable-title");
  payableTitle.forEach((item) => {
    payableGroup.removeChild(item);
  });
  const payableInput = document.querySelectorAll(".edit-payable-input");
  payableInput.forEach((item) => {
    payableGroup.removeChild(item);
  });
  const prepayTitle = document.querySelectorAll(".edit-prepay-title");
  prepayTitle.forEach((item) => {
    prepayGroup.removeChild(item);
  });
  const prepayInput = document.querySelectorAll(".edit-prepay-input");
  prepayInput.forEach((item) => {
    prepayGroup.removeChild(item);
  });
}

// 分攤、代墊說明
const queryPayable = document.getElementById("query-payable");
const queryPrepaid = document.getElementById("query-prepaid");
const editQueryPayable = document.getElementById("edit-query-payable");
const editQueryPrepaid = document.getElementById("edit-query-prepaid");
queryPayable.addEventListener("click", () => {
  showNoticeWindow(
    "分攤金額說明",
    "分攤金額合計數＝消費金額",
    closeNoticeWindow
  );
});
queryPrepaid.addEventListener("click", () => {
  showNoticeWindow(
    "支付金額說明",
    "支付金額合計數＝消費金額",
    closeNoticeWindow
  );
});
editQueryPayable.addEventListener("click", () => {
  showNoticeWindow(
    "分攤金額說明",
    "分攤金額合計數＝消費金額",
    closeNoticeWindow
  );
});
editQueryPrepaid.addEventListener("click", () => {
  showNoticeWindow(
    "支付金額說明",
    "支付金額合計數＝消費金額",
    closeNoticeWindow
  );
});

// 預設分攤、代墊金額
let typingTimer;
const doneTypingInterval = 500;
function setDefault(elem, elem2) {
  if (elem.target.value.trim().length > 0) {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(elem2, doneTypingInterval);
  }
}

function defaultValue() {
  const prepaidPrice = document.querySelectorAll("input[name='prepay']");
  const payablePrice = document.querySelectorAll("input[name='payable']");
  prepaidPrice.forEach((elem) => {
    if (parseInt(elem.id) === user.id && parseInt(amount.value) > 0) {
      elem.value = amount.value;
    } else {
      elem.value = 0;
    }
  });
  payablePrice.forEach((elem) => {
    if (parseInt(elem.id) === user.id && parseInt(amount.value) > 0) {
      elem.value = amount.value;
    } else {
      elem.value = 0;
    }
  });
}

function editDefaultValue() {
  const editPayablePrice = document.querySelectorAll(
    "input[name='edit-payable']"
  );
  const editprepaidPrice = document.querySelectorAll(
    "input[name='edit-prepay']"
  );
  editPayablePrice.forEach((elem) => {
    let id = elem.id.split("-")[1];
    if (parseInt(id) === user.id && parseInt(editPrice.value) > 0) {
      elem.value = editPrice.value;
    } else {
      elem.value = 0;
    }
  });
  editprepaidPrice.forEach((elem) => {
    let id = elem.id.split("-")[1];
    if (parseInt(id) === user.id && parseInt(editPrice.value) > 0) {
      elem.value = editPrice.value;
    } else {
      elem.value = 0;
    }
  });
}

amount.addEventListener("keyup", (elem) => {
  setDefault(elem, defaultValue);
});

editPrice.addEventListener("keyup", (elem) => {
  setDefault(elem, editDefaultValue);
});
