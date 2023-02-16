nav =
  '<nav class="nav">\
    <div class="nav-bar">\
        <div class="nav-left">\
            <div class="page-name" id="ezlife">EzLife ></div>\
            <div class="book-name"></div>\
        </div>\
        <div class="nav-right">\
            <img class="user-list"/>\
            <div class="user-list-content">\
                <div id=go-member-section>會員資料</div>\
                <div id="logout">登出系統</div>\
            </div>\
        </div>\
    </div>\
</nav>\
<nav class="nav-second">\
  <div class="nav-bar-second">\
    <div class="options" id="home-page">首頁</div>\
    <div class="options" id="account-books">帳簿</div>\
    <div class="options" id="chart">圖表</div>\
    <div class="options" id="account-settlement">結算</div>\
    <div class="options member" id="member">\
      成員\
      <div class="member-list"></div>\
    </div>\
    <div class="options invite">\
      邀請\
      <div class="invite-list">\
        <input\
          type="email"\
          placeholder="email"\
          required\
          id="invite-email"\
          class="invite-email"\
        />\
        <div id="invite-button" class="invite-button">確定</div>\
      </div>\
  </div>\
</nav>\
<div class="welcome">\
Hello，\
<span id="welcome-name"></span>\
</div>';

document.write(nav);
