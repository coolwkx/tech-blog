// MathJax 配置 + 多 CDN 自动回退加载
//
// 背景：pymdownx.arithmatex 会把 $...$ 包成 <span class="arithmatex">，
// 必须由 MathJax 负责渲染。如果只依赖单一 CDN，一旦该 CDN 在用户网络下不可达，
// 公式就会以纯文本形式裸露在页面上（这正是要避免的问题）。
//
// 策略：按顺序尝试多个 CDN，哪个先加载成功就用哪个；全部失败时给出控制台提示。

window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"], ["$", "$"]],
    displayMath: [["\\[", "\\]"], ["$$", "$$"]],
    processEscapes: true,
    processEnvironments: true,
    tags: "none"
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  },
  svg: {
    fontCache: "global"
  }
};

(function () {
  var CDNS = [
    "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js",
    "https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js",
    "https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.min.js",
    "https://npm.elemecdn.com/mathjax@3/es5/tex-mml-chtml.js"
  ];

  var idx = 0;
  var loaded = false;

  function tryNext() {
    if (loaded || idx >= CDNS.length) {
      if (!loaded) {
        console.warn(
          "[mathjax] 所有 CDN 均不可达，公式将显示为 LaTeX 源码。" +
            "如需离线可用，请把 mathjax 打包到 docs/javascripts/ 下并改写此文件。"
        );
      }
      return;
    }
    var url = CDNS[idx++];
    var s = document.createElement("script");
    s.src = url;
    s.async = true;
    s.onload = function () {
      loaded = true;
      // 脚本就绪后主动排版一次，避免只依赖自动排版
      if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise();
      }
    };
    s.onerror = function () {
      console.warn("[mathjax] 加载失败，尝试下一个 CDN：" + url);
      tryNext();
    };
    document.head.appendChild(s);
  }

  tryNext();

  // Material 的 instant navigation 换页后需要重新排版
  if (typeof document$ !== "undefined") {
    document$.subscribe(function () {
      if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.startup.output.clearCache();
        window.MathJax.typesetClear();
        window.MathJax.texReset();
        window.MathJax.typesetPromise();
      }
    });
  }
})();
