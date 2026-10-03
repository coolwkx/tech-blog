// Mermaid 初始化：把 ```mermaid 代码块渲染成图示
// GitHub 原生支持 mermaid 代码块，这个脚本让站点上的渲染效果与 GitHub 保持一致。
//
// 关于排序：本文件在 mermaid.min.js 之前被引入，所以不能在加载时直接调用
// mermaid.initialize；这里用轮询等到 CDN 脚本就绪后再初始化。
(function () {
  function initMermaid() {
    if (!window.mermaid) return false;
    mermaid.initialize({
      startOnLoad: false,
      theme: "base",
      themeVariables: {
        primaryColor: "#e8eaf6",
        primaryTextColor: "#1a1a1a",
        primaryBorderColor: "#5c6bc0",
        lineColor: "#5c6bc0",
        secondaryColor: "#f3f4f6",
        tertiaryColor: "#fafafa",
        fontFamily:
          '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
        fontSize: "14px"
      },
      flowchart: { curve: "basis", useMaxWidth: true },
      sequence: { useMaxWidth: true },
      state: { useMaxWidth: true },
      gantt: { useMaxWidth: true }
    });
    return true;
  }

  function renderMermaid() {
    if (!window.mermaid) return;
    var blocks = document.querySelectorAll(".mermaid:not([data-processed])");
    if (blocks.length === 0) return;
    try {
      mermaid.run({ nodes: blocks });
    } catch (e) {
      // 单个图语法错误不该影响整页
      console.warn("[mermaid] 渲染失败：", e);
    }
  }

  if (!initMermaid()) {
    var tries = 0;
    var timer = setInterval(function () {
      tries += 1;
      if (initMermaid()) {
        clearInterval(timer);
        renderMermaid();
      } else if (tries > 50) {
        clearInterval(timer); // 约 5 秒后放弃，不阻塞页面
        console.warn("[mermaid] CDN 未加载，图示将保持为代码块");
      }
    }, 100);
  } else {
    renderMermaid();
  }

  // Material 的 instant navigation 换页后需要重新渲染
  if (typeof document$ !== "undefined") {
    document$.subscribe(function () {
      renderMermaid();
    });
  }
})();
