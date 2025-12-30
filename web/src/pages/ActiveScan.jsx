import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Shield, Server, Globe, Layers, FileCode, Folder, Loader2, CheckCircle2, XCircle, Clock, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { useScanStore } from '../store/scanStore';
import { cn } from '../utils/cn';

const tabs = [
    { id: 'waf', label: 'WAF', icon: Shield },
    { id: 'port', label: 'Ports', icon: Server },
    { id: 'subdo', label: 'Subdomains', icon: Globe },
    { id: 'cms', label: 'CMS', icon: Layers },
    { id: 'tech', label: 'Tech', icon: FileCode },
    { id: 'dir', label: 'Directories', icon: Folder },
];

const ActiveScan = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const scanId = searchParams.get('id');

    const { currentScan, getScan, isLoading, error } = useScanStore();
    const [activeTab, setActiveTab] = useState('waf');

    // Poll for scan updates
    useEffect(() => {
        if (!scanId) {
            navigate('/');
            return;
        }

        // Initial fetch
        getScan(parseInt(scanId));

        // Poll every 2 seconds while scan is running
        const interval = setInterval(async () => {
            const scan = await getScan(parseInt(scanId));
            if (scan && (scan.status === 'completed' || scan.status === 'failed')) {
                clearInterval(interval);
            }
        }, 2000);

        return () => clearInterval(interval);
    }, [scanId, getScan, navigate]);

    if (isLoading && !currentScan) {
        return (
            <div className="flex items-center justify-center h-96">
                <Loader2 className="w-8 h-8 animate-spin text-accent-primary" />
            </div>
        );
    }

    if (error || !currentScan) {
        return (
            <div className="flex flex-col items-center justify-center h-96 gap-4">
                <AlertCircle className="w-12 h-12 text-status-danger" />
                <p className="text-text-secondary">{error || 'Scan not found'}</p>
                <Button onClick={() => navigate('/')}>Back to Dashboard</Button>
            </div>
        );
    }

    const { target, status, progress, current_module, results, created_at } = currentScan;

    const modules = [
        { name: 'waf', label: 'WAF', status: getModuleStatus('waf', current_module, results, status) },
        { name: 'port', label: 'Ports', status: getModuleStatus('port', current_module, results, status) },
        { name: 'subdo', label: 'Subdomains', status: getModuleStatus('subdo', current_module, results, status) },
        { name: 'cms', label: 'CMS', status: getModuleStatus('cms', current_module, results, status) },
        { name: 'tech', label: 'Tech', status: getModuleStatus('tech', current_module, results, status) },
        { name: 'dir', label: 'Dir', status: getModuleStatus('dir', current_module, results, status) },
    ];

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-text-primary">
                        {status === 'running' ? 'Scanning...' : status === 'completed' ? 'Scan Complete' : 'Scan Failed'}
                    </h1>
                    <p className="text-accent-primary font-mono mt-1">{target}</p>
                </div>
                <Badge variant="outline" className="px-3 py-1">ID: #{currentScan.id}</Badge>
            </div>

            {/* Progress Card */}
            <Card className="border-accent-primary/20">
                <CardHeader className="pb-2">
                    <div className="flex justify-between items-center">
                        <CardTitle className="text-lg flex items-center gap-2">
                            {status === 'running' && <Loader2 className="w-5 h-5 animate-spin text-accent-primary" />}
                            {status === 'completed' && <CheckCircle2 className="w-5 h-5 text-status-success" />}
                            {status === 'failed' && <XCircle className="w-5 h-5 text-status-danger" />}
                            Scan Progress
                        </CardTitle>
                        <div className="flex items-center gap-2 text-sm text-text-secondary">
                            <Clock className="w-4 h-4" />
                            <span>{new Date(created_at).toLocaleString()}</span>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="w-full bg-background-tertiary rounded-full h-4 mb-6 overflow-hidden">
                        <div
                            className="bg-accent-primary h-full transition-all duration-500 ease-out relative"
                            style={{ width: `${progress}%` }}
                        >
                            {status === 'running' && <div className="absolute inset-0 bg-white/20 animate-pulse" />}
                        </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                        {modules.map((mod) => (
                            <div
                                key={mod.name}
                                className={cn(
                                    "flex items-center gap-2 p-3 rounded-lg border",
                                    mod.status === 'completed' && "bg-status-success/10 border-status-success/20",
                                    mod.status === 'running' && "bg-accent-primary/10 border-accent-primary/20",
                                    mod.status === 'pending' && "bg-background-tertiary border-transparent text-text-secondary",
                                    mod.status === 'failed' && "bg-status-danger/10 border-status-danger/20"
                                )}
                            >
                                <StatusIcon status={mod.status} />
                                <span className="text-sm font-medium">{mod.label}</span>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Results Tabs */}
            <div className="space-y-4">
                <div className="flex overflow-x-auto pb-2 gap-2">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={cn(
                                "flex items-center gap-2 px-4 py-3 rounded-lg border transition-all whitespace-nowrap min-w-[120px]",
                                activeTab === tab.id
                                    ? "bg-accent-primary/10 border-accent-primary text-text-primary"
                                    : "bg-background-secondary border-border text-text-secondary hover:bg-background-tertiary"
                            )}
                        >
                            <tab.icon className={cn("w-4 h-4", activeTab === tab.id && "text-accent-primary")} />
                            <span className="text-sm font-medium">{tab.label}</span>
                        </button>
                    ))}
                </div>

                {/* Results Content */}
                <Card>
                    <CardContent className="p-6">
                        {results && results[activeTab] ? (
                            <ResultContent module={activeTab} data={results[activeTab]} />
                        ) : (
                            <div className="text-center text-text-secondary py-8">
                                {status === 'running' ? 'Waiting for results...' : 'No data available'}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

// Helper to determine module status
function getModuleStatus(moduleName, currentModule, results, scanStatus) {
    if (results && results[moduleName]) return 'completed';
    if (currentModule === moduleName) return 'running';
    if (scanStatus === 'failed') return 'failed';
    return 'pending';
}

const StatusIcon = ({ status }) => {
    switch (status) {
        case 'completed': return <CheckCircle2 className="w-4 h-4 text-status-success" />;
        case 'running': return <Loader2 className="w-4 h-4 animate-spin text-accent-primary" />;
        case 'failed': return <XCircle className="w-4 h-4 text-status-danger" />;
        default: return <div className="w-4 h-4 rounded-full border-2 border-text-secondary/30" />;
    }
};

const ResultContent = ({ module, data }) => {
    switch (module) {
        case 'waf':
            return (
                <div className="flex items-center gap-4 p-4 bg-background-tertiary rounded-lg">
                    <Shield className={`w-12 h-12 ${data.detected ? 'text-status-success' : 'text-status-warning'}`} />
                    <div>
                        <h3 className="font-bold text-lg">{data.detected ? `${data.waf_name} Detected` : 'No WAF Detected'}</h3>
                        <p className="text-text-secondary text-sm">Target: {data.target}</p>
                    </div>
                </div>
            );
        case 'port':
            return (
                <div className="space-y-2">
                    <h3 className="font-bold mb-4">Open Ports ({data.open_ports?.length || 0})</h3>
                    {data.open_ports?.map((p, i) => (
                        <div key={i} className="flex items-center justify-between p-3 bg-background-tertiary/50 rounded">
                            <div className="flex items-center gap-4">
                                <span className="w-16 font-mono font-bold text-accent-primary">{p.port}/tcp</span>
                                <span className="w-20 text-sm uppercase text-text-secondary">{p.service}</span>
                                <span className="text-sm">{p.version}</span>
                            </div>
                            <Badge variant="success">OPEN</Badge>
                        </div>
                    ))}
                </div>
            );
        case 'subdo':
            return (
                <div className="space-y-2">
                    <h3 className="font-bold mb-4">Subdomains Found ({data.count || 0})</h3>
                    {data.subdomains?.map((sub, i) => (
                        <div key={i} className="p-3 bg-background-tertiary/50 rounded font-mono text-sm">
                            {sub}
                        </div>
                    ))}
                </div>
            );
        case 'cms':
            return (
                <div className="flex items-center gap-4 p-4 bg-background-tertiary rounded-lg">
                    <Layers className={`w-12 h-12 ${data.detected ? 'text-status-success' : 'text-text-secondary'}`} />
                    <div>
                        <h3 className="font-bold text-lg">{data.detected ? data.cms_name : 'No CMS Detected'}</h3>
                        {data.version && <p className="text-text-secondary text-sm">Version: {data.version}</p>}
                    </div>
                </div>
            );
        case 'tech':
            return (
                <div className="flex flex-wrap gap-2">
                    {data.technologies?.map((tech, i) => (
                        <Badge key={i} variant="outline" className="text-sm px-3 py-1">{tech}</Badge>
                    ))}
                </div>
            );
        case 'dir':
            return (
                <div className="space-y-2">
                    <h3 className="font-bold mb-4">Directories Found ({data.directories?.length || 0})</h3>
                    {data.directories?.map((d, i) => (
                        <div key={i} className="flex items-center justify-between p-3 bg-background-tertiary/50 rounded">
                            <span className="font-mono text-sm">{d.path}</span>
                            <Badge variant={d.status === 200 ? 'success' : d.status === 403 ? 'warning' : 'danger'}>
                                {d.status}
                            </Badge>
                        </div>
                    ))}
                </div>
            );
        default:
            return <p className="text-text-secondary">No data</p>;
    }
};

export default ActiveScan;
