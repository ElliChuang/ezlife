import { showNoticeWindow, closeNoticeWindow } from "./notice.js";
import { indexPage, bookAuth, getStatus } from "./nav.js";

// 取得帳簿 id
const url = location.href;
const bookId = url.split("account_book/")[1].split("/")[0];

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
    console.log("Let's start");
  }
});

// 取得帳務資訊
let mainDatas = "";
let characterDatas = "";
const mainColor = [
  "rgb(255, 230, 230)",
  "rgb(217, 230, 242)",
  "rgb(217, 217, 242)",
  "rgb(194, 194, 163, 0.7)",
  "rgb(223, 191, 159)",
  "rgb(255, 221, 179)",
];
const characterColor = [
  "rgb(255, 221, 179)",
  "rgb(223, 191, 159)",
  "rgb(194, 194, 163, 0.7)",
  "rgb(217, 217, 242)",
  "rgb(217, 230, 242)",
  "rgb(255, 230, 230)",
];
const checkbox = document.querySelectorAll("[type=radio]");
const main = document.getElementById("main");
const character = document.getElementById("character");
const queryBoxButton = document.querySelector(".chart-query-box-button");

queryBoxButton.addEventListener("click", getData);

async function getData() {
  // 取得篩選條件
  const year = document.getElementById("year").value;
  const month = document.getElementById("month").value;
  const categoryMain = document.getElementById("category_main").value;
  const categoryCharacter = document.getElementById("category_character").value;
  const categoryObject = document.getElementById("category_object").value;
  const keyword = document.getElementById("keyword").value;

  const url = `/api/account_book/${bookId}/chart?year=${year}&month=${month}&main=${categoryMain}&character=${categoryCharacter}&object=${categoryObject}&keyword=${keyword}`;
  const fetchData = await fetch(url, { method: "GET" });
  const jsonData = await fetchData.json();

  if (jsonData.data === "請先登入會員") {
    showNoticeWindow("請登入會員", "", indexPage);
  } else if (jsonData.data === "請輸入欲查詢的年度及月份") {
    showNoticeWindow("錯誤訊息", "", closeNoticeWindow);
  } else {
    const journalList = jsonData.journal_list;
    getJournalList(journalList);

    const chartMain = jsonData.chart_main;
    const chartCharacter = jsonData.chart_character;
    mainDatas = chartMain;
    characterDatas = chartCharacter;

    checkbox.forEach((elem) => {
      if (elem.checked && elem.value === "main") {
        main.className = "chart-main-span-checked";
        character.className = "chart-main-span-unchecked";
        getChart(mainDatas, mainColor);
      } else if (elem.checked && elem.value === "character") {
        character.className = "chart-main-span-checked";
        main.className = "chart-main-span-unchecked";
        getChart(characterDatas, characterColor);
      }
    });
  }
}

// 圓餅圖
checkbox.forEach((elem) => {
  elem.addEventListener("change", (elem) => {
    if (elem.target.value === "main") {
      main.className = "chart-main-span-checked";
      character.className = "chart-main-span-unchecked";
      getChart(mainDatas, mainColor);
    } else if (elem.target.value === "character") {
      character.className = "chart-main-span-checked";
      main.className = "chart-main-span-unchecked";
      getChart(characterDatas, characterColor);
    }
  });
});

function getChart(datas, color) {
  removeChart();
  const currentChart = document.getElementById("current-chart");
  const canvas = document.createElement("canvas");
  currentChart.appendChild(canvas);
  canvas.id = `myChart`;
  const ctx = document.getElementById(`myChart`);

  new Chart(ctx, {
    type: "pie",
    data: {
      labels: Object.keys(datas),
      datasets: [
        {
          data: Object.values(datas),
          backgroundColor: color,
          hoverOffset: 4,
        },
      ],
    },
    plugins: [ChartDataLabels],
    options: {
      plugins: {
        legend: {
          labels: {
            font: {
              size: 20,
            },
          },
        },
        tooltip: {
          titleAlign: "center",
          titleFont: {
            size: 18,
          },
          bodyFont: {
            size: 18,
          },
          boxPadding: 5,
        },
        datalabels: {
          formatter: function (value, context) {
            const datapoints = context.chart.data.datasets[0].data;
            function sum(total, datapoint) {
              return total + datapoint;
            }
            const totalValue = datapoints.reduce(sum, 0);
            const percentageValue = ((value / totalValue) * 100).toFixed(1);
            if (value == 0) {
              return "";
            }
            return `${percentageValue} %`;
          },
          labels: {
            value: {
              color: "black",
              font: {
                size: 18,
                weight: "bold",
              },
            },
          },
        },
      },

      layout: {
        padding: {
          bottom: 40,
          top: 40,
        },
      },
      maintainAspectRatio: false,
    },
  });
}

function removeChart() {
  const currentChart = document.getElementById("current-chart");
  const ctx = document.getElementById(`myChart`);
  currentChart.removeChild(ctx);
}

// 明細賬
function getJournalList(datas) {
  removeJournalList();
  if (datas === "查無帳目明細") {
    const category_main = { 食: 0, 衣: 0, 住: 0, 行: 0, 育: 0, 樂: 0 };
    Object.entries(category_main).forEach(([key, value]) => {
      const subtotal = document.getElementById(`subtotal-${key}`);
      subtotal.innerText = value;
    });

    const total = document.getElementById("total");
    total.innerText = 0;

    const journalListContainer = document.querySelector(
      ".current-journal-list-container"
    );
    let itemDiv = document.createElement("div");
    journalListContainer.appendChild(itemDiv);
    itemDiv.className = "item";
    itemDiv.innerText = datas;
    return;
  }

  const category_main = datas.category_main;
  Object.entries(category_main).forEach(([key, value]) => {
    const subtotal = document.getElementById(`subtotal-${key}`);
    subtotal.innerText = value;
  });

  const total = document.getElementById("total");
  total.innerText = datas.amount;

  const len = datas.data.length;
  for (let i = 0; i < len; i++) {
    const journalListContainer = document.querySelector(
      ".current-journal-list-container"
    );
    let itemDiv = document.createElement("div");
    journalListContainer.appendChild(itemDiv);
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
    let keywordDiv = document.createElement("div");
    itemDescribeDiv.appendChild(keywordDiv);
    keywordDiv.className = "keyword";
    let date = datas.data[i].journal_list.date;
    let shortDate = date.split("-")[1] + "/" + date.split("-")[2];
    keywordDiv.innerText =
      shortDate +
      " （" +
      datas.data[i].journal_list.day +
      "） " +
      datas.data[i].journal_list.keyword;
    let mainCategoryDiv = document.createElement("div");
    categoryDiv.appendChild(mainCategoryDiv);
    mainCategoryDiv.className = "main-category";
    mainCategoryDiv.innerText = datas.data[i].journal_list.category_main;
    let subCategoryDiv1 = document.createElement("div");
    categoryDiv.appendChild(subCategoryDiv1);
    subCategoryDiv1.className = "sub-category";
    subCategoryDiv1.innerText = datas.data[i].journal_list.category_object;
    let subCategoryDiv2 = document.createElement("div");
    categoryDiv.appendChild(subCategoryDiv2);
    subCategoryDiv2.className = "sub-category";
    subCategoryDiv2.innerText = datas.data[i].journal_list.category_character;
  }
}

function removeJournalList() {
  const journalListContainer = document.querySelector(
    ".current-journal-list-container"
  );
  const items = document.querySelectorAll(".item");
  items.forEach((item) => {
    journalListContainer.removeChild(item);
  });
}

// 下載 csv file
const download = document.getElementById("download");
download.addEventListener("click", getFile);

async function getFile() {
  // 取得篩選條件
  const year = document.getElementById("year").value;
  const month = document.getElementById("month").value;
  const categoryMain = document.getElementById("category_main").value;
  const categoryCharacter = document.getElementById("category_character").value;
  const categoryObject = document.getElementById("category_object").value;
  const keyword = document.getElementById("keyword").value;

  const url = `/api/account_book/${bookId}/csv_file?year=${year}&month=${month}&main=${categoryMain}&character=${categoryCharacter}&object=${categoryObject}&keyword=${keyword}`;
  const fetchData = await fetch(url);
  if (fetchData.status === 403) {
    const jsonData = await fetchData.json();
    if (jsonData.data === "請先登入會員") {
      return showNoticeWindow("請登入會員", jsonData.data, indexPage);
    }
    if (jsonData.data === "請輸入欲查詢的年度及月份") {
      return showNoticeWindow("錯誤訊息", jsonData.data, closeNoticeWindow);
    }
  }

  const blobData = await fetchData.blob();
  const fileUrl = window.URL.createObjectURL(blobData);
  const a = document.createElement("a");
  a.style.display = "none";
  a.href = fileUrl;
  a.download = `${year}_${month}月.csv`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(fileUrl);
}
