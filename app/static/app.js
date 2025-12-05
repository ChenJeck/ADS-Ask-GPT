const treeNodes = document.querySelectorAll('.tree-node');
const panels = document.querySelectorAll('.panel');
const preview = document.getElementById('report-preview');
const generateBtn = document.getElementById('generate-report');
const resetBtn = document.getElementById('reset-form');
const reportForm = document.getElementById('report-form');

// 左侧树形导航交互
if (treeNodes.length) {
  treeNodes.forEach((node) => {
    node.addEventListener('click', () => {
      const target = node.dataset.target;
      treeNodes.forEach((n) => n.classList.remove('active'));
      node.classList.add('active');
      panels.forEach((panel) => {
        panel.classList.toggle('active', panel.id === target);
      });
    });
  });
}

// 报表预览演示
const buildPreview = (data) => {
  const { date_from, date_to, metrics, dimensions, limit } = data;
  const metricList = metrics ? metrics.split(',').map((m) => m.trim()).filter(Boolean) : [];
  const dimensionList = dimensions ? dimensions.split(',').map((d) => d.trim()).filter(Boolean) : [];

  const chips = [...metricList, ...dimensionList].map((item) => `<span class="chip">${item}</span>`).join(' ');

  preview.innerHTML = `
    <div class="preview-header">
      <div>
        <p class="eyebrow">分析窗口</p>
        <h4>${date_from || '开始日期'} 至 ${date_to || '结束日期'}</h4>
      </div>
      <div class="preview-limit">TOP ${limit || 50}</div>
    </div>
    <p class="muted">已选择的指标 / 维度：</p>
    <div class="chip-row">${chips || '<span class="muted">尚未选择任何字段</span>'}</div>
    <div class="sample-data">
      <div class="badge">样本</div>
      <p>生成时将自动展示从 ADS 拉取的样本数据，并附带 ChatGPT 生成的中文报表摘要。</p>
    </div>
  `;
};

if (generateBtn) {
  generateBtn.addEventListener('click', () => {
    const formData = new FormData(reportForm);
    const payload = Object.fromEntries(formData.entries());
    buildPreview(payload);
    generateBtn.textContent = '已生成 · 再试一次';
    generateBtn.classList.add('success');
    setTimeout(() => generateBtn.classList.remove('success'), 1200);
  });
}

if (resetBtn) {
  resetBtn.addEventListener('click', () => {
    reportForm.reset();
    preview.innerHTML = '<p class="muted">填写表单后点击生成，即可在此看到分析结果与样本数据概览。</p>';
  });
}
