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

interface DataVisualizationProps {
    data: any[];
    visualizationType: 'table' | 'bar' | 'line' | 'pie' | 'scatter';
    sqlQuery?: string;
}

const COLORS = [
    '#0ea5e9', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981',
    '#3b82f6', '#a855f7', '#f43f5e', '#eab308', '#14b8a6',
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

    const renderBarChart = () => {
        const xKey = columns[0];
        const yKey = columns[1] || columns[0];

        return (
            <ResponsiveContainer width="100%" height={400}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey={xKey} stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                        }}
                    />
                    <Legend />
                    <Bar dataKey={yKey} fill="#0ea5e9" radius={[8, 8, 0, 0]} />
                </BarChart>
            </ResponsiveContainer>
        );
    };

    const renderLineChart = () => {
        const xKey = columns[0];
        const yKey = columns[1] || columns[0];

        return (
            <ResponsiveContainer width="100%" height={400}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey={xKey} stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                        }}
                    />
                    <Legend />
                    <Line
                        type="monotone"
                        dataKey={yKey}
                        stroke="#0ea5e9"
                        strokeWidth={3}
                        dot={{ fill: '#0ea5e9', r: 5 }}
                    />
                </LineChart>
            </ResponsiveContainer>
        );
    };

    const renderPieChart = () => {
        const nameKey = columns[0];
        const valueKey = columns[1] || columns[0];

        const pieData = data.map((item) => ({
            name: item[nameKey],
            value: Number(item[valueKey]) || 0,
        }));

        return (
            <ResponsiveContainer width="100%" height={400}>
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

        const xKey = columns[0];
        const yKey = columns[1];

        return (
            <ResponsiveContainer width="100%" height={400}>
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
            <div className="overflow-x-auto">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-dark-700">
                            {columns.map((col) => (
                                <th
                                    key={col}
                                    className="px-4 py-3 text-left font-semibold text-dark-300 bg-dark-800/50"
                                >
                                    {col}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {displayData.map((row, idx) => (
                            <tr
                                key={idx}
                                className="border-b border-dark-800 hover:bg-dark-800/30 transition-colors"
                            >
                                {columns.map((col) => (
                                    <td key={col} className="px-4 py-3 text-dark-400">
                                        {typeof row[col] === 'number'
                                            ? row[col].toLocaleString()
                                            : String(row[col] || '-')}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>

                {data.length > 100 && (
                    <div className="text-center py-4 text-dark-500 text-sm">
                        Showing first 100 of {data.length} rows
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="space-y-4">
            {sqlQuery && (
                <div className="p-4 rounded-lg glass-dark text-sm">
                    <p className="text-dark-400 mb-1">SQL Query:</p>
                    <code className="text-primary-300 font-mono">{sqlQuery}</code>
                </div>
            )}

            <div className="chart-container">{renderVisualization()}</div>

            <div className="flex items-center justify-between text-xs text-dark-500">
                <span>{data.length} rows returned</span>
                <span>Visualization: {visualizationType}</span>
            </div>
        </div>
    );
}
