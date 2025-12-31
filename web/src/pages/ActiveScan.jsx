import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Shield, Server, Globe, Layers, FileCode, Folder, Loader2, CheckCircle2, XCircle, Clock, AlertCircle, AlertTriangle, ExternalLink, StopCircle } from 'lucide-react';
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
    { id: 'tech', label: 'Tech Stack', icon: FileCode },
    { id: 'dir', label: 'Directories', icon: Folder },
];

const ActiveScan = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const scanId = searchParams.get('id');

    const { currentScan, getScan, stopScan, isLoading, error } = useScanStore();
    const [activeTab, setActiveTab] = useState('waf');
    const [isStopping, setIsStopping] = useState(false);

    useEffect(() => {
        if (!scanId) {
            navigate('/');
            return;
        }

        getScan(parseInt(scanId));

        const interval = setInterval(async () => {
            const scan = await getScan(parseInt(scanId));
            if (scan && (scan.status === 'completed' || scan.status === 'failed' || scan.status === 'cancelled')) {
                clearInterval(interval);
            }
        }, 2000);

        return () => clearInterval(interval);
    }, [scanId, getScan, navigate]);

    const handleStopScan = async () => {
        setIsStopping(true);
        await stopScan(parseInt(scanId));
        setIsStopping(false);
    };

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
                        {status === 'running' ? 'Scanning...' : status === 'completed' ? 'Scan Complete' : status === 'cancelled' ? 'Scan Cancelled' : 'Scan Failed'}
                    </h1>
                    <p className="text-accent-primary font-mono mt-1">{target}</p>
                </div>
                <div className="flex items-center gap-3">
                    {(status === 'running' || status === 'pending') && (
                        <Button
                            variant="destructive"
                            onClick={handleStopScan}
                            disabled={isStopping}
                            className="bg-status-danger hover:bg-status-danger/80"
                        >
                            {isStopping ? (
                                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                            ) : (
                                <StopCircle className="w-4 h-4 mr-2" />
                            )}
                            Stop Scan
                        </Button>
                    )}
                    <Badge variant="outline" className="px-3 py-1">ID: #{currentScan.id}</Badge>
                </div>
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
                                onClick={() => setActiveTab(mod.name)}
                                className={cn(
                                    "flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-all",
                                    mod.status === 'completed' && "bg-status-success/10 border-status-success/20",
                                    mod.status === 'running' && "bg-accent-primary/10 border-accent-primary/20 animate-pulse",
                                    mod.status === 'pending' && "bg-background-tertiary border-transparent text-text-secondary",
                                    mod.status === 'failed' && "bg-status-danger/10 border-status-danger/20",
                                    activeTab === mod.name && "ring-2 ring-accent-primary"
                                )}
                            >
                                <StatusIcon status={mod.status} />
                                <span className="text-sm font-medium">{mod.label}</span>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Results */}
            <Card>
                <CardHeader>
                    <div className="flex gap-2 overflow-x-auto pb-2">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={cn(
                                    "flex items-center gap-2 px-4 py-2 rounded-lg border transition-all whitespace-nowrap",
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
                </CardHeader>
                <CardContent className="min-h-[300px]">
                    {results && results[activeTab] ? (
                        <ResultContent module={activeTab} data={results[activeTab]} />
                    ) : (
                        <div className="flex flex-col items-center justify-center h-64 text-text-secondary">
                            {status === 'running' ? (
                                <>
                                    <Loader2 className="w-8 h-8 animate-spin mb-4" />
                                    <p>Waiting for results...</p>
                                </>
                            ) : (
                                <p>No data available for this module</p>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
};

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

// =============================================================================
// RESULT RENDERERS
// =============================================================================

const ResultContent = ({ module, data }) => {
    if (data.error) {
        return (
            <div className="flex items-center gap-3 p-4 rounded-lg bg-status-danger/10 border border-status-danger/20">
                <AlertTriangle className="w-6 h-6 text-status-danger" />
                <div>
                    <p className="font-medium text-status-danger">Error</p>
                    <p className="text-sm text-text-secondary">{data.error}</p>
                </div>
            </div>
        );
    }

    switch (module) {
        case 'waf': return <WafResult data={data} />;
        case 'port': return <PortResult data={data} />;
        case 'subdo': return <SubdomainResult data={data} />;
        case 'cms': return <CmsResult data={data} />;
        case 'tech': return <TechResult data={data} />;
        case 'dir': return <DirResult data={data} />;
        default: return <pre className="text-xs">{JSON.stringify(data, null, 2)}</pre>;
    }
};

const WafResult = ({ data }) => (
    <div className="space-y-4">
        <div className={cn(
            "flex items-center gap-4 p-6 rounded-lg border",
            data.detected ? "bg-status-success/5 border-status-success/20" : "bg-status-warning/5 border-status-warning/20"
        )}>
            <Shield className={cn("w-16 h-16", data.detected ? "text-status-success" : "text-status-warning")} />
            <div>
                <h3 className="text-2xl font-bold">{data.detected ? data.waf_name : "No WAF Detected"}</h3>
                {data.waf_vendor && <p className="text-text-secondary mt-1">Vendor: {data.waf_vendor}</p>}
                <p className="text-sm text-text-secondary mt-2">Target: {data.target}</p>
            </div>
            <Badge variant={data.detected ? "success" : "warning"} className="ml-auto text-lg px-4 py-2">
                {data.detected ? "PROTECTED" : "UNPROTECTED"}
            </Badge>
        </div>
    </div>
);

const PortResult = ({ data }) => (
    <div className="space-y-4">
        <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Open Ports ({data.count || 0})</h3>
            <span className="text-sm text-text-secondary">{data.scan_type}</span>
        </div>
        <div className="space-y-2">
            {data.open_ports?.length > 0 ? data.open_ports.map((p, i) => (
                <div key={i} className="flex items-center justify-between p-4 rounded-lg bg-background-tertiary/50 hover:bg-background-tertiary transition-colors">
                    <div className="flex items-center gap-6">
                        <div className="w-20">
                            <span className="font-mono font-bold text-accent-primary text-lg">{p.port}</span>
                            <span className="text-text-secondary">/{p.protocol}</span>
                        </div>
                        <div>
                            <span className="font-medium uppercase">{p.service}</span>
                            {p.version && <span className="text-text-secondary ml-2">{p.version}</span>}
                        </div>
                    </div>
                    <Badge variant={p.risk === 'high' ? 'danger' : p.risk === 'medium' ? 'warning' : 'success'}>
                        {p.risk?.toUpperCase()} RISK
                    </Badge>
                </div>
            )) : (
                <p className="text-center text-text-secondary py-8">No open ports found</p>
            )}
        </div>
    </div>
);

const SubdomainResult = ({ data }) => (
    <div className="space-y-4">
        <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Subdomains Found ({data.count || 0})</h3>
            <div className="flex gap-2">
                {data.sources?.map((src, i) => (
                    <Badge key={i} variant="outline" className="text-xs">{src}</Badge>
                ))}
            </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-96 overflow-y-auto">
            {data.subdomains?.length > 0 ? data.subdomains.map((s, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-background-tertiary/50 hover:bg-background-tertiary transition-colors group">
                    <div className="flex items-center gap-2">
                        <Badge variant={s.type === 'cpanel' ? 'warning' : 'default'} className="text-xs">
                            {s.type === 'cpanel' ? 'cPanel' : 'Regular'}
                        </Badge>
                        <span className="font-mono text-sm">{s.subdomain}</span>
                    </div>
                    <a href={s.url} target="_blank" rel="noopener noreferrer" className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <ExternalLink className="w-4 h-4 text-accent-primary" />
                    </a>
                </div>
            )) : (
                <p className="col-span-2 text-center text-text-secondary py-8">No subdomains found</p>
            )}
        </div>
    </div>
);

const CmsResult = ({ data }) => (
    <div className="space-y-4">
        <div className={cn(
            "flex items-center gap-4 p-6 rounded-lg border",
            data.detected ? "bg-accent-primary/5 border-accent-primary/20" : "bg-background-tertiary border-border"
        )}>
            <Layers className={cn("w-16 h-16", data.detected ? "text-accent-primary" : "text-text-secondary")} />
            <div className="flex-1">
                <h3 className="text-2xl font-bold">{data.detected ? data.cms_name : "No CMS Detected"}</h3>
                {data.cms_version && <p className="text-text-secondary mt-1">Version: {data.cms_version}</p>}
                {data.confidence && (
                    <Badge variant={data.confidence === 'high' ? 'success' : data.confidence === 'medium' ? 'warning' : 'default'} className="mt-2">
                        {data.confidence.toUpperCase()} CONFIDENCE
                    </Badge>
                )}
            </div>
        </div>
        {data.indicators?.length > 0 && (
            <div className="space-y-2">
                <h4 className="font-medium text-text-secondary">Detection Indicators:</h4>
                {data.indicators.map((ind, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm">
                        <CheckCircle2 className="w-4 h-4 text-status-success" />
                        <span>{ind}</span>
                    </div>
                ))}
            </div>
        )}
    </div>
);

const TechResult = ({ data }) => (
    <div className="space-y-6">
        <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Technologies Detected ({data.count || 0})</h3>
        </div>

        {data.headers && Object.keys(data.headers).length > 0 && (
            <div className="p-4 rounded-lg bg-background-tertiary">
                <h4 className="font-medium mb-2">Response Headers</h4>
                {Object.entries(data.headers).map(([key, val]) => (
                    <div key={key} className="flex gap-2 text-sm">
                        <span className="text-text-secondary">{key}:</span>
                        <span className="font-mono">{val}</span>
                    </div>
                ))}
            </div>
        )}

        {data.categories && Object.keys(data.categories).length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(data.categories).map(([cat, techs]) => (
                    <div key={cat} className="p-4 rounded-lg bg-background-tertiary/50">
                        <h4 className="font-medium capitalize mb-3">{cat.replace('_', ' ')}</h4>
                        <div className="flex flex-wrap gap-2">
                            {techs.map((tech, i) => (
                                <Badge key={i} variant="outline">{tech}</Badge>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        )}
    </div>
);

const DirResult = ({ data }) => (
    <div className="space-y-4">
        <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Directories Found ({data.count || 0})</h3>
            {data.by_status && (
                <div className="flex gap-2">
                    {Object.entries(data.by_status).map(([status, count]) => (
                        <Badge key={status} variant={status === '200' ? 'success' : status === '403' ? 'warning' : 'default'}>
                            {status}: {count}
                        </Badge>
                    ))}
                </div>
            )}
        </div>
        <div className="space-y-2 max-h-96 overflow-y-auto">
            {data.directories?.length > 0 ? data.directories.map((d, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-background-tertiary/50 hover:bg-background-tertiary transition-colors">
                    <div className="flex items-center gap-3">
                        <Badge variant={
                            d.status === 200 ? 'success' :
                                d.status === 301 || d.status === 302 ? 'warning' :
                                    d.status === 403 ? 'danger' : 'default'
                        }>
                            {d.status}
                        </Badge>
                        <span className="font-mono text-sm">{d.path}</span>
                    </div>
                    {d.size > 0 && <span className="text-xs text-text-secondary">{d.size} bytes</span>}
                </div>
            )) : (
                <p className="text-center text-text-secondary py-8">No directories found</p>
            )}
        </div>
    </div>
);

export default ActiveScan;
