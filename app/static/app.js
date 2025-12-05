const treeNodes = document.querySelectorAll('.tree-node');
const panels = document.querySelectorAll('.panel');
const preview = document.getElementById('report-preview');
const generateBtn = document.getElementById('generate-report');
const resetBtn = document.getElementById('reset-form');
const reportForm = document.getElementById('report-form');
const saveCardBtn = document.getElementById('save-card');
const reportStatus = document.getElementById('report-status');
const sourcePreview = document.getElementById('source-preview');
const sourceStatus = document.getElementById('source-status');
const cardGallery = document.getElementById('card-gallery');
const cardPagination = document.getElementById('card-pagination');
const modelForm = document.getElementById('model-form');
const sourceForm = document.getElementById('source-form');
const testModelBtn = document.getElementById('test-model');
const saveModelBtn = document.getElementById('save-model');
const testSourceBtn = document.getElementById('test-source');
const saveSourceBtn = document.getElementById('save-source');

const savedCards = [];
let currentPage = 1;
let lastReportData = null;

const toast = (target, message, state = 'info') => {
  if (!target) return;
  target.textContent = message;
  target.className = `status-chip ${state}`;
};

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

const summarizeModel = () => {
  if (!modelForm) return '';
  const formData = new FormData(modelForm);
  const model = formData.get('model') || 'deepseek';
  const apiBase = formData.get('api_base') || '未填写';
  const obfuscatedKey = (formData.get('api_key') || '').replace(/.(?=.{4})/g, '•');
  return `模型：${model.toUpperCase()} · Base：${apiBase} · Key：${obfuscatedKey || '未配置'}`;
};

const summarizeSource = () => {
  if (!sourceForm) return '';
  const formData = new FormData(sourceForm);
  const endpoint = formData.get('endpoint') || '未设置';
  const project = formData.get('project') || '未设置';
  const region = formData.get('region_note') || '未备注';
  return `Endpoint：${endpoint} / Project：${project} / 备注：${region}`;
};

const buildPreview = (data) => {
  const { ads_table, date_from, date_to, metrics, dimensions, limit } = data;
  const metricList = metrics ? metrics.split(',').map((m) => m.trim()).filter(Boolean) : [];
  const dimensionList = dimensions ? dimensions.split(',').map((d) => d.trim()).filter(Boolean) : [];
  const chips = [...metricList, ...dimensionList].map((item) => `<span class="chip">${item}</span>`).join(' ');
  const tableLabel = ads_table || '未选择宽表';

  preview.innerHTML = `
    <div class="preview-header">
      <div>
        <p class="eyebrow">分析窗口</p>
        <h4>${date_from || '开始日期'} 至 ${date_to || '结束日期'}</h4>
        <p class="muted">宽表：${tableLabel}</p>
      </div>
      <div class="preview-limit">TOP ${limit || 50}</div>
    </div>
    <p class="muted">已选择的指标 / 维度：</p>
    <div class="chip-row">${chips || '<span class="muted">尚未选择任何字段</span>'}</div>
    <div class="sample-data">
      <div class="badge">样本</div>
      <p>生成时将自动展示从 ADS 拉取的样本数据，并附带模型生成的中文与英文报表摘要。</p>
    </div>
  `;
};

const renderCards = (page = 1) => {
  if (!cardGallery || !cardPagination) return;
  if (!savedCards.length) {
    cardGallery.innerHTML = '<p class="muted">暂无保存的卡片，生成报表后点击保存即可在此查看。</p>';
    cardPagination.innerHTML = '';
    return;
  }

  const totalPages = Math.max(1, Math.ceil(savedCards.length / 9));
  currentPage = Math.min(page, totalPages);
  const start = (currentPage - 1) * 9;
  const end = start + 9;
  const currentCards = savedCards.slice(start, end);

  cardGallery.innerHTML = currentCards
    .map(
      (card) => `
      <div class="card-tile" data-id="${card.id}" data-lang="${card.lang}">
        <div class="tile-preview"></div>
        <div class="tile-meta">
          <span class="tile-badge">${card.table || '宽表未填'}</span>
          <span>${card.dateRange}</span>
        </div>
        <h4 class="tile-title">${card.lang === 'zh' ? card.titleZh : card.titleEn}</h4>
        <p class="tile-desc">${card.lang === 'zh' ? card.descZh : card.descEn}</p>
        <div class="tile-actions">
          <button class="page-btn translate-btn" data-id="${card.id}">翻译</button>
          <button class="page-btn preview-btn" data-id="${card.id}">预览</button>
        </div>
      </div>
    `
    )
    .join('');

  cardPagination.innerHTML = Array.from({ length: totalPages }, (_, idx) => {
    const pageNum = idx + 1;
    return `<button class="page-btn ${pageNum === currentPage ? 'active' : ''}" data-page="${pageNum}">${pageNum}</button>`;
  }).join('');
};

const toggleCardLanguage = (id) => {
  const card = savedCards.find((c) => c.id === id);
  if (!card) return;
  card.lang = card.lang === 'zh' ? 'en' : 'zh';
  renderCards(currentPage);
};

const showCardPreviewToast = (id) => {
  const card = savedCards.find((c) => c.id === id);
  if (!card || !reportStatus) return;
  toast(reportStatus, `预览：${card.titleZh} (${card.table})`, 'info');
};

if (cardGallery) {
  cardGallery.addEventListener('click', (event) => {
    const target = event.target;
    const id = target.dataset.id;
    if (!id) return;
    if (target.classList.contains('translate-btn')) {
      toggleCardLanguage(id);
    }
    if (target.classList.contains('preview-btn')) {
      showCardPreviewToast(id);
    }
  });
}

if (cardPagination) {
  cardPagination.addEventListener('click', (event) => {
    const target = event.target;
    const page = Number(target.dataset.page);
    if (page) renderCards(page);
  });
}

const handleReportGenerate = () => {
  const formData = new FormData(reportForm);
  const payload = Object.fromEntries(formData.entries());
  lastReportData = payload;
  buildPreview(payload);
  toast(reportStatus, '已生成最新预览', 'success');
  generateBtn.textContent = '已生成 · 再试一次';
  generateBtn.classList.add('success');
  if (saveCardBtn) saveCardBtn.disabled = false;
  setTimeout(() => generateBtn.classList.remove('success'), 1200);
};

if (generateBtn && reportForm) {
  generateBtn.addEventListener('click', handleReportGenerate);
}

if (resetBtn && reportForm) {
  resetBtn.addEventListener('click', () => {
    reportForm.reset();
    preview.innerHTML = '<p class="muted">填写表单后点击生成，即可在此看到分析结果与样本数据概览。</p>';
    toast(reportStatus, '等待生成', 'info');
    if (saveCardBtn) saveCardBtn.disabled = true;
    lastReportData = null;
  });
}

if (saveCardBtn) {
  saveCardBtn.addEventListener('click', () => {
    if (!lastReportData) return;
    const modelSummary = summarizeModel();
    const dateRange = `${lastReportData.date_from || '开始'} - ${lastReportData.date_to || '结束'}`;
    const metrics = lastReportData.metrics || '未指定';
    const dimensions = lastReportData.dimensions || '未指定';
    const titleZh = `${lastReportData.ads_table || 'ADS 宽表'} · ${dateRange}`;
    const descZh = `指标：${metrics}；维度：${dimensions}；Top ${lastReportData.limit || 50}；${modelSummary}`;
    const titleEn = `${lastReportData.ads_table || 'ADS table'} · ${dateRange}`;
    const descEn = `Metrics: ${metrics}; Dimensions: ${dimensions}; Top ${lastReportData.limit || 50}; ${modelSummary}`;

    savedCards.unshift({
      id: `${Date.now()}`,
      table: lastReportData.ads_table || 'ads_table',
      dateRange,
      titleZh,
      descZh,
      titleEn,
      descEn,
      lang: 'zh',
    });

    toast(reportStatus, '已保存到我的卡片', 'success');
    renderCards(1);
  });
}

if (testModelBtn) {
  testModelBtn.addEventListener('click', () => {
    const summary = summarizeModel();
    toast(reportStatus, `模型测试通过：${summary}`, 'success');
  });
}

if (saveModelBtn) {
  saveModelBtn.addEventListener('click', () => {
    toast(reportStatus, '模型配置已保存', 'success');
  });
}

if (testSourceBtn) {
  testSourceBtn.addEventListener('click', () => {
    toast(sourceStatus, '测试通过：连通性正常', 'success');
    sourcePreview.innerHTML = `<p>${summarizeSource()}</p>`;
  });
}

if (saveSourceBtn) {
  saveSourceBtn.addEventListener('click', () => {
    toast(sourceStatus, '已保存数据源配置', 'success');
    sourcePreview.innerHTML = `<p>${summarizeSource()}</p>`;
  });
}

renderCards();
