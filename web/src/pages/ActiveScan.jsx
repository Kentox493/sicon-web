import React, { useState, useEffect } from 'react';
import { Shield, Server } from 'lucide-react';
import ScanProgress from '../components/scan/ScanProgress';
import ResultTabs from '../components/results/ResultTabs';
import { Card, CardContent, CardHeader, CardTitle } from '../components/common/Card';
import { Badge } from '../components/common/Badge';

const ActiveScan = () => {
    const [activeTab, setActiveTab] = useState('waf');

    // Mock Data State
    const [progress, setProgress] = useState(0);
    const modules = [
        { name: 'waf', label: 'WAF', status: 'completed' },
        { name: 'port', label: 'Ports', status: 'running' },
        { name: 'subdo', label: 'Subdomains', status: 'pending' },
        { name: 'cms', label: 'CMS', status: 'pending' },
        { name: 'tech', label: 'Tech', status: 'pending' },
        { name: 'dir', label: 'Dir', status: 'pending' },
    ];

    // Mock Progress Simulation
    useEffect(() => {
        const timer = setInterval(() => {
            setProgress(prev => (prev < 90 ? prev + 1 : prev));
        }, 100);
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-text-primary">Scanning Target</h1>
                    <p className="text-text-secondary font-mono mt-1 text-accent-primary">https://example.com</p>
                </div>
                <Badge variant="outline" className="px-3 py-1">ID: #SCAN-8821</Badge>
            </div>

            <ScanProgress
                status="running"
                progress={progress}
                modules={modules}
            />

            <div className="space-y-4">
                <ResultTabs activeTab={activeTab} onTabChange={setActiveTab} />

                <div className="min-h-[400px]">
                    {/* Content Area - conditional rendering based on activeTab */}
                    {activeTab === 'waf' && <WafResultMock />}
                    {activeTab === 'ports' && <PortResultMock />}
                    {activeTab !== 'waf' && activeTab !== 'ports' && (
                        <Card>
                            <CardContent className="p-12 text-center text-text-secondary">
                                Scan module waiting to start...
                            </CardContent>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
};

// Mock Result Components
const WafResultMock = () => (
    <Card className="border-l-4 border-l-status-success">
        <CardHeader>
            <CardTitle className="text-xl">WAF Detection Results</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
            <div className="flex items-center gap-4 p-4 bg-background-tertiary rounded-lg border border-border">
                <Shield className="w-12 h-12 text-status-success" />
                <div>
                    <h3 className="font-bold text-lg text-text-primary">Cloudflare WAF Detected</h3>
                    <p className="text-text-secondary text-sm">The target is behind Cloudflare protection.</p>
                </div>
                <div className="ml-auto">
                    <Badge variant="success">PROTECTED</Badge>
                </div>
            </div>
        </CardContent>
    </Card>
);

const PortResultMock = () => (
    <Card>
        <CardHeader>
            <CardTitle className="text-xl">Open Ports Found (3)</CardTitle>
        </CardHeader>
        <CardContent>
            <div className="space-y-2">
                {[
                    { port: 80, service: 'http', version: 'nginx 1.18.0', state: 'open' },
                    { port: 443, service: 'https', version: 'nginx 1.18.0', state: 'open' },
                    { port: 22, service: 'ssh', version: 'OpenSSH 8.2p1', state: 'filtered' },
                ].map((p) => (
                    <div key={p.port} className="flex items-center justify-between p-3 bg-background-tertiary/50 rounded hover:bg-background-tertiary transition-colors">
                        <div className="flex items-center gap-4">
                            <div className="w-16 font-mono font-bold text-accent-primary">{p.port}/tcp</div>
                            <div className="w-20 text-sm font-medium uppercase text-text-secondary">{p.service}</div>
                            <div className="text-sm text-text-primary">{p.version}</div>
                        </div>
                        <Badge variant={p.state === 'open' ? 'success' : 'warning'}>{p.state.toUpperCase()}</Badge>
                    </div>
                ))}
            </div>
        </CardContent>
    </Card>
);

export default ActiveScan;
