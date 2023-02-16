memberInfor =
  '<div class="member-section">\
        <form class="member-group" id="member-form">\
          <div class="close-member">\
            <button class="close-member-button"></button>\
          </div>\
          <div class="profile">\
            <img class="image" id="profile" />\
            <div class="edit"></div>\
            <input type="file" name="file" id=file />\
          </div>\
          <h2 class="title">個人資料</h2>\
          <div class="member-subgroup">\
            <label class="subtitle">會員姓名</label>\
            <input type="text" name="memberName" required /><br />\
            <label class="subtitle">會員信箱</label>\
            <input\
              type="email"\
              name="memberEmail"\
              required\
              placeholder="example@example.com"\
            />\
            <br />\
            <div class="modify-message"></div>\
            <button type="submit" class="confirmToModify" id="confirmToModify">確定修改</button>\
          </div>\
        </form>\
      </div>';
document.write(memberInfor);
