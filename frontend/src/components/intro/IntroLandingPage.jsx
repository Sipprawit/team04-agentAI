import React from 'react';
import {
  Sparkles,
  ArrowRight,
  FileSpreadsheet,
  Bot,
  BarChart3,
  ShieldCheck,
  Zap,
  TrendingUp,
  CheckCircle2,
  PieChart as PieIcon,
  Pin,
  Check
} from 'lucide-react';
import './IntroLandingPage.css';

export default function IntroLandingPage({ onStartApp }) {
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

      {/* 1. Glassmorphism Top Navigation Bar */}
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

          <nav className="intro-nav-links">
            <button type="button" onClick={() => scrollToSection('how-it-works')} className="nav-link-btn">
              <span>How It Works</span>
              <span className="nav-link-th">ขั้นตอนการทำงาน</span>
            </button>
            <button type="button" onClick={() => scrollToSection('features')} className="nav-link-btn">
              <span>Capabilities</span>
              <span className="nav-link-th">จุดเด่นระบบ</span>
            </button>
          </nav>
        </div>
      </header>

      {/* 2. Hero Section */}
      <section className="intro-hero-section">
        <div className="intro-hero-container">
          {/* Top Pill Badge */}
          <div className="hero-pill-badge">
            <div className="pill-dot" />
            <Sparkles size={14} className="text-amber-400" />
            <span>Enterprise Intelligence • สถาปัตยกรรมวิเคราะห์ข้อมูลอัจฉริยะ</span>
          </div>

          {/* Main Prominent Headline */}
          <h1 className="hero-main-title">
            Conversational Data Analytics <br />
            <span className="gradient-text">Engineered for Thai Business Data</span>
          </h1>

          {/* Sub-headline description */}
          <p className="hero-subtitle">
            Transform natural Thai language queries into safe SQL, instant statistical summaries, and interactive visual dashboards.
            <span className="hero-subtitle-th">
              (สืบค้นข้อมูล แปลงคำถามภาษาไทยเป็นคำสั่ง SQL วิเคราะห์สถิติ และสร้างรายงานอัตโนมัติด้วยระบบความปลอดภัยระดับองค์กร)
            </span>
          </p>

          {/* Single Focused Smooth Start Button */}
          <div className="hero-action-container">
            <button
              type="button"
              className="hero-start-btn"
              onClick={() => onStartApp && onStartApp('')}
            >
              <span>Start</span>
              <ArrowRight size={18} className="btn-arrow-icon" />
            </button>
          </div>

          {/* Trust Indicators / Badges */}
          <div className="hero-trust-indicators">
            <div className="trust-item">
              <ShieldCheck size={18} className="text-emerald-400" />
              <div className="trust-text-group">
                <span className="trust-label-en">4-Layer Sandbox</span>
                <span className="trust-label-th">ความปลอดภัยอ่านอย่างเดียว 100%</span>
              </div>
            </div>
            <div className="trust-divider" />
            <div className="trust-item">
              <Zap size={18} className="text-blue-400" />
              <div className="trust-text-group">
                <span className="trust-label-en">Groq High-Speed LLM</span>
                <span className="trust-label-th">ประมวลผลคำสั่งรวดเร็วระดับวินาที</span>
              </div>
            </div>
            <div className="trust-divider" />
            <div className="trust-item">
              <BarChart3 size={18} className="text-purple-400" />
              <div className="trust-text-group">
                <span className="trust-label-en">Automated Insights</span>
                <span className="trust-label-th">สังเคราะห์แผนภูมิและสรุปสถิติจริง</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3. How It Works Section */}
      <section id="how-it-works" className="intro-steps-section">
        <div className="steps-container">
          <div className="section-header-centered">
            <span className="section-pill-tag">WORKFLOW</span>
            <h2 className="section-title">
              How It Works <span className="highlight-text">• 3 ขั้นตอนการวิเคราะห์ข้อมูลสู่แดชบอร์ด</span>
            </h2>
            <p className="section-subtitle">
              From raw spreadsheet datasets to comprehensive executive visual dashboards in seconds.
              <span className="section-subtitle-th">
                (เปลี่ยนข้อมูลดิบสู่แดชบอร์ดสรุปผลเชิงลึกอย่างเป็นระบบ ไร้ความซับซ้อน)
              </span>
            </p>
          </div>

          {/* 3 Step Cards Grid */}
          <div className="steps-cards-grid">
            {/* Step 1 */}
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
                      <div className="grid-cell">หมวดหมู่</div>
                      <div className="grid-cell">ยอดขาย (บาท)</div>
                      <div className="grid-cell">วันที่</div>
                    </div>
                    <div className="grid-row">
                      <div className="grid-cell">เครื่องดื่ม</div>
                      <div className="grid-cell highlight-cell">45,000</div>
                      <div className="grid-cell">2026-08-15</div>
                    </div>
                    <div className="grid-row">
                      <div className="grid-cell">เบเกอรี่</div>
                      <div className="grid-cell highlight-cell">89,200</div>
                      <div className="grid-cell">2026-08-16</div>
                    </div>
                  </div>
                  <div className="mockup-file-badge">
                    <FileSpreadsheet size={15} className="text-emerald-400" />
                    <span>CSV, Excel (.xlsx, .xls)</span>
                  </div>
                </div>
              </div>

              <div className="step-card-content">
                <div className="step-badge-icon step-icon-1">
                  <FileSpreadsheet size={20} />
                </div>
                <h3 className="step-heading">
                  1. Ingest Data Source
                  <span className="step-heading-th">นำเข้าชุดข้อมูล</span>
                </h3>
                <p className="step-desc">
                  Upload Excel (.xlsx, .xls) or CSV files. The engine automatically profiles schema, infers data types, detects Thai encodings (UTF-8, CP874), and checks for personal privacy data (PDPA).
                </p>
                <div className="step-feature-list">
                  <span className="feature-check-item">
                    <Check size={13} className="text-emerald-400" />
                    <span>Auto Type Inference & Schema Profiling</span>
                  </span>
                  <span className="feature-check-item">
                    <Check size={13} className="text-emerald-400" />
                    <span>UTF-8 / CP874 Detection & PDPA Warnings</span>
                  </span>
                </div>
              </div>
            </div>

            {/* Step 2 */}
            <div className="step-card step-card-2">
              <div className="step-visual-mockup">
                <div className="mockup-header-bar">
                  <div className="mockup-dots">
                    <span className="dot dot-r" />
                    <span className="dot dot-y" />
                    <span className="dot dot-g" />
                  </div>
                  <span className="mockup-title">AI Query Pipeline</span>
                </div>
                <div className="mockup-body mockup-analysis">
                  <div className="radar-circle-center">
                    <div className="radar-pulse" />
                    <Sparkles size={24} className="radar-sparkle text-emerald-400" />
                  </div>
                  <div className="radar-nodes">
                    <div className="radar-node node-charts">Charts</div>
                    <div className="radar-node node-insights">Insights</div>
                    <div className="radar-node node-kpis">KPIs</div>
                    <div className="radar-node node-sql">SQL Sandbox</div>
                  </div>
                  <div className="mockup-status-badge">
                    <Bot size={13} className="text-emerald-400" />
                    <span>Translating query & validating SQL...</span>
                  </div>
                </div>
              </div>

              <div className="step-card-content">
                <div className="step-badge-icon step-icon-2">
                  <Bot size={20} />
                </div>
                <h3 className="step-heading">
                  2. Autonomous Query & SQL Execution
                  <span className="step-heading-th">วิเคราะห์ภาษาไทยและรันคำสั่ง</span>
                </h3>
                <p className="step-desc">
                  AI translates Thai questions into optimized SQL queries, executes strictly within a 4-layer read-only sandbox, and heals SQL automatically if syntax adjustments are needed.
                </p>
                <div className="step-feature-list">
                  <span className="feature-check-item">
                    <Check size={13} className="text-emerald-400" />
                    <span>4-Layer Read-Only Sandbox (`PRAGMA query_only`)</span>
                  </span>
                  <span className="feature-check-item">
                    <Check size={13} className="text-emerald-400" />
                    <span>Agentic Self-Correction Loop (Up to 2 Retries)</span>
                  </span>
                </div>
              </div>
            </div>

            {/* Step 3 */}
            <div className="step-card step-card-3">
              <div className="step-visual-mockup">
                <div className="mockup-header-bar">
                  <div className="mockup-dots">
                    <span className="dot dot-r" />
                    <span className="dot dot-y" />
                    <span className="dot dot-g" />
                  </div>
                  <span className="mockup-title">Visual Dashboard Ready</span>
                </div>
                <div className="mockup-body mockup-dashboard">
                  <div className="kpi-mini-grid">
                    <div className="kpi-mini-card">
                      <span className="kpi-label">TOTAL SALES</span>
                      <strong className="kpi-val text-blue-400">฿2.4M</strong>
                    </div>
                    <div className="kpi-mini-card">
                      <span className="kpi-label">GROWTH</span>
                      <strong className="kpi-val text-emerald-400">+18.5%</strong>
                    </div>
                    <div className="kpi-mini-card">
                      <span className="kpi-label">TRANSACTIONS</span>
                      <strong className="kpi-val text-purple-400">12,847</strong>
                    </div>
                  </div>
                  <div className="chart-mini-bars">
                    <div className="bar-col bar-1" style={{ height: '45%' }} />
                    <div className="bar-col bar-2" style={{ height: '70%' }} />
                    <div className="bar-col bar-3" style={{ height: '95%' }} />
                    <div className="bar-col bar-4" style={{ height: '60%' }} />
                    <div className="bar-col bar-5" style={{ height: '80%' }} />
                  </div>
                  <div className="mockup-insight-pill">
                    <CheckCircle2 size={13} className="text-emerald-400" />
                    <span>Interactive Charts & KPI Insights</span>
                  </div>
                </div>
              </div>

              <div className="step-card-content">
                <div className="step-badge-icon step-icon-3">
                  <BarChart3 size={20} />
                </div>
                <h3 className="step-heading">
                  3. Visual Analytics & Reports
                  <span className="step-heading-th">แสดงผลเชิงภาพและส่งออกรายงาน</span>
                </h3>
                <p className="step-desc">
                  Inspect recommended charts (Bar, Line, Area, Pie), review deterministic executive summaries without hallucinations, pin charts to your personal dashboard, and export reports in 2x Retina PNG or CSV.
                </p>
                <div className="step-feature-list">
                  <span className="feature-check-item">
                    <Check size={13} className="text-emerald-400" />
                    <span>Smart Chart Recommendations & Fullscreen Tables</span>
                  </span>
                  <span className="feature-check-item">
                    <Check size={13} className="text-emerald-400" />
                    <span>Pin to Dashboard & High-Res 2x PNG / CSV Export</span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Core Features Showcase Grid */}
      <section id="features" className="intro-features-section">
        <div className="features-container">
          <div className="section-header-centered">
            <span className="section-pill-tag">CAPABILITIES</span>
            <h2 className="section-title">
              Key Capabilities <span className="gradient-text">• จุดเด่นสถาปัตยกรรมระบบ</span>
            </h2>
            <p className="section-subtitle">
              Engineered with advanced natural language processing, deterministic statistics, and defense-in-depth security.
              <span className="section-subtitle-th">
                (เทคโนโลยีที่ผสานการประมวลผลภาษาธรรมชาติ สถิติเชิงปริมาณ และความปลอดภัยระดับองค์กร)
              </span>
            </p>
          </div>

          <div className="features-grid-cards">
            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-blue">
                <Zap size={22} />
              </div>
              <h4 className="feature-title">
                Thai Natural Language to SQL
                <span className="feature-title-th">เข้าใจไวยากรณ์และบริบทภาษาไทย</span>
              </h4>
              <p className="feature-desc">
                Converts natural Thai questions into accurate SQLite queries using Few-Shot contextual understanding and schema mapping.
              </p>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-emerald">
                <ShieldCheck size={22} />
              </div>
              <h4 className="feature-title">
                4-Layer Security Sandbox
                <span className="feature-title-th">ความปลอดภัยอ่านอย่างเดียว 100%</span>
              </h4>
              <p className="feature-desc">
                Protected by Pre-validation, AST Sanitizer, C-Engine `PRAGMA query_only = ON;`, execution timeout, and row limits.
              </p>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-purple">
                <Bot size={22} />
              </div>
              <h4 className="feature-title">
                Agentic Self-Correction Loop
                <span className="feature-title-th">ระบบกู้คืนคำสั่งอัตโนมัติ</span>
              </h4>
              <p className="feature-desc">
                Automatically diagnoses SQL errors against database schema and corrects queries up to 2 times without user intervention.
              </p>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-amber">
                <TrendingUp size={22} />
              </div>
              <h4 className="feature-title">
                Deterministic Insights
                <span className="feature-title-th">สถิติจริง ปราศจากการคาดเดา</span>
              </h4>
              <p className="feature-desc">
                Calculates factual metrics (sum, mean, min, max) with real business units directly from query results—zero hallucinations.
              </p>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-cyan">
                <PieIcon size={22} />
              </div>
              <h4 className="feature-title">
                Automated Chart Recommender
                <span className="feature-title-th">แนะนำแผนภูมิอัตโนมัติ</span>
              </h4>
              <p className="feature-desc">
                Selects the best visualization (Bar, Line, Area, Pie) based on data cardinality and provides 2x Retina PNG export.
              </p>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-rose">
                <Pin size={22} />
              </div>
              <h4 className="feature-title">
                Pinned Board & Multi-Session
                <span className="feature-title-th">แดชบอร์ดส่วนตัวและประวัติแชท</span>
              </h4>
              <p className="feature-desc">
                Pin critical insight cards to your customizable dashboard grid, and manage isolated SQLite conversation histories effortlessly.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. Minimalist Footer */}
      <footer className="intro-footer">
        <div className="footer-container">
          <div className="footer-left">
            <div className="footer-brand">
              <Bot size={18} className="text-blue-400" />
              <span>DataAgent AI</span>
            </div>
            <p className="footer-copy">
              Intelligent Conversational Data Analytics Platform • Team 04
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
