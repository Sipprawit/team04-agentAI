import React, { useState, useEffect, useRef } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  AreaChart,
  Area,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { BarChart3, TrendingUp, PieChart as PieIcon, Layers, Info, Camera, Check } from 'lucide-react';

const COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#6366f1', '#14b8a6'
];

// Custom Tooltip แสดงข้อมูลอย่างละเอียดเมื่อเอาเมาส์ชี้บนกราฟ
const CustomChartTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const dataObj = payload[0].payload;
    const value = payload[0].value;
    const name = dataObj.name || label || "ข้อมูล";
    
    // แสดงหน่วยเฉพาะเมื่อ Backend ส่ง unit มาชัดเจน — ห้ามเดาจากค่าตัวเลข
    const unit = dataObj.unit || '';

    // สำหรับ Pie Chart: recharts ส่ง percent มาใน payload
    const isPieSlice = payload[0].percent !== undefined;
    const realPercent = isPieSlice ? (payload[0].percent * 100).toFixed(1) : null;

    return (
      <div className="custom-chart-tooltip">
        <div className="tooltip-header">
          <Info size={13} className="text-blue-500" />
          <span className="tooltip-title">{name}</span>
        </div>
        <div className="tooltip-body">
          <div className="tooltip-row">
            <span className="tooltip-label">ค่าที่บันทึก:</span>
            <strong className="tooltip-value">
              {typeof value === 'number' ? value.toLocaleString() : value}{unit ? ` ${unit}` : ''}
            </strong>
          </div>
          {isPieSlice && realPercent && (
            <div className="tooltip-row">
              <span className="tooltip-label">สัดส่วน:</span>
              <span>{realPercent}%</span>
            </div>
          )}
          {dataObj.period_of_inv && dataObj.period_of_inv !== name && (
            <div className="tooltip-row">
              <span className="tooltip-label">ระยะเวลา:</span>
              <span>{dataObj.period_of_inv}</span>
            </div>
          )}
          {dataObj.cate_of_busi && dataObj.cate_of_busi !== name && (
            <div className="tooltip-row">
              <span className="tooltip-label">หมวดธุรกิจ:</span>
              <span>{dataObj.cate_of_busi}</span>
            </div>
          )}
          {dataObj.year && (
            <div className="tooltip-row">
              <span className="tooltip-label">ปี พ.ศ.:</span>
              <span>{dataObj.year}</span>
            </div>
          )}
        </div>
      </div>
    );
  }
  return null;
};


export default function ChartRenderer({ visualization }) {
  const initialType = visualization?.recommended_chart || 'bar';
  const [selectedChartType, setSelectedChartType] = useState(initialType);
  const [isExporting, setIsExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  const chartContainerRef = useRef(null);

  useEffect(() => {
    if (visualization?.recommended_chart) {
      setSelectedChartType(visualization.recommended_chart);
    }
  }, [visualization]);

  const handleExportPng = () => {
    if (!chartContainerRef.current || isExporting) return;
    // ค้นหา SVG ของ Recharts โดยตรงภายใน chartContainerRef (ไม่ปนกับไอคอนบน Toolbar)
    const svgElement = chartContainerRef.current.querySelector('svg.recharts-surface') || chartContainerRef.current.querySelector('svg');
    if (!svgElement) return;

    try {
      setIsExporting(true);
      const bbox = svgElement.getBoundingClientRect();
      const width = bbox.width || svgElement.clientWidth || 650;
      const height = bbox.height || svgElement.clientHeight || 290;

      // โคลน SVG เพื่อเซ็ตแอตทริบิวต์และสไตล์โดยไม่กระทบ DOM ปัจจุบัน
      const clone = svgElement.cloneNode(true);
      clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
      clone.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');
      clone.setAttribute('width', width);
      clone.setAttribute('height', height);
      if (!clone.getAttribute('viewBox')) {
        clone.setAttribute('viewBox', `0 0 ${width} ${height}`);
      }

      // ฝัง Font และ Fill สีสำหรับ Text ให้เรนเดอร์ภาษาไทยและตัวเลขได้คมชัด
      const origTexts = svgElement.querySelectorAll('text');
      const cloneTexts = clone.querySelectorAll('text');
      origTexts.forEach((orig, idx) => {
        if (cloneTexts[idx]) {
          const comp = window.getComputedStyle(orig);
          cloneTexts[idx].style.fontFamily = comp.fontFamily || '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
          cloneTexts[idx].style.fontSize = comp.fontSize || '11px';
          cloneTexts[idx].style.fill = comp.fill || '#64748b';
        }
      });

      const svgString = new XMLSerializer().serializeToString(clone);
      const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
      const URL = window.URL || window.webkitURL || window;
      const blobURL = URL.createObjectURL(svgBlob);

      const image = new Image();
      image.onload = () => {
        const canvas = document.createElement('canvas');
        const scale = 2; // Retina 2x คมชัดสูงสำหรับทำสไลด์และรายงาน
        canvas.width = width * scale;
        canvas.height = height * scale;

        const ctx = canvas.getContext('2d');
        // เติมพื้นหลังสีขาวป้องกันปัญหาพื้นหลังโปร่งใส
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.scale(scale, scale);
        ctx.drawImage(image, 0, 0, width, height);

        URL.revokeObjectURL(blobURL);

        const pngUrl = canvas.toDataURL('image/png');
        const downloadLink = document.createElement('a');
        downloadLink.download = `chart_${selectedChartType}_${Date.now()}.png`;
        downloadLink.href = pngUrl;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);

        setIsExporting(false);
        setExportSuccess(true);
        setTimeout(() => setExportSuccess(false), 2000);
      };
      image.onerror = (e) => {
        console.error('Export PNG failed:', e);
        setIsExporting(false);
      };
      image.src = blobURL;
    } catch (err) {
      console.error('Export PNG error:', err);
      setIsExporting(false);
    }
  };

  if (!visualization || visualization.recommended_chart === 'none') {
    return null;
  }

  const { chart_data, labels, values, x_axis_key, y_axis_key, title, value } = visualization;

  // แปลง chart_data ถ้ายังไม่มี
  let data = chart_data;
  if (!data || data.length === 0) {
    if (labels && values && labels.length === values.length) {
      data = labels.map((lbl, i) => ({
        name: lbl,
        value: values[i],
        [x_axis_key || 'name']: lbl,
        [y_axis_key || 'value']: values[i],
      }));
    }
  }

  if (!data || data.length === 0) {
    return null;
  }

  // 1. Summary Card
  if (selectedChartType === 'summary_card') {
    return (
      <div className="chart-wrapper summary-card-box">
        <div className="summary-card-title">{title || 'สรุปสถิติสำคัญ'}</div>
        <div className="summary-card-value">
          {typeof value === 'number' ? value.toLocaleString() : (data[0]?.value?.toLocaleString?.() ?? data[0]?.name)}
        </div>
      </div>
    );
  }

  return (
    <div className="chart-wrapper">
      {/* Chart Header & Interactive Switcher Toolbar */}
      <div className="chart-header-toolbar">
        <div className="chart-type-badge">
          {selectedChartType === 'bar' && (
            <span className="type-badge-inner">
              <BarChart3 size={13} />
              <span>กราฟแท่ง (Bar Chart)</span>
            </span>
          )}
          {selectedChartType === 'line' && (
            <span className="type-badge-inner">
              <TrendingUp size={13} />
              <span>กราฟเส้น (Line Chart)</span>
            </span>
          )}
          {selectedChartType === 'pie' && (
            <span className="type-badge-inner">
              <PieIcon size={13} />
              <span>แผนภูมิวงกลม (Pie Chart)</span>
            </span>
          )}
          {selectedChartType === 'area' && (
            <span className="type-badge-inner">
              <Layers size={13} />
              <span>กราฟพื้นที่ (Area Chart)</span>
            </span>
          )}
        </div>

        <div className="chart-actions-group">
          {/* Chart Switcher Buttons */}
          <div className="chart-switcher-group">
            <button
              className={`chart-switch-btn ${selectedChartType === 'bar' ? 'active' : ''}`}
              onClick={() => setSelectedChartType('bar')}
              title="สลับเป็นกราฟแท่ง (Bar Chart)"
            >
              <BarChart3 size={14} />
            </button>
            <button
              className={`chart-switch-btn ${selectedChartType === 'line' ? 'active' : ''}`}
              onClick={() => setSelectedChartType('line')}
              title="สลับเป็นกราฟเส้น (Line Chart)"
            >
              <TrendingUp size={14} />
            </button>
            <button
              className={`chart-switch-btn ${selectedChartType === 'pie' ? 'active' : ''}`}
              onClick={() => setSelectedChartType('pie')}
              title="สลับเป็นแผนภูมิวงกลม (Pie Chart)"
            >
              <PieIcon size={14} />
            </button>
            <button
              className={`chart-switch-btn ${selectedChartType === 'area' ? 'active' : ''}`}
              onClick={() => setSelectedChartType('area')}
              title="สลับเป็นกราฟพื้นที่ (Area Chart)"
            >
              <Layers size={14} />
            </button>
          </div>

          {/* Export Chart as PNG for Presentation */}
          <button
            type="button"
            className={`chart-export-btn ${exportSuccess ? 'success' : ''}`}
            onClick={handleExportPng}
            disabled={isExporting}
            title="ส่งออกกราฟเป็นรูปภาพ PNG คมชัดสูง (สำหรับทำสไลด์/พรีเซนต์)"
          >
            {exportSuccess ? <Check size={13} /> : <Camera size={13} />}
            <span>{exportSuccess ? 'บันทึกแล้ว' : isExporting ? 'กำลังบันทึก...' : 'ส่งออก PNG'}</span>
          </button>
        </div>
      </div>

      {/* Truncation Notice Banner (กรณีข้อมูลเกิน 20 รายการ หรือจัดกลุ่ม Pie) */}
      {visualization?.is_truncated && (
        <div className="chart-truncation-banner">
          <Info size={13} className="truncation-icon" />
          <span className="truncation-text">
            {visualization.truncation_label || `แสดง ${data.length} รายการแรกจากทั้งหมด ${visualization.total_count || data.length} รายการ`}
            <span className="truncation-hint"> (ดูข้อมูลทั้งหมดได้ในแท็บตารางข้อมูล)</span>
          </span>
        </div>
      )}

      {/* Render Selected Chart Type with Custom Hover Tooltip */}
      <div ref={chartContainerRef} style={{ width: '100%', height: 290 }}>
        {selectedChartType === 'bar' && (
          <ResponsiveContainer>
            <BarChart data={data} margin={{ top: 15, right: 20, left: 10, bottom: 45 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="name"
                tick={{ fill: '#64748b', fontSize: 10 }}
                interval={0}
                angle={-25}
                textAnchor="end"
                height={45}
                tickFormatter={(val) => (val && val.length > 15 ? val.slice(0, 15) + '...' : val)}
              />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip content={<CustomChartTooltip />} />
              <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}

        {selectedChartType === 'line' && (
          <ResponsiveContainer>
            <LineChart data={data} margin={{ top: 15, right: 20, left: 10, bottom: 45 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="name"
                tick={{ fill: '#64748b', fontSize: 10 }}
                interval={0}
                angle={-25}
                textAnchor="end"
                height={45}
                tickFormatter={(val) => (val && val.length > 15 ? val.slice(0, 15) + '...' : val)}
              />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip content={<CustomChartTooltip />} />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#10b981"
                strokeWidth={3}
                dot={{ r: 4, fill: '#10b981' }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}

        {selectedChartType === 'pie' && (() => {
          // กรองข้อมูลที่มีค่า <= 0 ออก เพราะ Pie Chart ไม่ควรมีชิ้นที่ไม่มีค่า
          let pieData = data.filter(d => (d.value || 0) > 0);
          if (pieData.length < 2) {
            return (
              <div className="chart-empty-fallback">
                <PieIcon size={32} className="empty-fallback-icon" />
                <p className="empty-fallback-title">ข้อมูลไม่เพียงพอสำหรับแผนภูมิวงกลม</p>
                <p className="empty-fallback-desc">แผนภูมิวงกลมจำเป็นต้องมีข้อมูลอย่างน้อย 2 รายการที่มีค่ามากกว่า 0</p>
                <button
                  type="button"
                  className="empty-fallback-btn"
                  onClick={() => setSelectedChartType('bar')}
                >
                  <BarChart3 size={13} />
                  <span>สลับดูกราฟแท่ง (Bar Chart)</span>
                </button>
              </div>
            );
          }
          // หากชิ้นข้อมูลมีมากกว่า 8 ชิ้น และยังไม่ได้รวม 'อื่นๆ' ให้รวมชิ้นเล็กเข้าด้วยกัน
          if (pieData.length > 8 && !pieData.some(d => d.name === 'อื่นๆ')) {
            const sorted = [...pieData].sort((a, b) => (b.value || 0) - (a.value || 0));
            const top7 = sorted.slice(0, 7);
            const othersVal = sorted.slice(7).reduce((acc, curr) => acc + (curr.value || 0), 0);
            if (othersVal > 0) {
              pieData = [...top7, { name: 'อื่นๆ', value: othersVal }];
            }
          }
          return (
          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="48%"
                outerRadius={85}
                label={({ name, value, percent }) => {
                  const shortName = name.length > 14 ? name.slice(0, 14) + '...' : name;
                  const fmtVal = typeof value === 'number' ? value.toLocaleString() : value;
                  return `${shortName} (${(percent * 100).toFixed(1)}%, ${fmtVal})`;
                }}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomChartTooltip />} />
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
          );
        })()}

        {selectedChartType === 'area' && (
          <ResponsiveContainer>
            <AreaChart data={data} margin={{ top: 15, right: 20, left: 10, bottom: 35 }}>
              <defs>
                <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="name"
                tick={{ fill: '#64748b', fontSize: 11 }}
                interval={0}
                angle={-20}
                textAnchor="end"
              />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip content={<CustomChartTooltip />} />
              <Area type="monotone" dataKey="value" stroke="#2563eb" fillOpacity={1} fill="url(#colorVal)" />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
