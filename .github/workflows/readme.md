black : python 的自動排版工具
    -> black folder/

on : 什麼時候觸發
jobs : 執行哪些工作

runs-on : 在哪個環境執行
steps : 步驟

uses : 使用現成的 Action
runs : 執行 shell 命令

Checkout code : 取得程式碼
    - Github Actions 在雲端的 VM 執行，一開始是空的
    - actions/checkout : 把 repository 程式碼載到 VM 裡，後面才能存取檔案

flake8 : 程式碼格式檢查 : 縮排錯誤、行太長、多餘空白、未使用 import、語法錯誤
    - E501 : 行太長
    - W503 : 運算子放在換行的最前面