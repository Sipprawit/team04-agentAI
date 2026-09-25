import React, { useState } from 'react';
import {
  Sparkles,
  ArrowRight,
  FileSpreadsheet,
  Bot,
  BarChart3,
  ShieldCheck,
  Zap,
  TrendingUp,
  PieChart as PieIcon,
  Pin,
  Lock,
  Database,
  Code2,
  Check,
  Table as TableIcon
} from 'lucide-react';
import './IntroLandingPage.css';

export default function IntroLandingPage({ onStartApp }) {
  // Interactive Live Demo tab state
  const [activeDemoIdx, setActiveDemoIdx] = useState(0);

  const demoScenarios = [
    {
      id: 'sales',
      tabLabel: 'Sales & Revenue',
      thaiLabel: 'ยอดขายและรายได้',
      userQuery: 'สรุปยอดขายรวมแยกตามหมวดหมู่สินค้า 5 อันดับแรก',
      generatedSql: 'SELECT category, SUM(amount) AS total_sales\nFROM dataset\nGROUP BY category\nORDER BY total_sales DESC\nLIMIT 5;',
      chartType: 'Bar Chart (Horizontal)',
      kpiSummary: [
        { label: 'Total Revenue', value: '฿ 4,829,000' },
        { label: 'Top Category', value: 'Electronics (38%)' },
        { label: 'Avg Order Value', value: '฿ 1,420' }
      ],
      aiExplanation: 'ยอดขายรวมทั้งหมดอยู่ที่ 4,829,000 บาท โดยหมวดหมู่อุปกรณ์อิเล็กทรอนิกส์มียอดจำหน่ายสูงสุด คิดเป็นสัดส่วน 38% ของรายได้ทั้งหมด'
    },
    {
      id: 'growth',
      tabLabel: 'Monthly Trend',
      thaiLabel: 'แนวโน้มการเติบโต',
      userQuery: 'แสดงแนวโน้มยอดขายรายเดือนตลอดปี 2026 พร้อมอัตราการเติบโต',
      generatedSql: 'SELECT strftime(\'%Y-%m\', order_date) AS month, COUNT(*) AS orders, SUM(amount) AS monthly_revenue\nFROM dataset\nGROUP BY month\nORDER BY month ASC;',
      chartType: 'Area / Line Chart',
      kpiSummary: [
        { label: 'Annual Growth', value: '+24.5%' },
        { label: 'Peak Month', value: 'August 2026' },
        { label: 'Total Orders', value: '18,450' }
      ],
      aiExplanation: 'แนวโน้มยอดขายรายเดือนมีทิศทางเติบโตต่อเนื่อง (+24.5%) โดยมียอดคำสั่งซื้อสูงสุดในเดือนสิงหาคม จำนวน 18,450 รายการ'
    },
    {
      id: 'customer',
      tabLabel: 'Customer Segments',
      thaiLabel: 'สัดส่วนกลุ่มลูกค้า',
      userQuery: 'เปรียบเทียบสัดส่วนมูลค่าคำสั่งซื้อของกลุ่มลูกค้าสมาชิกและลูกค้าทั่วไป',
      generatedSql: 'SELECT customer_type, COUNT(*) AS count, ROUND(AVG(amount), 2) AS avg_spend\nFROM dataset\nGROUP BY customer_type;',
      chartType: 'Donut / Pie Chart',
      kpiSummary: [
        { label: 'VIP Members', value: '64.2%' },
        { label: 'New Customers', value: '35.8%' },
        { label: 'Retention Rate', value: '88.4%' }
      ],
      aiExplanation: 'ลูกค้ากลุ่มสมาชิกสร้างมูลค่าเฉลี่ยต่อคำสั่งซื้อสูงกว่าลูกค้าทั่วไป 1.8 เท่า และคิดเป็นสัดส่วนรายได้หลัก 64.2%'
    }
  ];

  const currentDemo = demoScenarios[activeDemoIdx];

  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="intro-page-root">
      {/* Background Ambient Glow Elements */}
      <div className="ambient-glow glow-top-left" />
      <div className="ambient-glow glow-top-right" />
      <div className="ambient-glow glow-center" />
      <div className="ambient-grid-overlay" />

      {/* 1. Top Navbar (Clean, Re-ordered: How It Works -> Features -> Security) */}
      <header className="intro-navbar">
        <div className="intro-nav-container">
          <div className="intro-brand">
            <div className="brand-logo-glow">
              <Bot size={22} className="brand-logo-icon" />
            </div>
            <div className="brand-titles">
              <span className="brand-name">DataAgent AI</span>
              <span className="brand-tag">Team 04</span>
            </div>
          </div>

          {/* Navigation Links ordered strictly: Workflow (ขั้นตอน) -> Capabilities (จุดเด่น) -> Security (ความปลอดภัย) */}
          <nav className="intro-nav-links">
            <button type="button" onClick={() => scrollToSection('how-it-works')} className="nav-link-btn">
              <span>Workflow</span>
              <span className="nav-th-sub">ขั้นตอน</span>
            </button>
            <button type="button" onClick={() => scrollToSection('features')} className="nav-link-btn">
              <span>Capabilities</span>
              <span className="nav-th-sub">จุดเด่น</span>
            </button>
            <button type="button" onClick={() => scrollToSection('security')} className="nav-link-btn">
              <span>Security</span>
              <span className="nav-th-sub">ความปลอดภัย</span>
            </button>
          </nav>

          <div className="intro-nav-status">
            <span className="status-live-dot" />
            <span className="status-live-text">Enterprise Ready</span>
          </div>
        </div>
      </header>

      {/* 2. Hero Section (Ultra-Clean, Elegant, Single Smooth Start Button) */}
      <section className="intro-hero-section">
        <div className="intro-hero-container">
          {/* Top Pill Badge */}
          <div className="hero-pill-badge">
            <Sparkles size={13} className="text-blue-400" />
            <span>Next-Generation Natural Language to SQL Analytics</span>
          </div>

          {/* Main Prominent Headline */}
          <h1 className="hero-main-title">
            Conversational Data Intelligence <br />
            <span className="gradient-text">Engineered for Modern Enterprise</span>
          </h1>

          {/* Sub-headline description (English with concise Thai explanation) */}
          <p className="hero-subtitle">
            Upload your CSV or Excel dataset and ask questions in natural Thai or English.
            Our multi-stage AI engine synthesizes verified SQL, runs secure computations in a sandbox,
            and renders executive dashboards instantly.
          </p>
          <p className="hero-subtitle-th">
            ระบบวิเคราะห์ข้อมูลอัจฉริยะ แปลงคำถามภาษาธรรมชาติเป็นคำสั่ง SQL ที่ปลอดภัย พร้อมสังเคราะห์แผนภูมิสถิติและบทสรุปเชิงลึกอัตโนมัติ
          </p>

          {/* Single Refined "Start" CTA Button */}
          <div className="hero-start-action-container">
            <button
              type="button"
              className="hero-start-smooth-btn"
              onClick={() => onStartApp && onStartApp('')}
            >
              <span>Start</span>
              <ArrowRight size={18} className="start-arrow-icon" />
            </button>
          </div>

          {/* Trust Highlights */}
          <div className="hero-trust-indicators">
            <div className="trust-item">
              <ShieldCheck size={16} className="text-emerald-400" />
              <span className="trust-label">4-Layer Sandbox Security</span>
            </div>
            <div className="trust-divider" />
            <div className="trust-item">
              <Zap size={16} className="text-blue-400" />
              <span className="trust-label">Zero-Hallucination SQL Execution</span>
            </div>
            <div className="trust-divider" />
            <div className="trust-item">
              <BarChart3 size={16} className="text-indigo-400" />
              <span className="trust-label">Automated Visual Analytics</span>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Interactive Live Showcase Simulator (Interactive Feature) */}
      <section className="intro-interactive-showcase">
        <div className="showcase-container">
          <div className="section-header-centered">
            <span className="section-pill-tag">LIVE INTERACTIVE PREVIEW</span>
            <h2 className="section-title">
              See the Platform in <span className="gradient-text">Action</span>
            </h2>
            <p className="section-subtitle">
              เลือกหัวข้อจำลองเพื่อดูการประมวลผลจากคำถามภาษาไทยสู่คำสั่ง SQL และแดชบอร์ดสรุปผลแบบเรียลไทม์
            </p>
          </div>

          {/* Interactive Scenario Tabs */}
          <div className="showcase-tabs-wrapper">
            {demoScenarios.map((demo, idx) => (
              <button
                key={demo.id}
                type="button"
                className={`showcase-tab-btn ${activeDemoIdx === idx ? 'active' : ''}`}
                onClick={() => setActiveDemoIdx(idx)}
              >
                <span className="tab-en">{demo.tabLabel}</span>
                <span className="tab-th">{demo.thaiLabel}</span>
              </button>
            ))}
          </div>

          {/* Showcase Terminal & Result Card */}
          <div className="showcase-display-card">
            <div className="showcase-card-header">
              <div className="window-dots">
                <span className="w-dot dot-red" />
                <span className="w-dot dot-yellow" />
                <span className="w-dot dot-green" />
              </div>
              <div className="showcase-header-title">
                <Bot size={14} className="text-blue-400" />
                <span>AI Execution Pipeline • {currentDemo.tabLabel}</span>
              </div>
              <div className="showcase-security-tag">
                <Check size={12} className="text-emerald-400" />
                <span>Sandbox Verified</span>
              </div>
            </div>

            <div className="showcase-body-grid">
              {/* Left Column: Natural Query & Synthesized SQL */}
              <div className="showcase-col-query">
                <div className="query-box">
                  <div className="query-label">
                    <span className="tag-nl">Natural Language Query (TH)</span>
                  </div>
                  <div className="query-text">
                    "{currentDemo.userQuery}"
                  </div>
                </div>

                <div className="sql-box">
                  <div className="sql-box-header">
                    <div className="sql-box-title">
                      <Code2 size={13} className="text-indigo-400" />
                      <span>Synthesized SQLite Query</span>
                    </div>
                    <span className="sql-engine-badge">AST Validated</span>
                  </div>
                  <pre className="sql-code-snippet">
                    <code>{currentDemo.generatedSql}</code>
                  </pre>
                </div>

                <div className="insight-box">
                  <div className="insight-title">
                    <Sparkles size={13} className="text-amber-400" />
                    <span>AI Executive Insight</span>
                  </div>
                  <p className="insight-text">{currentDemo.aiExplanation}</p>
                </div>
              </div>

              {/* Right Column: Instant Visual KPI & Chart Preview */}
              <div className="showcase-col-preview">
                <div className="kpi-cards-row">
                  {currentDemo.kpiSummary.map((kpi, kIdx) => (
                    <div key={kIdx} className="mini-kpi-card">
                      <span className="kpi-label">{kpi.label}</span>
                      <span className="kpi-value">{kpi.value}</span>
                    </div>
                  ))}
                </div>

                {/* Simulated Chart Container */}
                <div className="chart-preview-container">
                  <div className="chart-preview-header">
                    <div className="chart-title-group">
                      <BarChart3 size={15} className="text-blue-400" />
                      <span>{currentDemo.chartType}</span>
                    </div>
                    <span className="chart-badge-auto">Auto-Generated</span>
                  </div>

                  <div className="chart-bars-simulation">
                    {activeDemoIdx === 0 && (
                      <div className="simulated-bar-group">
                        <div className="bar-row">
                          <span className="bar-label">Electronics</span>
                          <div className="bar-track"><div className="bar-fill fill-blue" style={{ width: '85%' }} /></div>
                          <span className="bar-val">฿ 1.83M</span>
                        </div>
                        <div className="bar-row">
                          <span className="bar-label">Home & Living</span>
                          <div className="bar-track"><div className="bar-fill fill-indigo" style={{ width: '68%' }} /></div>
                          <span className="bar-val">฿ 1.15M</span>
                        </div>
                        <div className="bar-row">
                          <span className="bar-label">Fashion</span>
                          <div className="bar-track"><div className="bar-fill fill-cyan" style={{ width: '52%' }} /></div>
                          <span className="bar-val">฿ 820K</span>
                        </div>
                        <div className="bar-row">
                          <span className="bar-label">Beauty</span>
                          <div className="bar-track"><div className="bar-fill fill-emerald" style={{ width: '40%' }} /></div>
                          <span className="bar-val">฿ 590K</span>
                        </div>
                        <div className="bar-row">
                          <span className="bar-label">Groceries</span>
                          <div className="bar-track"><div className="bar-fill fill-amber" style={{ width: '30%' }} /></div>
                          <span className="bar-val">฿ 439K</span>
                        </div>
                      </div>
                    )}

                    {activeDemoIdx === 1 && (
                      <div className="simulated-line-group">
                        <div className="trend-stat-row">
                          <div className="trend-stat-pill">Q1: ฿ 920K</div>
                          <div className="trend-stat-pill">Q2: ฿ 1.25M</div>
                          <div className="trend-stat-pill">Q3: ฿ 1.78M</div>
                          <div className="trend-stat-pill highlight">Q4: ฿ 2.15M</div>
                        </div>
                        <div className="line-graph-mockup">
                          <div className="sparkline-bar b1" />
                          <div className="sparkline-bar b2" />
                          <div className="sparkline-bar b3" />
                          <div className="sparkline-bar b4" />
                          <div className="sparkline-bar b5" />
                          <div className="sparkline-bar b6" />
                          <div className="sparkline-bar b7" />
                          <div className="sparkline-bar b8" />
                        </div>
                      </div>
                    )}

                    {activeDemoIdx === 2 && (
                      <div className="simulated-donut-group">
                        <div className="donut-vis-row">
                          <div className="donut-circle-mockup">
                            <div className="donut-inner">
                              <span className="donut-pct">64.2%</span>
                              <span className="donut-lbl">Members</span>
                            </div>
                          </div>
                          <div className="donut-legend-col">
                            <div className="legend-item"><span className="dot dot-indigo" /> VIP Tier (64.2%)</div>
                            <div className="legend-item"><span className="dot dot-cyan" /> Regular (35.8%)</div>
                            <div className="legend-item"><span className="dot dot-emerald" /> Retention (88.4%)</div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Section 1: Workflow / How It Works (id="how-it-works") */}
      <section id="how-it-works" className="intro-steps-section">
        <div className="steps-container">
          <div className="section-header-centered">
            <span className="section-pill-tag">END-TO-END WORKFLOW</span>
            <h2 className="section-title">
              How to Create a Data Dashboard in <span className="highlight-text">3 Simple Steps</span>
            </h2>
            <p className="section-subtitle">
              From raw Excel or CSV files to interactive KPI metrics, visual charts, and executive insights
            </p>
            <p className="section-subtitle-th">
              ขั้นตอนการทำงาน 3 ขั้นตอน ตั้งแต่นำเข้าไฟล์สเปรดชีต จนถึงแดชบอร์ดสรุปสถิติอัตโนมัติ
            </p>
          </div>

          <div className="steps-cards-grid">
            {/* Step 1: Upload */}
            <div className="step-card step-card-1">
              <div className="step-visual-mockup">
                <div className="mockup-header-bar">
                  <div className="mockup-dots">
                    <span className="dot dot-r" />
                    <span className="dot dot-y" />
                    <span className="dot dot-g" />
                  </div>
                  <span className="mockup-title">dataset_upload.xlsx</span>
                </div>
                <div className="mockup-body mockup-spreadsheets">
                  <div className="spreadsheet-grid">
                    <div className="grid-row grid-row-header">
                      <div className="grid-cell">Category</div>
                      <div className="grid-cell">Revenue</div>
                      <div className="grid-cell">Date</div>
                    </div>
                    <div className="grid-row">
                      <div className="grid-cell">Electronics</div>
                      <div className="grid-cell highlight-cell">45,000</div>
                      <div className="grid-cell">2026-08-15</div>
                    </div>
                    <div className="grid-row">
                      <div className="grid-cell">Retail</div>
                      <div className="grid-cell highlight-cell">89,200</div>
                      <div className="grid-cell">2026-08-16</div>
                    </div>
                  </div>
                  <div className="mockup-file-badge">
                    <FileSpreadsheet size={14} className="text-emerald-400" />
                    <span>Excel (.xlsx, .xls) & CSV</span>
                  </div>
                </div>
              </div>

              <div className="step-card-content">
                <div className="step-badge-icon step-icon-1">
                  <span>01</span>
                </div>
                <h3 className="step-headline">Connect & Upload Data</h3>
                <span className="step-headline-th">นำเข้าชุดข้อมูลสเปรดชีต</span>
                <p className="step-description">
                  Simply drag & drop your business dataset. The system inspects column types, formats headers, and establishes a secure local SQLite table.
                </p>
              </div>
            </div>

            {/* Step 2: AI SQL Synthesis */}
            <div className="step-card step-card-2">
              <div className="step-visual-mockup">
                <div className="mockup-header-bar">
                  <div className="mockup-dots">
                    <span className="dot dot-r" />
                    <span className="dot dot-y" />
                    <span className="dot dot-g" />
                  </div>
                  <span className="mockup-title">Groq LLM + AST Validator</span>
                </div>
                <div className="mockup-body mockup-ai-center">
                  <div className="ai-pulse-radar">
                    <div className="radar-ring ring-1" />
                    <div className="radar-ring ring-2" />
                    <div className="radar-ring ring-3" />
                    <div className="radar-core">
                      <Zap size={22} className="text-amber-400" />
                    </div>
                  </div>
                  <div className="ai-code-pill">
                    <code>SELECT category, SUM(amount)...</code>
                  </div>
                </div>
              </div>

              <div className="step-card-content">
                <div className="step-badge-icon step-icon-2">
                  <span>02</span>
                </div>
                <h3 className="step-headline">AI SQL Synthesis</h3>
                <span className="step-headline-th">ประมวลผลคำสั่งภาษาธรรมชาติ</span>
                <p className="step-description">
                  Type questions in Thai or English. The engine maps your question to precise SQL queries with automatic self-healing error correction.
                </p>
              </div>
            </div>

            {/* Step 3: Executive Dashboard */}
            <div className="step-card step-card-3">
              <div className="step-visual-mockup">
                <div className="mockup-header-bar">
                  <div className="mockup-dots">
                    <span className="dot dot-r" />
                    <span className="dot dot-y" />
                    <span className="dot dot-g" />
                  </div>
                  <span className="mockup-title">Executive Dashboard</span>
                </div>
                <div className="mockup-body mockup-dashboard-view">
                  <div className="mini-dash-kpi">
                    <span className="dash-kpi-title">TOTAL AMOUNT</span>
                    <span className="dash-kpi-number">฿ 1,284,500</span>
                  </div>
                  <div className="mini-dash-charts">
                    <div className="mini-chart-card">
                      <div className="chart-bar-dummy">
                        <span style={{ height: '40%' }} />
                        <span style={{ height: '75%' }} />
                        <span style={{ height: '55%' }} />
                        <span style={{ height: '90%' }} />
                      </div>
                    </div>
                    <div className="mini-chart-card">
                      <div className="chart-donut-dummy" />
                    </div>
                  </div>
                  <div className="mini-pin-tag">
                    <Pin size={11} className="text-amber-400" />
                    <span>Pinned to Dashboard</span>
                  </div>
                </div>
              </div>

              <div className="step-card-content">
                <div className="step-badge-icon step-icon-3">
                  <span>03</span>
                </div>
                <h3 className="step-headline">Review Insights & Dashboard</h3>
                <span className="step-headline-th">แสดงผลแดชบอร์ดและบทสรุป</span>
                <p className="step-description">
                  View automated charts (Bar, Line, Pie), examine interactive tables, pin preferred visual cards, and export full reports effortlessly.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 5. Section 2: Core Capabilities (id="features") */}
      <section id="features" className="intro-features-section">
        <div className="features-container">
          <div className="section-header-centered">
            <span className="section-pill-tag">CAPABILITIES</span>
            <h2 className="section-title">
              Core Platform <span className="gradient-text">Capabilities</span>
            </h2>
            <p className="section-subtitle">
              Engineered with advanced natural language processing, quantitative statistical inference, and enterprise reliability
            </p>
            <p className="section-subtitle-th">
              จุดเด่นสำคัญที่ออกแบบมาเพื่อเพิ่มประสิทธิภาพในการวิเคราะห์ข้อมูลธุรกิจอย่างครบวงจร
            </p>
          </div>

          <div className="features-grid-cards">
            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-blue">
                <Zap size={22} />
              </div>
              <h4 className="feature-title">Thai & English NL-to-SQL</h4>
              <p className="feature-desc">
                High-precision SQL generation tailored for Thai business inquiries, handling Thai column aliases and schema mapping with few-shot intelligence.
              </p>
              <span className="feature-th-desc">รองรับการสืบค้นด้วยภาษาไทยธรรมชาติ แม่นยำต่อโครงสร้างตาราง</span>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-purple">
                <Bot size={22} />
              </div>
              <h4 className="feature-title">Agentic Self-Healing Loop</h4>
              <p className="feature-desc">
                Autonomous query correction. When a syntax or schema discrepancy occurs, the AI inspects error diagnostics and repairs queries up to 2 retries.
              </p>
              <span className="feature-th-desc">ระบบซ่อมแซมคำสั่งอัตโนมัติหากพบข้อผิดพลาด โดยไม่ต้องพิมพ์ถามใหม่</span>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-cyan">
                <PieIcon size={22} />
              </div>
              <h4 className="feature-title">Smart Chart Synthesis</h4>
              <p className="feature-desc">
                Automated chart selection matching analytical intent (Bar, Line, Area, Donut, Scatter) with custom color palettes and high-resolution export.
              </p>
              <span className="feature-th-desc">วิเคราะห์และสร้างแผนภูมิที่เหมาะสมกับรูปแบบข้อมูลโดยอัตโนมัติ</span>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-amber">
                <TrendingUp size={22} />
              </div>
              <h4 className="feature-title">Zero-Hallucination Insights</h4>
              <p className="feature-desc">
                Concise executive KPI summaries computed strictly from database results. Real currency and metric units with zero hallucinated figures.
              </p>
              <span className="feature-th-desc">สรุปยอดรวม ค่าเฉลี่ย สูงสุด-ต่ำสุด ตรงตามข้อมูลจริง ไม่มโนตัวเลข</span>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-emerald">
                <TableIcon size={22} />
              </div>
              <h4 className="feature-title">Interactive Data Table</h4>
              <p className="feature-desc">
                Instant pagination, column sorting, search filtering, and one-click UTF-8 BOM CSV export for universal Excel compatibility.
              </p>
              <span className="feature-th-desc">ตารางข้อมูลค้นหา คัดกรอง และดาวน์โหลดเป็นไฟล์ CSV (UTF-8 BOM) ได้ทันที</span>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-rose">
                <Pin size={22} />
              </div>
              <h4 className="feature-title">Custom Pinned Dashboard</h4>
              <p className="feature-desc">
                Pin essential charts and statistical cards to your persistent live workspace dashboard to compile cohesive executive summary presentations.
              </p>
              <span className="feature-th-desc">ปักหมุดกราฟเพื่อสร้างแดชบอร์ดเฉพาะตัวและจัดเตรียมรายงานสรุป</span>
            </div>
          </div>
        </div>
      </section>

      {/* 6. Section 3: Enterprise Security & Sandbox Architecture (id="security") */}
      <section id="security" className="intro-security-section">
        <div className="security-container">
          <div className="section-header-centered">
            <span className="section-pill-tag">SECURITY ARCHITECTURE</span>
            <h2 className="section-title">
              4-Layer <span className="gradient-text">Defense-in-Depth</span> Sandbox
            </h2>
            <p className="section-subtitle">
              Strict isolation preventing unauthorized data mutations, injection attempts, and excessive computational resource consumption
            </p>
            <p className="section-subtitle-th">
              ระบบรักษาความปลอดภัย 4 ชั้นมาตรฐาน ป้องกันการแก้ไข ลบ หรือดึงข้อมูลนอกเหนือคำสั่ง
            </p>
          </div>

          <div className="security-grid-cards">
            <div className="security-layer-card">
              <div className="security-layer-num">01</div>
              <div className="security-icon-circle icon-shield">
                <ShieldCheck size={24} />
              </div>
              <h4 className="security-layer-title">AST Syntax Sanitizer</h4>
              <p className="security-layer-desc">
                Pre-execution Abstract Syntax Tree (AST) validation blocks dangerous statements: <code>DROP</code>, <code>DELETE</code>, <code>UPDATE</code>, <code>INSERT</code>, <code>ALTER</code>, and <code>ATTACH</code>.
              </p>
              <div className="security-tag-badge">Pre-Execution Guard</div>
            </div>

            <div className="security-layer-card">
              <div className="security-layer-num">02</div>
              <div className="security-icon-circle icon-lock">
                <Lock size={24} />
              </div>
              <h4 className="security-layer-title">C-Core Read-Only Sandbox</h4>
              <p className="security-layer-desc">
                Direct SQLite C-Engine enforcement with <code>PRAGMA query_only = ON;</code> ensures zero write access at the storage layer under all circumstances.
              </p>
              <div className="security-tag-badge">Kernel Level Protection</div>
            </div>

            <div className="security-layer-card">
              <div className="security-layer-num">03</div>
              <div className="security-icon-circle icon-zap">
                <Zap size={24} />
              </div>
              <h4 className="security-layer-title">Resource & Timeout Guard</h4>
              <p className="security-layer-desc">
                Hard 10-second query execution timeouts paired with automated 500-row result truncation safeguard server memory against denial-of-service queries.
              </p>
              <div className="security-tag-badge">10s Timeout • 500 Rows Max</div>
            </div>

            <div className="security-layer-card">
              <div className="security-layer-num">04</div>
              <div className="security-icon-circle icon-db">
                <Database size={24} />
              </div>
              <h4 className="security-layer-title">Local Data Isolation</h4>
              <p className="security-layer-desc">
                Uploaded datasets remain air-gapped on your private database instance. Only abstract schemas and sample metadata are shared with language models.
              </p>
              <div className="security-tag-badge">Zero Data Leakage</div>
            </div>
          </div>
        </div>
      </section>

      {/* 7. Clean Minimal Footer (No Redundant Duplicate CTA) */}
      <footer className="intro-footer">
        <div className="footer-container">
          <div className="footer-left">
            <div className="footer-brand">
              <Bot size={18} className="text-blue-400" />
              <span>DataAgent AI</span>
              <span className="footer-version">v4.0 Enterprise</span>
            </div>
            <p className="footer-copy">
              ระบบผู้ช่วยวิเคราะห์ข้อมูลอัจฉริยะด้วยภาษาธรรมชาติและสถิติเชิงลึก (Team 04)
            </p>
          </div>
          <div className="footer-right">
            <span>Powered by FastAPI • React • LangChain • Groq AI • SQLite WAL</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
