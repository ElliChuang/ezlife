const memberSection = document.querySelector(".member-section");
const memberName = document.querySelector("[name = memberName]");
const memberEmail = document.querySelector("[name = memberEmail]");
const modifyMessage = document.querySelector(".modify-message");
const profile = document.querySelector("#profile");
const userList = document.querySelector(".user-list");
const welcomeName = document.querySelector("#welcome-name");

export { showMemberSection, closeMemberSection, changeFile, modifyInfor };

// 點擊 會員資料 顯示會員專區
const goMemberSection = document.querySelector("#go-member-section");
goMemberSection.addEventListener("click", showMemberSection);
function showMemberSection() {
  memberSection.style.display = "block";
  modifyMessage.innerText = "";
  memberName.value = welcomeName.innerText;
  memberEmail.value = userList.value;
  profile.src = userList.src;
}

const closeMemberButton = document.querySelector(".close-member-button");
closeMemberButton.addEventListener("click", closeMemberSection);
function closeMemberSection(event) {
  event.preventDefault();
  memberSection.style.display = "none";
}

// 預覽圖片
const file = document.querySelector("#file");
file.addEventListener("change", changeFile);
function changeFile(elem) {
  let file = elem.target.files[0];
  if (!file) {
    return;
  }
  if (
    file.type === "image/jpeg" ||
    file.type === "image/jpg" ||
    file.type === "image/png"
  ) {
    modifyMessage.innerText = "";
    let reader = new FileReader();
    reader.onload = function (e) {
      profile.src = e.target.result;
    };
    reader.readAsDataURL(file);
  } else {
    return (modifyMessage.innerText = "請確認圖片格式為png、jpg、jpeg");
  }
}

// 會員資料修改
const memberForm = document.getElementById("member-form");
memberForm.addEventListener("submit", modifyInfor);

async function modifyInfor(event) {
  event.preventDefault();
  const formData = new FormData();
  if (file.files.length === 0) {
    formData.append("file", null);
    formData.append("memberId", userList.id);
    formData.append("memberName", memberName.value);
    formData.append("memberEmail", memberEmail.value);
    formData.append("profile", userList.src);
  } else {
    formData.append("file", file.files[0]);
    formData.append("memberId", userList.id);
    formData.append("memberName", memberName.value);
    formData.append("memberEmail", memberEmail.value);
  }

  if (memberName.value.trim().length === 0) {
    return (modifyMessage.innerText = "會員姓名不得空白");
  }
  if (!memberEmail.validity.valid) {
    return (modifyMessage.innerText = "請輸入有效的電子信箱");
  }

  const confirmToModify = document.getElementById("confirmToModify");
  confirmToModify.disabled = true;
  modifyMessage.innerText = "";
  let fetchUrl = await fetch("/api/user/auth", {
    method: "PATCH",
    body: formData,
  });

  let jsonData = await fetchUrl.json();
  if (jsonData.ok) {
    modifyMessage.innerText = "資料更新成功";
    let user = { id: "", name: "", email: "", profile: "" };
    user.id = jsonData.data.id;
    user.name = jsonData.data.name;
    user.email = jsonData.data.email;
    user.profile = jsonData.data.profile;

    // 依所在頁面更新畫面資訊
    userList.src = user.profile;
    userList.value = user.email;
    welcomeName.innerText = user.name;
    const payableTitle = document.getElementById(`payableTitle-${user.id}`);
    const prepayTitle = document.getElementById(`prepayTitle-${user.id}`);
    if (payableTitle && prepayTitle) {
      payableTitle.innerText = user.name;
      prepayTitle.innerText = user.name;
    }
  } else {
    modifyMessage.innerText = jsonData.data;
  }
  confirmToModify.disabled = false;
}
