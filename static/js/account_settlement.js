const container = document.querySelector(".settlement-container");
const detailContainer = document.querySelector(".detail-inner-container");
const amount = document.getElementById("amount");

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
    getOverview();
    console.log("Let's start");
  }
});

// 取得帳務資訊
const queryBoxClick = document.querySelector(".query-box-click");
queryBoxClick.addEventListener("click", getOverview);

async function getOverview() {
  removeOverview();
  // 取得篩選條件
  const year = document.getElementById("year").value;
  const month = document.getElementById("month").value;
  const url = `/api/account_book/${bookId}/account_settlement?year=${year}&month=${month}`;
  const fetchData = await fetch(url, { method: "GET" });
  const jsonData = await fetchData.json();
  console.log(jsonData);
  if (jsonData.data === "請先登入會員") {
    return showNoticeWindow("請登入會員", jsonData.data, indexPage);
  } else if (jsonData.data === "請輸入欲查詢的年度及月份") {
    return showNoticeWindow("錯誤訊息", jsonData.data, closeNoticeWindow);
  } else if (jsonData.data === "該月份無未結算項目") {
    container.innerText = jsonData.data;
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
    prepaidTitle.innerText = "墊付金額";
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
    if (result > 0) {
      title.innerText = "應收金額";
    } else {
      title.innerText = "應付金額";
    }
    let price = document.createElement("div");
    price.className = "price";
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
    container.appendChild(name);
    container.appendChild(group);
  }
  // 結算鈕
  let status = jsonData.data.status;
  let checkout = document.createElement("div");
  checkout.className = "unsettlement";
  checkout.innerText = "送出結算";
  container.appendChild(checkout);

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
  container.innerText = "";
  const group = document.querySelectorAll(".group");
  group.forEach((item) => {
    container.removeChild(item);
  });
  const name = document.querySelectorAll(".name");
  name.forEach((item) => {
    container.removeChild(item);
  });
  const settlement = document.querySelectorAll(".settlement");
  settlement.forEach((item) => {
    container.removeChild(item);
  });
}

// 送出結算
async function goCheckout() {
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
  console.log(jsonData);
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
