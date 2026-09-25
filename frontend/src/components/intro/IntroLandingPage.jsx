import React from 'react';
import {
  ArrowRight,
  FileSpreadsheet,
  Bot,
  BarChart3,
  ShieldCheck,
  Zap,
  TrendingUp,
  PieChart as PieIcon,
  CheckCircle2
} from 'lucide-react';
import './IntroLandingPage.css';

export default function IntroLandingPage({ onStartApp }) {
  const handleStart = () => {
    if (onStartApp) {
      onStartApp('');
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

      {/* 1. Top Navigation Bar (Clean & Minimalist) */}
      <header className="intro-navbar">
        <div className="intro-nav-container">
          <div className="intro-brand">
            <div className="brand-logo-glow">
              <Bot size={20} className="brand-logo-icon" />
            </div>
            <div className="brand-titles">
              <span className="brand-name">DataAgent AI</span>
              <span className="brand-tag">Team 04</span>
            </div>
          </div>

          <nav className="intro-nav-links">
            <button
              type="button"
              onClick={() => scrollToSection('how-it-works')}
              className="nav-link-btn"
            >
              ขั้นตอนการใช้งาน
            </button>
            <button
              type="button"
              onClick={() => scrollToSection('features')}
              className="nav-link-btn"
            >
              จุดเด่นระบบ
            </button>
          </nav>
        </div>
      </header>

      {/* 2. Hero Section */}
      <section className="intro-hero-section">
        <div className="intro-hero-container">
          {/* Subtle Status Pill */}
          <div className="hero-pill-badge">
            <span className="pill-dot" />
            <span>AI Data Analyst Assistant • Team 04</span>
          </div>

          {/* Elegant Headline */}
          <h1 className="hero-main-title">
            ระบบวิเคราะห์ข้อมูลอัจฉริยะ <br />
            <span className="gradient-text">ด้วยการสั่งงานภาษาไทย</span>
          </h1>

          {/* Concise Subtitle */}
          <p className="hero-subtitle">
            แปลงคำถามภาษาไทยเป็นคำสั่ง SQL สรุปผลทางสถิติ และสร้างแผนภูมิอัตโนมัติบนสภาพแวดล้อมที่ปลอดภัย
          </p>

          {/* Single Smooth Start CTA Button */}
          <div className="hero-cta-wrapper">
            <button
              type="button"
              className="hero-start-btn"
              onClick={handleStart}
            >
              <span>Start</span>
              <ArrowRight size={18} className="start-btn-icon" />
            </button>
          </div>

          {/* Understated Highlights */}
          <div className="hero-trust-indicators">
            <div className="trust-item">
              <Zap size={15} className="trust-icon text-blue-400" />
              <span className="trust-label">NL-to-SQL Engine</span>
            </div>
            <div className="trust-divider" />
            <div className="trust-item">
              <ShieldCheck size={15} className="trust-icon text-indigo-400" />
              <span className="trust-label">Secure Sandbox</span>
            </div>
            <div className="trust-divider" />
            <div className="trust-item">
              <BarChart3 size={15} className="trust-icon text-teal-400" />
              <span className="trust-label">Automated Insights</span>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Section 1: ขั้นตอนการใช้งาน (How It Works) */}
      <section id="how-it-works" className="intro-steps-section">
        <div className="steps-container">
          <div className="section-header-centered">
            <span className="section-pill-tag">WORKFLOW</span>
            <h2 className="section-title">
              ขั้นตอนการใช้งาน <span className="highlight-text">3 ขั้นตอน</span>
            </h2>
            <p className="section-subtitle">
              เริ่มต้นเปลี่ยนชุดข้อมูลสเปรดชีตให้กลายเป็นรายงานและแดชบอร์ดสรุปผลได้อย่างรวดเร็ว
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
                  <span className="mockup-title">dataset.xlsx</span>
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
                    <FileSpreadsheet size={14} className="text-blue-400" />
                    <span>CSV, Excel (.xlsx, .xls)</span>
                  </div>
                </div>
              </div>

              <div className="step-card-content">
                <div className="step-badge-icon step-icon-1">
                  <FileSpreadsheet size={18} />
                </div>
                <h3 className="step-heading">1. นำเข้าชุดข้อมูล</h3>
                <p className="step-desc">
                  อัปโหลดไฟล์ CSV หรือ Excel ระบบจะตรวจสอบประเภทของข้อมูลและเข้ารหัสภาษาไทยให้อัตโนมัติ พร้อมตรวจจับความปลอดภัย
                </p>
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
                  <span className="mockup-title">AI Processing Pipeline</span>
                </div>
                <div className="mockup-body mockup-analysis">
                  <div className="radar-circle-center">
                    <div className="radar-pulse" />
                    <Bot size={22} className="radar-sparkle text-indigo-400" />
                  </div>
                  <div className="radar-nodes">
                    <div className="radar-node node-charts">Charts</div>
                    <div className="radar-node node-insights">Insights</div>
                    <div className="radar-node node-kpis">KPIs</div>
                    <div className="radar-node node-sql">SQL Sandbox</div>
                  </div>
                  <div className="mockup-status-badge">
                    <span>Query execution inside read-only sandbox</span>
                  </div>
                </div>
              </div>

              <div className="step-card-content">
                <div className="step-badge-icon step-icon-2">
                  <Bot size={18} />
                </div>
                <h3 className="step-heading">2. ประมวลผลคำถามด้วย AI</h3>
                <p className="step-desc">
                  แปลงคำถามภาษาไทยเป็นคำสั่ง SQL ผ่านโมเดลภาษา พร้อมตรวจสอบและประมวลผลบนฐานข้อมูลในสภาพแวดล้อมที่ปลอดภัย
                </p>
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
                  <span className="mockup-title">Dashboard Preview</span>
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
                      <strong className="kpi-val text-indigo-400">12,847</strong>
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
                    <CheckCircle2 size={13} className="text-teal-400" />
                    <span>Dashboard Ready</span>
                  </div>
                </div>
              </div>

              <div className="step-card-content">
                <div className="step-badge-icon step-icon-3">
                  <BarChart3 size={18} />
                </div>
                <h3 className="step-heading">3. สรุปผลและแสดงแดชบอร์ด</h3>
                <p className="step-desc">
                  รับคำตอบพร้อมแผนภูมิสถิติที่เหมาะสม ตารางผลลัพธ์ที่ค้นหาได้ และปักหมุดข้อมูลลงบนแดชบอร์ดเพื่อวิเคราะห์ต่อ
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Section 2: จุดเด่นระบบ (Features & Capabilities) */}
      <section id="features" className="intro-features-section">
        <div className="features-container">
          <div className="section-header-centered">
            <span className="section-pill-tag">CAPABILITIES</span>
            <h2 className="section-title">
              จุดเด่นสำคัญของ <span className="gradient-text">DataAgent AI</span>
            </h2>
            <p className="section-subtitle">
              เทคโนโลยีการประมวลผลภาษาธรรมชาติและระบบความปลอดภัยสำหรับงานวิเคราะห์ข้อมูล
            </p>
          </div>

          <div className="features-grid-cards">
            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-blue">
                <Zap size={20} />
              </div>
              <h4 className="feature-title">Thai Text-to-SQL Translation</h4>
              <p className="feature-desc">
                แปลงคำถามภาษาไทยทั่วไปเป็นคำสั่ง SQL ที่แม่นยำ พร้อม Few-Shot Learning เข้าใจชื่อตารางและคอลัมน์ภาษาไทยอย่างเป็นธรรมชาติ
              </p>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-indigo">
                <ShieldCheck size={20} />
              </div>
              <h4 className="feature-title">Secure Read-Only Sandbox</h4>
              <p className="feature-desc">
                รันคำสั่งภายใต้การป้องกัน 4 ชั้น ป้องกันคำสั่งดัดแปลงหรือลบข้อมูล ประมวลผลแบบ Read-Only และมีระบบจำกัดเวลาทำงาน
              </p>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-teal">
                <PieIcon size={20} />
              </div>
              <h4 className="feature-title">Automated Chart Selection</h4>
              <p className="feature-desc">
                เลือกและสร้างแผนภูมิแท่ง แผนภูมิเส้น หรือแผนภูมิวงกลมที่เหมาะสมกับลักษณะตัวเลขและข้อมูลสถิติให้อัตโนมัติ
              </p>
            </div>

            <div className="feature-highlight-card">
              <div className="feature-card-icon icon-blue">
                <TrendingUp size={20} />
              </div>
              <h4 className="feature-title">Interactive Dashboard & Export</h4>
              <p className="feature-desc">
                ปักหมุดกราฟเพื่อสร้างแดชบอร์ดสรุปผลภาพรวม ตรวจสอบข้อมูลดิบในตาราง และดาวน์โหลดไฟล์ผลลัพธ์เป็น CSV (UTF-8 BOM) ได้ทันที
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. Minimalist Professional Footer */}
      <footer className="intro-footer">
        <div className="footer-container">
          <div className="footer-left">
            <div className="footer-brand">
              <Bot size={16} className="text-blue-400" />
              <span>DataAgent AI</span>
            </div>
            <p className="footer-copy">
              ระบบผู้ช่วยวิเคราะห์ข้อมูลอัจฉริยะ (Team 04)
            </p>
          </div>
          <div className="footer-right">
            <span>Powered by FastAPI • React • LangChain • SQLite</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
