import React, { useState, useEffect } from 'react';
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
import { BarChart3, TrendingUp, PieChart as PieIcon, Layers, Info } from 'lucide-react';

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
    
    // ตรวจสอบหน่วย เช่น ร้อยละ หรือ %
    const unit = dataObj.unit || (typeof value === 'number' && value <= 100 ? '%' : '');

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
              {typeof value === 'number' ? value.toLocaleString() : value} {unit}
            </strong>
          </div>
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

  useEffect(() => {
    if (visualization?.recommended_chart) {
      setSelectedChartType(visualization.recommended_chart);
    }
  }, [visualization]);

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
      </div>

      {/* Render Selected Chart Type with Custom Hover Tooltip */}
      <div style={{ width: '100%', height: 290 }}>
        {selectedChartType === 'bar' && (
          <ResponsiveContainer>
            <BarChart data={data} margin={{ top: 15, right: 20, left: 10, bottom: 35 }}>
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
            <LineChart data={data} margin={{ top: 15, right: 20, left: 10, bottom: 35 }}>
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

        {selectedChartType === 'pie' && (
          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="48%"
                outerRadius={85}
                label={({ name, percent }) => `${name.length > 15 ? name.slice(0, 15) + '...' : name} (${(percent * 100).toFixed(0)}%)`}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomChartTooltip />} />
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        )}

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
