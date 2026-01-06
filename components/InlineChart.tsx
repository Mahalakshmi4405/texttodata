import React from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface InlineChartProps {
    type: 'bar' | 'line' | 'pie' | 'table';
    data: any[];
    columns: string[];
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

export default function InlineChart({ type, data, columns }: InlineChartProps) {
    if (!data || data.length === 0) {
        return <div className="text-dark-400 text-sm">No data to visualize</div>;
    }

    // For bar and line charts, assume first column is X, second is Y
    const xKey = columns[0];
    const yKey = columns[1] || columns[0];

    if (type === 'table') {
        return (
            <div className="overflow-x-auto mt-3">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-dark-700">
                            {columns.map((col) => (
                                <th key={col} className="text-left p-2 text-dark-300">
                                    {col}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data.slice(0, 10).map((row, idx) => (
                            <tr key={idx} className="border-b border-dark-800 hover:bg-dark-800/50">
                                {columns.map((col) => (
                                    <td key={col} className="p-2 text-dark-200">
                                        {String(row[col])}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
                {data.length > 10 && (
                    <p className="text-xs text-dark-500 mt-2">Showing 10 of {data.length} rows</p>
                )}
            </div>
        );
    }

    if (type === 'bar') {
        return (
            <div className="mt-3">
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={data.slice(0, 20)}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey={xKey} stroke="#9CA3AF" />
                        <YAxis stroke="#9CA3AF" />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                            labelStyle={{ color: '#F3F4F6' }}
                        />
                        <Legend />
                        <Bar dataKey={yKey} fill="#3B82F6" />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        );
    }

    if (type === 'line') {
        return (
            <div className="mt-3">
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={data.slice(0, 50)}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey={xKey} stroke="#9CA3AF" />
                        <YAxis stroke="#9CA3AF" />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                            labelStyle={{ color: '#F3F4F6' }}
                        />
                        <Legend />
                        <Line type="monotone" dataKey={yKey} stroke="#10B981" strokeWidth={2} />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        );
    }

    if (type === 'pie') {
        const pieData = data.slice(0, 8).map((item) => ({
            name: String(item[xKey]),
            value: Number(item[yKey]) || 0
        }));

        return (
            <div className="mt-3">
                <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                        <Pie
                            data={pieData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                        >
                            {pieData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                        />
                        <Legend />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        );
    }

    return null;
}
