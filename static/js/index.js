const ezlife = document.querySelector("#ezlife");
const joinUs = document.querySelector(".join-us");
const loginSection = document.querySelector(".login-section");
const closeLoginButton = document.querySelector("#close-login-button");
const signUpSection = document.querySelector(".sign-up-section");
const register = document.querySelector("#register");
const closeSignUpButton = document.querySelector("#close-sign-up-button");
const goLogin = document.querySelector("#go-login");
const signUpButton = document.querySelector("#sign-up-button");
const signUpName = document.querySelector("#sign-up-name");
const signUpEmail = document.querySelector("#sign-up-email");
const signUpPassword = document.querySelector("#sign-up-password");
const signUpMessage = document.querySelector("#sign-up-message");
const loginButton = document.querySelector("#login-button");
const loginEmail = document.querySelector("#login-email");
const loginPassword = document.querySelector("#login-password");
const loginMessage = document.querySelector("#login-message");
import { showNoticeWindow, closeNoticeWindow } from "./notice.js";

ezlife.addEventListener("click", () => {
  window.location.href = "/";
});

// 取得會員狀態
getStatus();
async function getStatus() {
  let url = "/api/user/auth";
  let fetchData = await fetch(url, {
    method: "GET",
  });
  let jsonData = await fetchData.json();
  if (jsonData.data !== null && jsonData.data.id) {
    console.log(jsonData);
    homePage();
  }
}

// 登入／註冊 視窗
joinUs.addEventListener("click", showLogin);
closeLoginButton.addEventListener("click", closeLogin);
register.addEventListener("click", showSignUp);
closeLoginButton.addEventListener("click", closeLogin);
closeSignUpButton.addEventListener("click", closeSignUp);
goLogin.addEventListener("click", showLogin);

function showLogin() {
  closeSignUp();
  loginMessage.innerText = "";
  loginSection.style.display = "block";
}

function closeLogin() {
  loginSection.style.display = "none";
  loginEmail.value = "";
  loginPassword.value = "";
}

function showSignUp() {
  closeLogin();
  signUpMessage.innerText = "";
  signUpSection.style.display = "block";
}

function closeSignUp() {
  signUpSection.style.display = "none";
  signUpName.value = "";
  signUpEmail.value = "";
  signUpPassword.value = "";
}

// 註冊會員
signUpButton.addEventListener("click", memberSignUp);
async function memberSignUp() {
  if (
    !signUpName.validity.valid ||
    !signUpEmail.validity.valid ||
    !signUpPassword.validity.valid
  ) {
    signUpMessage.innerText = "請輸入姓名、電子郵件及密碼或確認格式";
  } else {
    let url = "/api/user";
    let requestBody = {
      name: signUpName.value,
      email: signUpEmail.value,
      password: signUpPassword.value,
    };
    console.log(requestBody);
    let fetchUrl = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(requestBody),
    });
    let jsonData = await fetchUrl.json();

    if (jsonData.ok) {
      console.log(jsonData);
      signUpMessage.innerText = "註冊成功";
      closeSignUp();
      showNoticeWindow("註冊成功", "請登入會員", closeNoticeWindow);
    } else {
      signUpMessage.innerText = jsonData.data;
    }
  }
}

// 會員登入
loginButton.addEventListener("click", memberLogin);
async function memberLogin() {
  if (!loginEmail.validity.valid || !loginPassword.validity.valid) {
    loginMessage.innerText = "請輸入電子郵件及密碼或確認格式";
  } else {
    let url = "/api/user/auth";
    let requestBody = {
      email: loginEmail.value,
      password: loginPassword.value,
    };
    let fetchData = await fetch(url, {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(requestBody),
    });
    let jsonData = await fetchData.json();
    console.log("會員登入:", jsonData);
    if (jsonData.ok) {
      closeLogin();
      showNoticeWindow("登入成功", "點選確定，繼續編輯帳簿", homePage);
    } else {
      loginMessage.innerText = jsonData.data;
    }
  }
}

// 重新載入頁面
function homePage() {
  window.location.href = "/home";
}
