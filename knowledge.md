# 黃啟嘉職務交接事項

## 負責專案總覽
- 行銷資料整合 (Iterable、MailJet、Klaviyo)
- TTD (The Trade Desk)
- SkyLens
- 司機帳務系統

---

## A. 行銷資料整合 (Iterable、MailJet、Klaviyo)

### 行銷負責總覽:
1.  更新資料至 Iterable 平台。
2.  更新不聯繫清單至 Iterable、Klaviyo、MailJet 等平台。
3.  幫忙解決User使用行銷小工具問題。

### Iterable例行維護與執行事項:
1.  每日上傳活躍用戶至 Iterable 平台。
2.  每週將其餘約一百二十萬用戶同步至Iterable平台。
3.  每日同步並維護不聯繫清單 (do-not-contact list) 至 Iterable平台。
4.  修正資料庫中型別錯誤的欄位、修正名稱與錯誤資料。
5.  定期清理資料庫，確保容量不超過免費額度限制。
6.  定期找出並清除無效 Email 會員，以節省平台人頭費用。
7.  定期找出註冊時錯填的 Email 並修正，以增加行銷觸及率。
### Klaviyo例行維護與執行事項:
1.  每日同步並維護不聯繫清單 (do-not-contact list) 至 Klaviyo平台。
2.  排程程式部屬於hangfire上，`https://iterable-prod.azurewebsites.net/hangfire/recurring`，確認Last execution執行標籤顯示綠色則正常。
### MailJet例行維護與執行事項:
1.  每日同步並維護不聯繫清單 (do-not-contact list) 至 MailJet平台。
2.  排程程式部屬於hangfire上，`https://iterable-prod.azurewebsites.net/hangfire/recurring`，確認Last execution執行標籤顯示綠色則正常。

---

## B. TTD (The Trade Desk)

### 例行維護與執行事項
1.  例行更新 ThirdPartyData 標籤、上傳新會員以取得 UID2、上傳本次受眾包標籤與例行更新 BucketId。
2.  更新 `PercentOfMediaCostRate` 與 `Amount` 欄位的數值，並同步更新上架欄位與價格，與 TTD 人員聯絡協調進度。
3.  上傳受眾包後，產出比對率報表與費率報表。
4.  資料清理：找出無效 Email 清單並更正，重新上傳以提高比對率。

---

## C. SkyLens

### 例行維護與執行事項
- 每日更新排程：`MobPlace`、`MobProfile`
- 每月更新排程：`HostIds`
- 依照需求更新 `MobTop100`

---

## D. 移動財務-司機帳務系統

### 例行維運作業
1.  資料庫維護，協助使用者回答疑問、解決資料錯誤或上傳錯誤問題。
2.  系統帳號權限維護: 移動人員新入職或離職權限新增或刪除。
3.  定期向移動請款並取得發票回傳。

### 新版司機帳務系統開發協助
1.  建立測試資料與 UAT (User Acceptance Testing) 環境，協助廠商測試。
2.  釐清舊系統資料流邏輯，並將各項功能從 C# 轉譯成 SQL 程式碼，提供給廠商進行開發與測試。
3.  協助回覆新系統開發廠商的測試問題或資料流問題。
4.  匯入並製作測試資料與情境供移動新版上線前測試比對。
