# Manual UI Layout Update

要手動把瀏覽器調整後的 layout 套回 VS Code，改的是這個檔案：

- [urban-legend-framework/index.html](D:/ELY/作品相關/###小遊戲製作GIT/都市傳說/都市傳說2/都市傳說2/urban-legend-framework/index.html)

## 要替換哪一段

在 VS Code 裡搜尋：

```js
const UI_LAYOUT_DEFAULTS=
```

你會找到一整大段：

```js
const UI_LAYOUT_DEFAULTS={
  ...
};
```

手動替換時：

1. 從 `const UI_LAYOUT_DEFAULTS={` 這一行開始選。
2. 一直選到這段結尾的 `};`。
3. 用新的整段內容完整覆蓋。

不要只貼 `desktop` 或 `mobile` 裡面的某一小塊，必須整段一起換掉。

## 瀏覽器裡怎麼拿到新內容

1. 進遊戲後按 `Shift+P` 進入 admin layout mode。
2. 調整完後按右上 `Export Layout`。
3. 複製跳出視窗裡的整段 `const UI_LAYOUT_DEFAULTS=...`。
4. 回到 VS Code，把 `index.html` 內原本那一整段取代掉。

## 替換完之後要做什麼

1. 存檔。
2. 重新整理遊戲頁面。
3. 如果畫面還像舊版，請硬重新整理：

```text
Ctrl + Shift + R
```

## 快速確認

替換成功後，`index.html` 裡應該還是只有一個：

```js
const UI_LAYOUT_DEFAULTS=
```

不要留下兩份，不然前後會互相覆蓋。
