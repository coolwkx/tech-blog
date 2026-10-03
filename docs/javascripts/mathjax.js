// MathJax 配置：让行内 $...$ 与块级 $$...$$ 都能渲染。
// 没有这个文件时，pymdownx.arithmatex 生成的公式会以纯文本形式裸露在页面上。
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

// Material 主题的 instant navigation 会在不刷新页面的情况下换页，
// 因此每次切换后都要重新排版公式（document$ 是主题提供的可观察对象）。
// 加存在性判断：万一主题未提供该对象，也不能让脚本整体报错。
if (typeof document$ !== "undefined") {
  document$.subscribe(() => {
    if (window.MathJax && window.MathJax.typesetPromise) {
      MathJax.startup.output.clearCache();
      MathJax.typesetClear();
      MathJax.texReset();
      MathJax.typesetPromise();
    }
  });
}
