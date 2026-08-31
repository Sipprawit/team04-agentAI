import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

const COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#6366f1', '#14b8a6'
];

export default function ChartRenderer({ visualization }) {
  if (!visualization || visualization.recommended_chart === 'none') {
    return null;
  }

  const { recommended_chart, chart_data, labels, values, x_axis_key, y_axis_key, title, value } = visualization;

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
  if (recommended_chart === 'summary_card') {
    return (
      <div className="chart-wrapper summary-card-box">
        <div className="summary-card-title">{title || 'สรุปสถิติสำคัญ'}</div>
        <div className="summary-card-value">
          {typeof value === 'number' ? value.toLocaleString() : (data[0]?.value?.toLocaleString?.() ?? data[0]?.name)}
        </div>
      </div>
    );
  }

  // 2. Bar Chart
  if (recommended_chart === 'bar') {
    return (
      <div className="chart-wrapper">
        <div className="chart-header">
          <span className="chart-type-badge">📊 กราฟแท่ง (Bar Chart)</span>
        </div>
        <div style={{ width: '100%', height: 280 }}>
          <ResponsiveContainer>
            <BarChart data={data} margin={{ top: 15, right: 20, left: 10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="name"
                tick={{ fill: '#64748b', fontSize: 11 }}
                interval={0}
                angle={-20}
                textAnchor="end"
              />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#ffffff', borderRadius: 8, border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                formatter={(val) => [typeof val === 'number' ? val.toLocaleString() : val, 'ค่า']}
              />
              <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  // 3. Line Chart
  if (recommended_chart === 'line') {
    return (
      <div className="chart-wrapper">
        <div className="chart-header">
          <span className="chart-type-badge">📈 กราฟเส้นแนวโน้ม (Line Chart)</span>
        </div>
        <div style={{ width: '100%', height: 280 }}>
          <ResponsiveContainer>
            <LineChart data={data} margin={{ top: 15, right: 20, left: 10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="name"
                tick={{ fill: '#64748b', fontSize: 11 }}
                interval={0}
                angle={-20}
                textAnchor="end"
              />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#ffffff', borderRadius: 8, border: '1px solid #e2e8f0' }}
                formatter={(val) => [typeof val === 'number' ? val.toLocaleString() : val, 'ค่า']}
              />
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
        </div>
      </div>
    );
  }

  // 4. Pie Chart
  if (recommended_chart === 'pie') {
    return (
      <div className="chart-wrapper">
        <div className="chart-header">
          <span className="chart-type-badge">🥧 แผนภูมิวงกลม (Pie Chart)</span>
        </div>
        <div style={{ width: '100%', height: 280 }}>
          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={85}
                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#ffffff', borderRadius: 8, border: '1px solid #e2e8f0' }}
                formatter={(val) => [typeof val === 'number' ? val.toLocaleString() : val, 'ค่า']}
              />
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  return null;
}
