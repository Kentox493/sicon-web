import React, { useState, useEffect } from 'react';
import { FileText, Download, Trash2, RefreshCw, Loader2, FileWarning, Search, Sparkles, File } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Badge } from '../components/common/Badge';
import { scansAPI, reportsAPI, settingsAPI } from '../services/api';

const Reports = () => {
    const [reports, setReports] = useState([]);
    const [scans, setScans] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [generating, setGenerating] = useState(null);
    const [downloading, setDownloading] = useState(null);
    const [hasAiKey, setHasAiKey] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setIsLoading(true);
        try {
            const [reportsData, scansData, settingsData] = await Promise.all([
                reportsAPI.list(),
                scansAPI.list(),
                settingsAPI.get()
            ]);
            setReports(reportsData);
            setScans(scansData.filter(s => s.status === 'completed'));
            setHasAiKey(settingsData.has_gemini_key);
        } catch (error) {
            console.error('Failed to fetch data:', error);
        }
        setIsLoading(false);
    };

    const handleGenerate = async (scanId, useAi = false) => {
        setGenerating({ scanId, useAi });
        try {
            await reportsAPI.generate(scanId, useAi);
            await fetchData();
        } catch (error) {
            console.error('Failed to generate report:', error);
            alert(error.response?.data?.detail || 'Failed to generate report');
        }
        setGenerating(null);
    };

    const handleDownload = async (scanId, target, useAi = false) => {
        setDownloading({ scanId, useAi });
        try {
            const blob = await reportsAPI.download(scanId, useAi);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            const type = useAi ? 'AI' : 'STANDARD';
            a.download = `S1C0N_${type}_${target}_${scanId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Failed to download report:', error);
            alert(error.response?.data?.detail || 'Failed to download report');
        }
        setDownloading(null);
    };

    const handleDelete = async (reportId) => {
        if (!window.confirm('Are you sure you want to delete this report?')) return;

        try {
            await reportsAPI.delete(reportId);
            setReports(reports.filter(r => r.id !== reportId));
        } catch (error) {
            console.error('Failed to delete report:', error);
        }
    };

    const formatFileSize = (bytes) => {
        if (!bytes) return '0 KB';
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return 'N/A';
        return new Date(dateStr).toLocaleDateString('en-US', {
            year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        });
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-text-primary">Reports</h1>
                    <p className="text-text-secondary mt-1">Generate and download PDF reports from your scans.</p>
                </div>
                <Button variant="secondary" onClick={fetchData} disabled={isLoading}>
                    <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} /> Refresh
                </Button>
            </div>

            {/* AI Key Status */}
            {!hasAiKey && (
                <div className="flex items-center gap-3 p-4 rounded-lg bg-status-warning/10 border border-status-warning/20">
                    <Sparkles className="w-5 h-5 text-status-warning" />
                    <div className="flex-1">
                        <p className="text-text-primary font-medium">AI Reports Disabled</p>
                        <p className="text-sm text-text-secondary">Add your Gemini API key in Settings to enable AI-enhanced reports.</p>
                    </div>
                    <a href="/settings" className="text-accent-primary hover:underline text-sm">Configure</a>
                </div>
            )}

            {/* Generate New Report Section */}
            <Card className="border-accent-primary/20">
                <CardHeader>
                    <h2 className="text-lg font-semibold">Generate New Report</h2>
                </CardHeader>
                <CardContent>
                    {scans.length === 0 ? (
                        <p className="text-text-secondary text-center py-4">No completed scans. Run a scan first.</p>
                    ) : (
                        <div className="space-y-4">
                            {scans.map((scan) => (
                                <div key={scan.id} className="flex items-center justify-between p-4 rounded-lg bg-background-tertiary/50 hover:bg-background-tertiary transition-colors border border-border/20">
                                    <div className="min-w-0 flex-1">
                                        <p className="font-mono text-sm text-accent-primary truncate">{scan.target}</p>
                                        <p className="text-xs text-text-secondary mt-1">ID: #{scan.id} • {formatDate(scan.completed_at)}</p>
                                    </div>
                                    <div className="flex gap-2 ml-4">
                                        {/* Standard Report */}
                                        <Button
                                            size="sm"
                                            variant="secondary"
                                            onClick={() => handleDownload(scan.id, scan.target, false)}
                                            disabled={downloading?.scanId === scan.id}
                                        >
                                            {downloading?.scanId === scan.id && !downloading?.useAi ? (
                                                <Loader2 className="w-4 h-4 animate-spin" />
                                            ) : (
                                                <>
                                                    <File className="w-4 h-4 mr-1" />
                                                    Standard
                                                </>
                                            )}
                                        </Button>

                                        {/* AI Report */}
                                        <Button
                                            size="sm"
                                            onClick={() => handleDownload(scan.id, scan.target, true)}
                                            disabled={!hasAiKey || downloading?.scanId === scan.id}
                                            title={!hasAiKey ? 'Configure Gemini API key in Settings' : 'Generate AI-enhanced report'}
                                        >
                                            {downloading?.scanId === scan.id && downloading?.useAi ? (
                                                <Loader2 className="w-4 h-4 animate-spin" />
                                            ) : (
                                                <>
                                                    <Sparkles className="w-4 h-4 mr-1" />
                                                    AI Report
                                                </>
                                            )}
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Existing Reports */}
            <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                    <h2 className="text-lg font-semibold">Generated Reports</h2>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex items-center justify-center py-12">
                            <Loader2 className="w-6 h-6 animate-spin text-accent-primary" />
                        </div>
                    ) : reports.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-12 text-text-secondary">
                            <FileWarning className="w-12 h-12 mb-4 opacity-50" />
                            <p>No reports generated yet.</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {reports.map((report) => {
                                const scan = scans.find(s => s.id === report.scan_id);
                                const isAiReport = report.filename.includes('AI');
                                return (
                                    <div key={report.id} className="flex items-center justify-between p-4 rounded-lg bg-background-tertiary/50 hover:bg-background-tertiary transition-colors border border-border/20 group">
                                        <div className="flex items-center gap-4">
                                            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${isAiReport ? 'bg-accent-primary/10' : 'bg-status-danger/10'
                                                }`}>
                                                {isAiReport
                                                    ? <Sparkles className="w-6 h-6 text-accent-primary" />
                                                    : <FileText className="w-6 h-6 text-status-danger" />
                                                }
                                            </div>
                                            <div>
                                                <p className="font-medium text-text-primary">{report.filename}</p>
                                                <div className="flex items-center gap-3 mt-1 text-sm text-text-secondary">
                                                    <span>{formatFileSize(report.file_size)}</span>
                                                    <span>•</span>
                                                    <span>{formatDate(report.created_at)}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="opacity-0 group-hover:opacity-100 hover:text-status-danger"
                                            onClick={() => handleDelete(report.id)}
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </Button>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
};

export default Reports;
