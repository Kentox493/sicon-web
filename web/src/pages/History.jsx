import React, { useState } from 'react';
import { Search, Calendar, Filter, Eye, Download, Trash2, MoreVertical, RefreshCw } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Badge } from '../components/common/Badge';

const History = () => {
    // Mock Data
    const scans = [
        { id: 1, target: 'example.com', type: 'Full Scan', status: 'completed', date: '2024-12-30', duration: '5m' },
        { id: 2, target: 'test-site.org', type: 'WAF Only', status: 'completed', date: '2024-12-29', duration: '2m' },
        { id: 3, target: 'shop.local', type: 'Full Scan', status: 'failed', date: '2024-12-29', duration: '1m' },
        { id: 4, target: 'api.dev.io', type: 'Subdomain', status: 'running', date: '2024-12-30', duration: '-' },
        { id: 5, target: 'corp.net', type: 'Port Scan', status: 'completed', date: '2024-12-28', duration: '8m' },
    ];

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-text-primary">Scan History</h1>
                    <p className="text-text-secondary mt-1">Review and manage your past reconnaissance activities.</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="secondary"><Download className="w-4 h-4 mr-2" /> Export All</Button>
                </div>
            </div>

            <Card className="border-accent-primary/20">
                <CardHeader className="flex flex-row items-center justify-between pb-4">
                    <div className="relative w-full max-w-sm">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
                        <Input placeholder="Search scans..." className="pl-9 bg-background-tertiary border-transparent focus:border-accent-primary" />
                    </div>
                    <div className="flex gap-2">
                        <Button variant="ghost" size="icon"><Filter className="w-4 h-4" /></Button>
                        <Button variant="ghost" size="icon"><Calendar className="w-4 h-4" /></Button>
                    </div>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead className="bg-background-tertiary text-text-secondary uppercase text-xs font-semibold">
                                <tr>
                                    <th className="px-6 py-4">Target</th>
                                    <th className="px-6 py-4">Scan Type</th>
                                    <th className="px-6 py-4">Status</th>
                                    <th className="px-6 py-4">Date</th>
                                    <th className="px-6 py-4">Duration</th>
                                    <th className="px-6 py-4 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border/50">
                                {scans.map((scan) => (
                                    <tr key={scan.id} className="hover:bg-background-tertiary/50 transition-colors group">
                                        <td className="px-6 py-4 font-medium text-text-primary">{scan.target}</td>
                                        <td className="px-6 py-4 text-text-secondary">{scan.type}</td>
                                        <td className="px-6 py-4">
                                            <StatusBadge status={scan.status} />
                                        </td>
                                        <td className="px-6 py-4 text-text-secondary">{scan.date}</td>
                                        <td className="px-6 py-4 text-text-secondary font-mono">{scan.duration}</td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <Button variant="ghost" size="icon" className="h-8 w-8 hover:text-accent-primary"><Eye className="w-4 h-4" /></Button>
                                                <Button variant="ghost" size="icon" className="h-8 w-8 hover:text-accent-primary"><RefreshCw className="w-4 h-4" /></Button>
                                                <Button variant="ghost" size="icon" className="h-8 w-8 hover:text-status-danger"><Trash2 className="w-4 h-4" /></Button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="p-4 border-t border-border flex justify-center">
                        <div className="flex gap-2">
                            <Button variant="ghost" size="sm" disabled>Previous</Button>
                            <Button variant="ghost" size="sm" className="bg-accent-primary/10 text-accent-primary">1</Button>
                            <Button variant="ghost" size="sm">2</Button>
                            <Button variant="ghost" size="sm">3</Button>
                            <Button variant="ghost" size="sm">Next</Button>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

const StatusBadge = ({ status }) => {
    const styles = {
        completed: 'bg-status-success/10 text-status-success border-status-success/20',
        running: 'bg-status-warning/10 text-status-warning border-status-warning/20',
        failed: 'bg-status-danger/10 text-status-danger border-status-danger/20',
    };

    return (
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles[status]}`}>
            {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
    );
};

export default History;
