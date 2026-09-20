# MAYDAY 5525 BBS VJ

[播放 21 秒动画](https://ccl125.github.io/mayday-5525-bbs-vj/)

复刻「回到那一天」的复古 BBS 舞台画面。登录文字与人物字符画来自提供的 .NET 程序，M/A 与无限符号轮廓按提供的标识参考图重绘。

单文件 HTML，无网络依赖。打开 `mayday-5525-bbs-vj.html` 即可播放；空格或点击暂停/继续，左右方向键跳转，R 重播。用 `?t=21&pause` 查看最终画面。网页版播放结束后停留在最终画面；个人主页 GIF 每 21 秒循环。

## 个人主页动画

`assets/mayday-5525-21s.gif` 是供 GitHub README 显示的轻量预览。文字、人物字符画和时间轴由 `export-profile.cjs` 从播放器提取，`render-profile.py` 渲染为 GIF，字体和光晕与浏览器版本略有区别。

macOS 上安装 Node.js 和 uv 后，可重新导出：

```sh
uv run --with pillow python render-profile.py
```

导出器会验证总时长为 21,000 毫秒。GitHub Pages 从 `main` 分支根目录发布，`index.html` 跳转到播放器。
