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
  CheckCircle2,
  ChevronRight,
  PieChart as PieIcon,
  Pin,
  Check,
  Star
} from 'lucide-react';
import './IntroLandingPage.css';

export default function IntroLandingPage({ onStartApp }) {
  const [sampleQuery, setSampleQuery] = useState('');

  const sampleQuestions = [
    'สรุปยอดขายรวมและจำแนกตามประเภทสินค้า',
    'เปรียบเทียบสัดส่วนตามแต่ละหมวดหมู่',
    'ค้นหา 5 อันดับแรกที่มีมูลค่าสูงที่สุด',
    'แสดงข้อมูลสถิติภาพรวมทั้งหมด'
  ];

  const handleLaunchWithQuery = (q) => {
    if (onStartApp) {
      onStartApp(q || sampleQuery);
    }
  };

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
            <button type="button" onClick={() => scrollToSection('features')} className="nav-link-btn">
              จุดเด่นระบบ
            </button>
            <button type="button" onClick={() => scrollToSection('how-it-works')} className="nav-link-btn">
              ขั้นตอนการใช้งาน
            </button>
            <button type="button" onClick={() => scrollToSection('security')} className="nav-link-btn">
              ความปลอดภัย
            </button>
          </nav>

          <div className="intro-nav-actions">
            <button
              type="button"
              className="intro-nav-cta-btn"
              onClick={() => handleLaunchWithQuery('')}
            >
              <span>เข้าสู่หน้าใช้งาน</span>
              <ArrowRight size={15} />
            </button>
          </div>
        </div>
      </header>

      {/* 2. Hero Section (Inspired by Reference Image 1) */}
      <section className="intro-hero-section">
        <div className="intro-hero-container">
          {/* Top Pill Badge */}
          <div className="hero-pill-badge">
            <div className="pill-dot" />
            <Sparkles size={14} className="text-amber-400" />
            <span>Next-Gen Thai Text-to-SQL & Automated Analytics</span>
          </div>

          {/* Main Prominent Headline */}
          <h1 className="hero-main-title">
            Powerful Thai Data Analytics <br />
            <span className="gradient-text">Begins Right Here for Your Team</span>
          </h1>

          {/* Feature Badges Pills */}
          <div className="hero-feature-tags">
            <span className="feature-tag-pill">
              <Zap size={13} className="text-amber-400" />
              <span>AI Thai-to-SQL</span>
            </span>
            <span className="feature-tag-pill">
              <ShieldCheck size={13} className="text-emerald-400" />
              <span>4-Layer Sandbox</span>
            </span>
            <span className="feature-tag-pill">
              <FileSpreadsheet size={13} className="text-blue-400" />
              <span>Excel & CSV Ready</span>
            </span>
            <span className="feature-tag-pill">
              <TrendingUp size={13} className="text-purple-400" />
              <span>Executive Insights</span>
            </span>
          </div>

          {/* Sub-headline description */}
          <p className="hero-subtitle">
            หยุดเสียเวลากับสูตร Excel ที่ซับซ้อน หรือการเขียนคำสั่ง SQL เอง 
            เพียงแค่นำเข้าชุดข้อมูลและพิมพ์คำถามภาษาไทย AI จะแปลงคำถามเป็นคำสั่ง SQL ที่ปลอดภัย 
            วิเคราะห์สถิติ และสร้างบทสรุปพร้อมแผนภูมิสถิติอัตโนมัติในไม่กี่วินาที
          </p>

          {/* Interactive Hero Input Box & CTA Button */}
          <div className="hero-action-box">
            <div className="hero-input-wrapper">
              <input
                type="text"
                className="hero-query-input"
                placeholder="พิมพ์คำถามภาษาไทย เช่น: สรุปยอดรวมและเปรียบเทียบตามหมวดหมู่..."
                value={sampleQuery}
                onChange={(e) => setSampleQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleLaunchWithQuery(sampleQuery);
                }}
              />
              <button
                type="button"
                className="hero-submit-btn"
                onClick={() => handleLaunchWithQuery(sampleQuery)}
              >
                <span>เริ่มใช้งานทันที</span>
                <ChevronRight size={16} />
              </button>
            </div>

            {/* Quick Sample Query Chips */}
            <div className="hero-sample-chips">
              <span className="sample-label">ลองเลือกคำถามตัวอย่าง:</span>
              <div className="chips-list">
                {sampleQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="sample-chip-btn"
                    onClick={() => handleLaunchWithQuery(q)}
                  >
                    <span>{q}</span>
                    <ArrowRight size={11} className="chip-arrow" />
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Trust Indicators / Badges */}
          <div className="hero-trust-indicators">
            <div className="trust-item">
              <div className="trust-stars">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} size={13} className="star-filled" fill="#f59e0b" />
                ))}
              </div>
              <span className="trust-label">100% Zero Hallucination Guarantee</span>
            </div>
            <div className="trust-divider" />
            <div className="trust-item">
              <ShieldCheck size={16} className="text-emerald-400" />
              <span className="trust-label">4-Layer Defense-in-Depth Sandbox</span>
            </div>
            <div className="trust-divider" />
            <div className="trust-item">
              <Zap size={16} className="text-blue-400" />
              <span className="trust-label">Groq High-Speed LLM & SQLite WAL</span>
            </div>
          </div>
        </div>
      </section>

      {/* 3. How It Works Section (Inspired by Reference Image 2: 3 Simple Steps) */}
      <section id="how-it-works" className="intro-steps-section">
        <div className="steps-container">
          <div className="section-header-centered">
            <span className="section-pill-tag">HOW IT WORKS</span>
            <h2 className="section-title">
              How to Create a Data Dashboard Online in <span className="highlight-text">3 Simple Steps</span>
            </h2>
            <p className="section-subtitle">
              From raw Excel or CSV data to a complete AI-generated interactive dashboard with multiple charts, KPI cards, data insights, and intelligent auto-layout
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
                      <div className="grid-cell">ยอดสถิติ</div>
                      <div className="grid-cell">วันที่</div>
                    </div>
                    <div className="grid-row">
                      <div className="grid-cell">บริการ</div>
                      <div className="grid-cell highlight-cell">45,000</div>
                      <div className="grid-cell">2026-08-15</div>
                    </div>
                    <div className="grid-row">
                      <div className="grid-cell">ค้าปลีก</div>
                      <div className="grid-cell highlight-cell">89,200</div>
                      <div className="grid-cell">2026-08-16</div>
                    </div>
                  </div>
                  <div className="mockup-file-badge">
                    <FileSpreadsheet size={15} className="text-emerald-400" />
                    <span>Excel, CSV, TSV Data Files</span>
                  </div>
                </div>
              </div>

              <div className="step-card-content">
                <div className="step-badge-icon step-icon-1">
                  <FileSpreadsheet size={20} />
                </div>
                <h3 className="step-heading">1. Upload Your Excel or CSV Data</h3>
                <p className="step-desc">
                  Connect your data source by uploading Excel (.xlsx, .xls), CSV, or TSV files. 
                  The AI automatically profiles every column, detects Thai encodings (CP874, UTF-8), and flags personal data (PDPA/PII).
                </p>
                <div className="step-feature-list">
                  <span className="feature-check-item">
                    <Check size={13} className="text-emerald-400" />
                    <span>Auto Type Inference (INTEGER, REAL, DATE, TEXT)</span>
                  </span>
                  <span className="feature-check-item">
                    <Check size={13} className="text-emerald-400" />
                    <span>Auto Encoding & PDPA Privacy Warning</span>
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
                  <span className="mockup-title">AI Deep Analysis Pipeline</span>
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
                    <span>Analyzing patterns & generating safe SQL...</span>
                  </div>
                </div>
              </div>

              <div className="step-card-content">
                <div className="step-badge-icon step-icon-2">
                  <Bot size={20} />
                </div>
                <h3 className="step-heading">2. AI Deep Analysis & Dashboard Generation</h3>
                <p className="step-desc">
                  AI performs deep natural language translation, selects optimal chart types for each metric, 
                  executes queries inside a secure read-only sandbox, and heals SQL automatically if errors occur.
                </p>
                <div className="step-feature-list">
                  <span className="feature-check-item">
                    <Check size={13} className="text-emerald-400" />
                    <span>Agentic Self-Healing Loop (Max 2 Retries)</span>
                  </span>
                  <span className="feature-check-item">
                    <Check size={13} className="text-emerald-400" />
                    <span>Read-Only SQLite Engine Sandbox (Timeout 10s)</span>
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
                  <span className="mockup-title">Complete Dashboard Ready</span>
                </div>
                <div className="mockup-body mockup-dashboard">
                  <div className="kpi-mini-grid">
                    <div className="kpi-mini-card">
                      <span className="kpi-label">ยอดรวม</span>
                      <strong className="kpi-val text-blue-400">2.4M</strong>
                    </div>
                    <div className="kpi-mini-card">
                      <span className="kpi-label">เติบโต</span>
                      <strong className="kpi-val text-emerald-400">+18.5%</strong>
                    </div>
                    <div className="kpi-mini-card">
                      <span className="kpi-label">รายการ</span>
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
                    <span>Complete Dashboard Ready</span>
                  </div>
                </div>
              </div>

              <div className="step-card-content">
                <div className="step-badge-icon step-icon-3">
                  <BarChart3 size={20} />
                </div>
                <h3 className="step-heading">3. Review Insights & Export Dashboard</h3>
                <p className="step-desc">
                  Get a complete interactive dashboard with multiple charts (Bar, Line, Area, Pie), 
                  executive summary in Thai, and export capabilities as 2x Retina PNG or formatted CSV tables.
                </p>
                <div className="step-feature-list">
                  <span className="feature-check-item">
                    <Check size={13} className="text-emerald-400" />
                    <span>Executive Insights without Hallucination</span>
                  </span>
                  <span className="feature-check-item">
                    <Check size={13} className="text-emerald-400" />
                    <span>High-Res 2x Retina PNG & Full CSV Export</span>
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
              จุดเด่นสำคัญของ <span className="gradient-text">DataAgent AI</span>
            </h2>
            <p className="section-subtitle">
              เทคโนโลยีที่ผสานการประมวลผลภาษาธรรมชาติ สถิติเชิงปริมาณ และความปลอดภัยระดับองค์กรเข้าไว้ด้วยกัน
            </p>
          </div>

          <div className="features-grid-cards">
            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-blue">
                <Zap size={22} />
              </div>
              <h4 className="feature-title">Thai Text-to-SQL Translation</h4>
              <p className="feature-desc">
                แปลงคำถามภาษาไทยทั่วไปให้กลายเป็นชุดคำสั่ง SQLite Query ที่แม่นยำ พร้อม Few-Shot Learning 
                เข้าใจบริบทตารางและชื่อคอลัมน์ภาษาไทยได้อย่างเป็นธรรมชาติ
              </p>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-emerald">
                <ShieldCheck size={22} />
              </div>
              <h4 className="feature-title">4-Layer Defense Sandbox</h4>
              <p className="feature-desc">
                รันคำสั่งภายใต้กรงขังความปลอดภัย 4 ชั้น: Pre-validation, AST Sanitizer, 
                SQLite C-Engine `PRAGMA query_only = ON;`, Timeout 10s และจำกัดแถว 500 รายการ
              </p>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-purple">
                <Bot size={22} />
              </div>
              <h4 className="feature-title">Agentic Self-Healing Loop</h4>
              <p className="feature-desc">
                หากคำสั่ง SQL รันไม่ผ่าน AI จะอ่านสาเหตุของข้อผิดพลาดและวิเคราะห์ Schema 
                เพื่อซ่อมแซมคำสั่งให้อัตโนมัติสูงสุด 2 รอบโดยที่ผู้ใช้ไม่ต้องพิมพ์สั่งใหม่
              </p>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-amber">
                <TrendingUp size={22} />
              </div>
              <h4 className="feature-title">Zero-Hallucination Insights</h4>
              <p className="feature-desc">
                รายงานสถิติ ยอดรวม ค่าเฉลี่ย สูงสุด ต่ำสุด สำหรับผู้บริหารอย่างกระชับ 
                ระบุหน่วยจริง (เช่น บาท, ชิ้น, ร้อยละ) ตามข้อมูลในตาราง ไม่มีการมโนตัวเลข
              </p>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-cyan">
                <PieIcon size={22} />
              </div>
              <h4 className="feature-title">Smart Chart Recommender</h4>
              <p className="feature-desc">
                เลือกและสร้างกราฟที่เหมาะสมที่สุดโดยอัตโนมัติ (Bar, Line, Area, Pie Chart) 
                สามารถสลับประเภทกราฟได้ตามใจชอบ และส่งออกภาพ PNG คมชัดสูง 2x Retina
              </p>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-rose">
                <Pin size={22} />
              </div>
              <h4 className="feature-title">Pinned Dashboard & Table Viewer</h4>
              <p className="feature-desc">
                ปักหมุดกราฟและข้อสรุปที่สนใจลงบนหน้าปัดแดชบอร์ดเพื่อพิมพ์เป็นรายงาน PDF 
                พร้อมตารางข้อมูลผลลัพธ์ที่สามารถขยายดูแบบเต็มจอ (Fullscreen) ได้อย่างสบายตา
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. Bottom Call to Action Section */}
      <section className="intro-bottom-cta-section">
        <div className="bottom-cta-container">
          <div className="cta-glow-bg" />
          <div className="cta-content">
            <h2 className="cta-title">
              พร้อมเริ่มต้นวิเคราะห์ข้อมูลของคุณหรือยัง?
            </h2>
            <p className="cta-subtitle">
              สัมผัสประสบการณ์การวิเคราะห์ข้อมูลรูปแบบใหม่ ด้วย AI ผู้ช่วยภาษาไทยที่ใช้งานง่ายและปลอดภัย
            </p>
            <div className="cta-buttons-group">
              <button
                type="button"
                className="cta-primary-btn"
                onClick={() => handleLaunchWithQuery('')}
              >
                <span>เข้าสู่ระบบ DataAgent AI ทันที</span>
                <ArrowRight size={17} />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 6. Footer */}
      <footer className="intro-footer">
        <div className="footer-container">
          <div className="footer-left">
            <div className="footer-brand">
              <Bot size={18} className="text-blue-400" />
              <span>DataAgent AI</span>
            </div>
            <p className="footer-copy">
              ระบบผู้ช่วยวิเคราะห์ข้อมูลอัจฉริยะด้วยภาษาธรรมชาติและสถิติเชิงลึก (Team 04)
            </p>
          </div>
          <div className="footer-right">
            <span>Powered by FastAPI • React • LangChain • Groq AI • SQLite</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
