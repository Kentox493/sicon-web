import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, Activity, Globe, Shield, Search, Server, FileCode, Layers, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { useScanStore } from '../store/scanStore';

const Dashboard = () => {
    const navigate = useNavigate();
    const { startScan, isLoading, error, clearError } = useScanStore();

    const [targetUrl, setTargetUrl] = useState('');
    const [scanOptions, setScanOptions] = useState({
        waf: true,
        port: true,
        subdo: true,
        cms: true,
        tech: true,
        dir: true,
        wp: false,
    });
    const [advancedOpen, setAdvancedOpen] = useState(false);
    const [proxy, setProxy] = useState('');
    const [userAgent, setUserAgent] = useState('');

    const toggleOption = (key) => {
        setScanOptions(prev => ({ ...prev, [key]: !prev[key] }));
    };

    const handleStartScan = async () => {
        if (!targetUrl) return;
        clearError();

        const options = {
            ...scanOptions,
            proxy: proxy || null,
            user_agent: userAgent || null,
            use_tor: false,
        };

        const scan = await startScan(targetUrl, options);
        if (scan) {
            navigate(`/scan?id=${scan.id}`);
        }
    };

    const stats = [
        { label: 'Total Scans', value: '—', icon: Activity, color: 'text-blue-400' },
        { label: 'Vulnerabilities', value: '—', icon: Shield, color: 'text-red-400' },
        { label: 'Domains', value: '—', icon: Globe, color: 'text-green-400' },
    ];

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-text-primary">Dashboard</h1>
                    <p className="text-text-secondary mt-1">Welcome back, ready for reconnaissance?</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {stats.map((stat, index) => (
                    <Card key={index} className="hover:border-accent-primary/50 transition-colors cursor-default">
                        <CardContent className="p-6 flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-text-secondary">{stat.label}</p>
                                <div className="text-3xl font-bold text-text-primary mt-2">{stat.value}</div>
                            </div>
                            <div className={`p-3 rounded-full bg-background-tertiary ${stat.color}`}>
                                <stat.icon className="w-6 h-6" />
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            <Card className="border-accent-primary/20">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Search className="w-6 h-6 text-accent-primary" />
                        New Reconnaissance Scan
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                    {error && (
                        <div className="flex items-center gap-2 p-3 rounded-lg bg-status-danger/10 border border-status-danger/20 text-status-danger text-sm">
                            <AlertCircle className="w-4 h-4" />
                            {error}
                        </div>
                    )}

                    <div className="flex flex-col gap-4">
                        <div className="flex-1">
                            <label className="text-sm font-medium text-text-secondary mb-2 block">Target URL / Domain</label>
                            <Input
                                placeholder="example.com or https://example.com"
                                className="h-12 text-lg font-mono placeholder:text-text-secondary/50"
                                value={targetUrl}
                                onChange={(e) => setTargetUrl(e.target.value)}
                            />
                        </div>
                        <div>
                            <Button
                                size="lg"
                                className="w-full font-bold text-base shadow-lg shadow-accent-primary/20 hover:shadow-accent-primary/40 transition-all"
                                onClick={handleStartScan}
                                disabled={!targetUrl}
                                isLoading={isLoading}
                            >
                                <Play className="w-5 h-5 mr-2" />
                                START SCAN
                            </Button>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <label className="text-sm font-medium text-text-secondary block">Scan Modules</label>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <ScanOption label="WAF Detection" active={scanOptions.waf} onClick={() => toggleOption('waf')} icon={Shield} />
                            <ScanOption label="Port Scan" active={scanOptions.port} onClick={() => toggleOption('port')} icon={Server} />
                            <ScanOption label="Subdomains" active={scanOptions.subdo} onClick={() => toggleOption('subdo')} icon={Globe} />
                            <ScanOption label="CMS Detect" active={scanOptions.cms} onClick={() => toggleOption('cms')} icon={Layers} />
                            <ScanOption label="Tech Stack" active={scanOptions.tech} onClick={() => toggleOption('tech')} icon={FileCode} />
                            <ScanOption label="Directories" active={scanOptions.dir} onClick={() => toggleOption('dir')} icon={Search} />
                            <ScanOption label="WordPress Enum" active={scanOptions.wp} onClick={() => toggleOption('wp')} icon={FileCode} className="col-span-2 md:col-span-2" />
                        </div>
                    </div>

                    <div className="pt-4 border-t border-border">
                        <Button variant="ghost" size="sm" className="text-text-secondary" onClick={() => setAdvancedOpen(!advancedOpen)}>
                            {advancedOpen ? 'Hide' : 'Show'} Advanced Options
                        </Button>

                        {advancedOpen && (
                            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 animate-in slide-in-from-top-2">
                                <div>
                                    <label className="text-sm text-text-secondary mb-1 block">Proxy URL</label>
                                    <Input placeholder="socks5://127.0.0.1:9050" value={proxy} onChange={(e) => setProxy(e.target.value)} />
                                </div>
                                <div>
                                    <label className="text-sm text-text-secondary mb-1 block">Custom User Agent</label>
                                    <Input placeholder="Mozilla/5.0..." value={userAgent} onChange={(e) => setUserAgent(e.target.value)} />
                                </div>
                            </div>
                        )}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

const ScanOption = ({ label, active, onClick, icon: Icon, className }) => (
    <button
        onClick={onClick}
        className={`
      flex items-center gap-3 p-4 rounded-lg border transition-all duration-200 text-left
      ${active
                ? 'bg-accent-primary/10 border-accent-primary text-text-primary shadow-[0_0_10px_rgba(37,211,102,0.1)]'
                : 'bg-background-secondary border-border text-text-secondary hover:border-text-secondary hover:bg-background-tertiary'}
      ${className}
    `}
    >
        <div className={`p-2 rounded-md ${active ? 'bg-accent-primary text-background-primary' : 'bg-background-tertiary'}`}>
            <Icon className="w-5 h-5" />
        </div>
        <span className="font-medium text-sm">{label}</span>
    </button>
);

export default Dashboard;
