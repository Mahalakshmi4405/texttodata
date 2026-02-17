// Data Visualization Component

'use client';

import React from 'react';
import {
    BarChart,
    Bar,
    LineChart,
    Line,
    PieChart,
    Pie,
    ScatterChart,
    Scatter,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';

// COLORS constant replaced below

interface DataVisualizationProps {
    data: any[];
    visualizationType: 'table' | 'bar' | 'line' | 'pie' | 'scatter';
    sqlQuery?: string;
}

const COLORS = [
    '#3B82F6', // Blue
    '#8B5CF6', // Purple
    '#14B8A6', // Teal
    '#EC4899', // Pink
    '#F59E0B', // Amber
    '#10B981', // Emerald
];

export default function DataVisualization({
    data,
    visualizationType,
    sqlQuery,
}: DataVisualizationProps) {
    if (!data || data.length === 0) {
        return (
            <div className="chart-container text-center py-12">
                <p className="text-dark-400">No data to display</p>
            </div>
        );
    }

    const columns = Object.keys(data[0]);

    // Intelligent axis detection
    const determineAxes = () => {
        if (!data || data.length === 0) return { xKey: '', yKey: '' };

        const sample = data[0];
        const keys = Object.keys(sample);

        // Find best numeric key for Y Axis (price, amount, quantity, etc.)
        let yKey = keys.find(k =>
            typeof sample[k] === 'number' &&
            ['price', 'sales', 'amount', 'total', 'quantity', 'cost', 'revenue', 'profit'].some(term => k.toLowerCase().includes(term))
        );

        // Fallback: any number
        if (!yKey) {
            yKey = keys.find(k => typeof sample[k] === 'number');
        }

        // Find best string key for X Axis (product, name, date, category)
        let xKey = keys.find(k =>
            typeof sample[k] === 'string' &&
            ['product', 'name', 'category', 'date', 'month', 'year', 'time'].some(term => k.toLowerCase().includes(term))
        );

        // Fallback: any string, or just first key if not yKey
        if (!xKey) {
            xKey = keys.find(k => typeof sample[k] === 'string' && k !== yKey) || keys[0];
        }

        // Safety: if we still don't have a yKey, reuse something just to show data
        if (!yKey) yKey = keys[1] || keys[0];

        return { xKey, yKey };
    };

    const axes = determineAxes();

    // Render based on visualization type
    const renderVisualization = () => {
        switch (visualizationType) {
            case 'bar':
                return renderBarChart();
            case 'line':
                return renderLineChart();
            case 'pie':
                return renderPieChart();
            case 'scatter':
                return renderScatterChart();
            default:
                return renderTable();
        }
    };

    // Helper to format chart tick values
    const formatAxisTick = (value: any) => {
        if (typeof value !== 'string') return value;

        // Check if it looks like a date/time
        // ISO format or common date formats
        if (value.match(/^\d{4}-\d{2}-\d{2}/) || value.match(/[A-Za-z]{3} \d{1,2}, \d{4}/)) {
            try {
                const date = new Date(value);
                if (!isNaN(date.getTime())) {
                    // If it's a full timestamp include time if relevant, otherwise just date
                    if (value.includes('T') || value.includes(':')) {
                        // Check if time is 00:00:00, then omit it
                        if (value.includes('00:00:00') || date.getHours() + date.getMinutes() === 0) {
                            return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: '2-digit' });
                        }
                        // Short date + time for dense data
                        return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
                    }
                    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
                }
            } catch (e) {
                return value;
            }
        }

        // Truncate long strings
        if (value.length > 15) {
            return value.substring(0, 12) + '...';
        }

        return value;
    };

    const renderBarChart = () => {
        const { xKey, yKey } = axes;

        return (
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 50 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis
                        dataKey={xKey}
                        stroke="#94a3b8"
                        tickFormatter={formatAxisTick}
                        angle={-45}
                        textAnchor="end"
                        height={60}
                        interval={0}
                    />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                        }}
                        labelFormatter={formatAxisTick}
                    />
                    <Legend verticalAlign="top" />
                    <Bar dataKey={yKey} fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                </BarChart>
            </ResponsiveContainer>
        );
    };

    const renderLineChart = () => {
        const { xKey, yKey } = axes;

        return (
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 50 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis
                        dataKey={xKey}
                        stroke="#94a3b8"
                        tickFormatter={formatAxisTick}
                        angle={-45}
                        textAnchor="end"
                        height={60}
                    />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                        }}
                        labelFormatter={formatAxisTick}
                    />
                    <Legend verticalAlign="top" />
                    <Line
                        type="monotone"
                        dataKey={yKey}
                        stroke="#0ea5e9"
                        strokeWidth={3}
                        dot={{ fill: '#0ea5e9', r: 4 }}
                        activeDot={{ r: 6 }}
                    />
                </LineChart>
            </ResponsiveContainer>
        );
    };

    const renderPieChart = () => {
        const nameKey = axes.xKey;
        const valueKey = axes.yKey;

        const pieData = data.map((item) => ({
            name: item[nameKey],
            value: Number(item[valueKey]) || 0,
        }));

        return (
            <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                    <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                        outerRadius={120}
                        fill="#8884d8"
                        dataKey="value"
                    >
                        {pieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                        }}
                    />
                </PieChart>
            </ResponsiveContainer>
        );
    };

    const renderScatterChart = () => {
        if (columns.length < 2) return renderTable();

        const { xKey, yKey } = axes;

        return (
            <ResponsiveContainer width="100%" height="100%">
                <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey={xKey} stroke="#94a3b8" name={xKey} />
                    <YAxis dataKey={yKey} stroke="#94a3b8" name={yKey} />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                        }}
                        cursor={{ strokeDasharray: '3 3' }}
                    />
                    <Scatter name="Data" data={data} fill="#0ea5e9" />
                </ScatterChart>
            </ResponsiveContainer>
        );
    };

    const renderTable = () => {
        // Limit to first 100 rows for performance
        const displayData = data.slice(0, 100);

        return (
            <div className="overflow-auto h-full rounded-lg border border-white/10 relative">
                <table className="w-full text-sm">
                    <thead className="sticky top-0 z-10 bg-[#0F172A] shadow-sm">
                        <tr className="bg-[#1E293B] border-b border-white/10">
                            {columns.map((col) => (
                                <th
                                    key={col}
                                    className="px-4 py-2 text-left font-medium text-slate-300 border-b border-white/10"
                                >
                                    {col.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {displayData.map((row, idx) => (
                            <tr
                                key={idx}
                                className="border-b border-white/5 hover:bg-white/5 transition-colors"
                            >
                                {columns.map((col) => (
                                    <td key={col} className="px-4 py-2 text-slate-300">
                                        {formatAxisTick(row[col])}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>

                {data.length > 100 && (
                    <div className="text-center py-4 text-slate-500 text-xs bg-[#1E293B]/50">
                        Showing first 100 of {data.length} rows
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="flex flex-col h-full gap-4">
            {sqlQuery && (
                <div className="p-4 bg-[#1E293B] text-slate-200 rounded-2xl border border-white/10 text-sm flex-none">
                    <p className="text-slate-400 mb-1">SQL Query:</p>
                    <code className="text-primary font-mono">{sqlQuery}</code>
                </div>
            )}

            <div className="chart-container flex-1 min-h-0 relative">{renderVisualization()}</div>

            <div className="flex items-center justify-between text-xs text-slate-500 flex-none">
                <span>{data.length} rows returned</span>
                <span>Visualization: {visualizationType}</span>
            </div>
        </div>
    );
}
