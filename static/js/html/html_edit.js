editInfor =
  '<div class="edit-zone">\
        <div class="edit-group">\
          <div class="close-edit">\
              <button class="close-edit-button"></button>\
            </div>\
          <div class=edit-section>\
            <section >\
              <div class="name">消費明細</div>\
              <div class="edit-detail">\
                <span>金額</span><input type="text" name="price" id="edit-price" /><br />\
                <span>日期</span><input type="date" id="edit-date"  /><br />\
                <span>生活機能</span>\
                <select size="1" id="edit-category-main">\
                  <option>食</option>\
                  <option>衣</option>\
                  <option>住</option>\
                  <option>行</option>\
                  <option>育</option>\
                  <option>樂</option></select\
                ><br />\
                <span>消費型態</span>\
                <select size="1" id="edit-category-object">\
                  <option>食品</option>\
                  <option>日常用品</option>\
                  <option>水電</option>\
                  <option>瓦斯</option>\
                  <option>網路</option>\
                  <option>電信</option>\
                  <option>管理費</option>\
                  <option>維修</option>\
                  <option>保養</option>\
                  <option>房租</option>\
                  <option>房貸</option>\
                  <option>車貸</option>\
                  <option>油資</option>\
                  <option>停車</option>\
                  <option>美妝保養</option>\
                  <option>服裝</option>\
                  <option>設備</option>\
                  <option>學習</option>\
                  <option>運動</option>\
                  <option>娛樂</option>\
                  <option>交際費</option>\
                  <option>理財</option>\
                  <option>醫療</option>\
                  <option>保健</option>\
                  <option>保險</option>\
                  <option>其他</option></select\
                ><br />\
                <span>支出對象</span>\
                <select size="1" id="edit-category-character">\
                  <option>個人</option>\
                  <option>家庭</option>\
                  <option>育兒</option>\
                  <option>寵物</option>\
                  <option>宿舍</option>\
                  <option>旅行</option></select\
                ><br />\
                <span>備註說明</span\
                ><input type="text" name="keyword" class="keyword-input" id="edit-keyword" />\
                <ul class="keyword-ul"></ul>\
              </div>\
            </section>\
            <section class="edit-price-setting">\
              <div class="name">分攤金額</div>\
              <div class="edit-price-setting-group" id="edit-payable-group">\
              </div>\
              <div class="name">代墊金額</div>\
              <div class="edit-price-setting-group" id="edit-prepay-group">\
              </div>\
            </section>\
          </div>\
          <button type="button" class="confirmToEditJournal">確定修改</button>\
        </div>\
      </section>\
      </div>\
      </div>';
document.write(editInfor);
