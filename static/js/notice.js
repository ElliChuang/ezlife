const noticeWindowOuter = document.querySelector(".notice-window-outer");
const noticeWindow = document.querySelector(".notice-window");
const noticeTitle = document.querySelector(".notice-title");
const noticeMessage = document.querySelector(".notice-message");
const noticeButton = document.querySelector(".notice-button");
const noticeClosed = document.querySelector(".notice-closed");
export { showNoticeWindow, closeNoticeWindow };

function showNoticeWindow(elem1, elem2, elem3) {
  noticeWindowOuter.style.display = "block";
  noticeTitle.innerText = elem1;
  noticeMessage.innerText = elem2;
  noticeButton.addEventListener("click", elem3);
  noticeClosed.addEventListener("click", closeNoticeWindow);
}

function closeNoticeWindow() {
  noticeWindowOuter.style.display = "none";
  noticeTitle.innerText = "";
  noticeMessage.innerText = "";
}
