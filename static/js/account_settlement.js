const settlementContainer = document.getElementById("settlement-container");
const detailContainer = document.querySelector(".detail-inner-container");
const amount = document.getElementById("amount");
const checkbox = document.querySelectorAll("[type=radio]");
const startToSettlement = document.getElementById("start-to-settlement");
const goToRecord = document.getElementById("go-to-record");
const recordZone = document.getElementById("record-zone");
const recordBoxInner = document.querySelector(".record-box-inner");
const settlementZone = document.getElementById("settlement-zone");

import { showNoticeWindow, closeNoticeWindow } from "./notice.js";
import { indexPage, bookAuth, getStatus } from "./nav.js";

const socket = io();

// 取得帳簿 id
const url = location.href;
const bookId = url.split("account_book/")[1].split("/")[0];

// 取得帳簿權限、使用者權限
const userList = document.querySelector(".user-list");
const welcomeName = document.querySelector("#welcome-name");
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
    const year = document.getElementById("year");
    const month = document.getElementById("month");
    year.value = dt_year;
    month.value = dt_month;
    getOverview(dt_year, dt_month);
  }
});

// 取得帳務資訊
const queryBoxClick = document.querySelector(".query-box-click");
queryBoxClick.addEventListener("click", () => {
  const year = document.getElementById("year").value;
  const month = document.getElementById("month").value;
  getOverview(year, month);
});

async function getOverview(year, month) {
  removeOverview();
  // 取得篩選條件
  const url = `/api/account_book/${bookId}/account_settlement?year=${year}&month=${month}`;
  const fetchData = await fetch(url, { method: "GET" });
  const jsonData = await fetchData.json();
  if (jsonData.data === "請先登入會員") {
    return showNoticeWindow("請登入會員", jsonData.data, indexPage);
  } else if (jsonData.data === "請輸入欲查詢的年度及月份") {
    return showNoticeWindow("錯誤訊息", jsonData.data, closeNoticeWindow);
  } else if (jsonData.data === "該月份無未結算項目") {
    settlementContainer.innerText = jsonData.data;
    removeJournalList();
    amount.innerText = 0;
    let itemDiv = document.createElement("div");
    itemDiv.className = "item";
    itemDiv.innerText = jsonData.data;
    detailContainer.appendChild(itemDiv);
    return;
  }

  let overview = jsonData.data.overview;
  let len = overview.length;
  for (let i = 0; i < len; i++) {
    let name = document.createElement("div");
    name.className = "name";
    name.innerText = overview[i].name;
    let group = document.createElement("div");
    group.className = "group";
    // 分攤金額
    let payableSubgroup = document.createElement("div");
    payableSubgroup.className = "subgroup";
    let payableTitle = document.createElement("div");
    payableTitle.innerText = "分攤金額";
    let payablePrice = document.createElement("div");
    payablePrice.className = "price";
    payablePrice.innerText = overview[i].payable;
    payableSubgroup.appendChild(payableTitle);
    payableSubgroup.appendChild(payablePrice);
    // 代墊金額
    let prepaidSubgroup = document.createElement("div");
    prepaidSubgroup.className = "subgroup";
    let prepaidTitle = document.createElement("div");
    prepaidTitle.innerText = "已付金額";
    let prepaidPrice = document.createElement("div");
    prepaidPrice.className = "price";
    prepaidPrice.innerText = overview[i].prepaid;
    prepaidSubgroup.appendChild(prepaidTitle);
    prepaidSubgroup.appendChild(prepaidPrice);
    // 應收／應付金額
    let subgroup = document.createElement("div");
    subgroup.className = "subgroup";
    let result = parseInt(overview[i].prepaid - overview[i].payable);
    let title = document.createElement("div");
    title.classList.add("result");
    if (result > 0) {
      title.innerText = "應收金額";
    } else {
      title.innerText = "應付金額";
    }
    let price = document.createElement("div");
    price.className = "price";
    price.classList.add("result");
    price.innerText = Math.abs(result);
    subgroup.appendChild(title);
    subgroup.appendChild(price);
    // 明細查詢鈕
    let button = document.createElement("div");
    button.className = "subgroup detail-query-button";
    button.id = overview[i].id;
    button.innerText = "明細查詢";
    group.appendChild(payableSubgroup);
    group.appendChild(prepaidSubgroup);
    group.appendChild(subgroup);
    group.appendChild(button);
    settlementContainer.appendChild(name);
    settlementContainer.appendChild(group);
  }
  // 結算鈕
  let status = jsonData.data.status;
  let checkout = document.createElement("div");
  checkout.className = "unsettlement";
  checkout.innerText = "送出結算";
  settlementContainer.appendChild(checkout);

  // 取得結帳明細
  getJournalList();

  // 取得個別明細
  const queryButton = document.querySelectorAll(".detail-query-button");
  queryButton.forEach((elem) => {
    elem.addEventListener("click", (elem) => {
      const Id = elem.target.id;
      getJournalList(Id);
    });
  });

  // 送出結算
  const checkoutButton = document.querySelector(".unsettlement");
  checkoutButton.addEventListener("click", goCheckout);
}

// 明細賬
async function getJournalList(collaborator_id = "") {
  removeJournalList();
  const year = document.getElementById("year").value;
  const month = document.getElementById("month").value;
  const url = `/api/account_book/${bookId}/account_settlement?year=${year}&month=${month}&collaborator_id=${collaborator_id}`;
  const fetchData = await fetch(url, { method: "GET" });
  const jsonData = await fetchData.json();

  // 設定支出總額
  let total = 0;

  if (jsonData.data === "請先登入會員") {
    return showNoticeWindow("請登入會員", jsonData.data, indexPage);
  } else if (jsonData.data === "請輸入欲查詢的年度及月份") {
    return showNoticeWindow("錯誤訊息", jsonData.data, closeNoticeWindow);
  } else if (jsonData.data === "該月份無未結算項目") {
    let itemDiv = document.createElement("div");
    detailContainer.appendChild(itemDiv);
    itemDiv.className = "item";
    itemDiv.innerText = jsonData.data;
    amount.innerText = total;
    return;
  }
  const journalList = jsonData.data.journal_list;
  const len = journalList.length;
  for (let i = 0; i < len; i++) {
    if (parseInt(journalList[i].price) > 0) {
      let itemDiv = document.createElement("div");
      detailContainer.appendChild(itemDiv);
      itemDiv.className = "item";
      let itemDescribeDiv = document.createElement("div");
      itemDiv.appendChild(itemDescribeDiv);
      itemDescribeDiv.className = "item-describe";
      let itemDollarDiv = document.createElement("div");
      itemDiv.appendChild(itemDollarDiv);
      itemDollarDiv.className = "item-dollar";
      itemDollarDiv.innerText = journalList[i].price;
      let categoryDiv = document.createElement("div");
      itemDescribeDiv.appendChild(categoryDiv);
      categoryDiv.className = "category";
      let keywordDiv = document.createElement("div");
      itemDescribeDiv.appendChild(keywordDiv);
      keywordDiv.className = "keyword";
      let date = journalList[i].date;
      let shortDate = date.split("-")[1] + "/" + date.split("-")[2];
      keywordDiv.innerText =
        shortDate + " （" + journalList[i].day + "） " + journalList[i].keyword;
      let mainCategoryDiv = document.createElement("div");
      categoryDiv.appendChild(mainCategoryDiv);
      mainCategoryDiv.className = "main-category";
      mainCategoryDiv.innerText = journalList[i].category_main;
      let subCategoryDiv1 = document.createElement("div");
      categoryDiv.appendChild(subCategoryDiv1);
      subCategoryDiv1.className = "sub-category";
      subCategoryDiv1.innerText = journalList[i].category_object;
      let subCategoryDiv2 = document.createElement("div");
      categoryDiv.appendChild(subCategoryDiv2);
      subCategoryDiv2.className = "sub-category";
      subCategoryDiv2.innerText = journalList[i].category_character;
      let nameCategoryDiv = document.createElement("div");
      categoryDiv.appendChild(nameCategoryDiv);
      nameCategoryDiv.className = "name-category";
      nameCategoryDiv.innerText = journalList[i].name;
      // 計算總額
      total += parseInt(journalList[i].price);
    }
  }
  amount.innerText = total;
}

function removeJournalList() {
  const items = document.querySelectorAll(".item");
  items.forEach((item) => {
    detailContainer.removeChild(item);
  });
}

function removeOverview() {
  settlementContainer.innerText = "";
  const group = document.querySelectorAll(".group");
  const name = document.querySelectorAll(".name");
  if (group & name) {
    group.forEach((item) => {
      settlementContainer.removeChild(item);
    });
    name.forEach((item) => {
      settlementContainer.removeChild(item);
    });
  }
}

// 送出結算
async function goCheckout() {
  const checkoutButton = document.querySelector(".unsettlement");
  checkoutButton.disabled = true;
  const year = document.getElementById("year").value;
  const month = document.getElementById("month").value;
  let requestBody = {
    year: year,
    month: month,
  };
  const url = `/api/account_book/${bookId}/account_settlement`;
  const fetchData = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(requestBody),
  });
  const jsonData = await fetchData.json();
  if (jsonData.data === "請先登入會員") {
    return showNoticeWindow("請登入會員", jsonData.data, indexPage);
  } else if (jsonData.data === "請輸入欲結帳年度及月份") {
    return showNoticeWindow("錯誤訊息", jsonData.data, closeNoticeWindow);
  } else if (jsonData.data === "無未結算項目") {
    return showNoticeWindow("訊息通知", jsonData.data, closeNoticeWindow);
  } else if (jsonData.ok) {
    socket.emit("sumbit_checkout", {
      collaboratorName: jsonData.data.collaborator_name,
      roomId: bookId,
      year: year,
      month: month,
    });
  }
}

// 結算紀錄／開始結算 切換
checkbox.forEach((elem) => {
  elem.addEventListener("change", (elem) => {
    if (elem.target.value === "start") {
      startToSettlement.className = "record-checked";
      goToRecord.className = "record-unchecked";
      recordZone.style.display = "none";
      settlementZone.style.display = "block";
    } else if (elem.target.value === "record") {
      goToRecord.className = "record-checked";
      startToSettlement.className = "record-unchecked";
      recordZone.style.display = "block";
      settlementZone.style.display = "none";
      getRecord();
    }
  });
});

//取得所有結算紀錄
async function getRecord() {
  revmoveRecord();
  const url = `/api/account_book/${bookId}/record`;
  const fetchData = await fetch(url, { method: "GET" });
  const jsonData = await fetchData.json();
  if (jsonData.data === "請先登入會員") {
    return showNoticeWindow("請登入會員", jsonData.data, indexPage);
  } else if (jsonData.data === "無結算紀錄") {
    let record = document.createElement("div");
    record.className = "no-record";
    record.id = "no-record";
    record.innerText = jsonData.data;
    recordBoxInner.appendChild(record);
    return;
  } else if (jsonData.ok) {
    let len = jsonData.data.length;
    for (let i = 0; i < len; i++) {
      let record = document.createElement("div");
      record.className = "record";
      recordBoxInner.appendChild(record);
      let recordDate = document.createElement("div");
      recordDate.className = "record-date";
      recordDate.innerText = jsonData.data[i].account_dt;
      let recordMember = document.createElement("div");
      recordMember.className = "record-member";
      recordMember.innerText = jsonData.data[i].account_member;
      let recordQuery = document.createElement("div");
      recordQuery.className = "record-query";
      recordQuery.id = jsonData.data[i].account_dt;
      record.appendChild(recordDate);
      record.appendChild(recordMember);
      record.appendChild(recordQuery);
    }
  }
  const recordQueryButton = document.querySelectorAll(".record-query");
  recordQueryButton.forEach((elem) => {
    elem.addEventListener("click", (elem) => {
      const Id = elem.target.id;
      recordDashboard(Id);
    });
  });
}

function revmoveRecord() {
  const noRecord = document.getElementById("no-record");
  const record = document.querySelectorAll(".record");
  if (noRecord) {
    recordBoxInner.removeChild(noRecord);
  }
  if (record) {
    record.forEach((elem) => {
      recordBoxInner.removeChild(elem);
    });
  }
}

// 取得指定的結算紀錄總覽
async function recordDashboard(dt) {
  revmoveRecordDashboard();
  const url = `/api/account_book/${bookId}/record?account_dt=${dt}`;
  const fetchData = await fetch(url, { method: "GET" });
  const jsonData = await fetchData.json();
  if (jsonData.data === "請先登入會員") {
    return showNoticeWindow("請登入會員", jsonData.data, indexPage);
  } else if (jsonData.ok) {
    let recordTitle = document.createElement("div");
    recordTitle.className = "detail-list";
    recordTitle.innerText = "結算金額總覽：" + dt;
    recordTitle.id = "record-dashboard-title";
    let container = document.createElement("div");
    container.className = "container";
    container.id = "record-container";
    let recordContainer = document.createElement("div");
    recordContainer.className = "settlement-container";
    recordZone.appendChild(recordTitle);
    recordZone.appendChild(container);
    container.appendChild(recordContainer);
    let len = jsonData.data[0].records.length;
    let records = jsonData.data[0].records;
    for (let i = 0; i < len; i++) {
      let name = document.createElement("div");
      name.className = "name";
      name.innerText = records[i].name;
      let group = document.createElement("div");
      group.className = "group";
      // 分攤金額
      let payableSubgroup = document.createElement("div");
      payableSubgroup.className = "subgroup";
      let payableTitle = document.createElement("div");
      payableTitle.innerText = "分攤金額";
      let payablePrice = document.createElement("div");
      payablePrice.className = "price";
      payablePrice.innerText = records[i].payable;
      payableSubgroup.appendChild(payableTitle);
      payableSubgroup.appendChild(payablePrice);
      // 代墊金額
      let prepaidSubgroup = document.createElement("div");
      prepaidSubgroup.className = "subgroup";
      let prepaidTitle = document.createElement("div");
      prepaidTitle.innerText = "已付金額";
      let prepaidPrice = document.createElement("div");
      prepaidPrice.className = "price";
      prepaidPrice.innerText = records[i].prepaid;
      prepaidSubgroup.appendChild(prepaidTitle);
      prepaidSubgroup.appendChild(prepaidPrice);
      // 應收／應付金額
      let subgroup = document.createElement("div");
      subgroup.className = "subgroup";
      let result = parseInt(records[i].prepaid) - parseInt(records[i].payable);
      let title = document.createElement("div");
      title.classList.add("result");
      if (result > 0) {
        title.innerText = "應收金額";
      } else {
        title.innerText = "應付金額";
      }
      let price = document.createElement("div");
      price.className = "price";
      price.classList.add("result");
      price.innerText = Math.abs(result);
      subgroup.appendChild(title);
      subgroup.appendChild(price);
      group.appendChild(payableSubgroup);
      group.appendChild(prepaidSubgroup);
      group.appendChild(subgroup);
      recordContainer.appendChild(name);
      recordContainer.appendChild(group);
    }
  }
}

function revmoveRecordDashboard() {
  const title = document.getElementById("record-dashboard-title");
  const recordContainer = document.getElementById("record-container");
  if (title && recordContainer) {
    recordZone.removeChild(title);
    recordZone.removeChild(recordContainer);
  }
}
