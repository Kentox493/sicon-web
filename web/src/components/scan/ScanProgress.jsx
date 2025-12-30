import React from 'react';
import { Loader2, CheckCircle2, AlertTriangle, XCircle, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../common/Card';
import { Button } from '../common/Button';
import { cn } from '../../utils/cn';

const ScanProgress = ({ status = 'running', progress = 0, modules = [] }) => {
    return (
        <Card className="border-accent-primary/20">
            <CardHeader className="pb-2">
                <div className="flex justify-between items-center">
                    <CardTitle className="text-lg flex items-center gap-2">
                        {status === 'running' && <Loader2 className="w-5 h-5 animate-spin text-accent-primary" />}
                        {status === 'completed' && <CheckCircle2 className="w-5 h-5 text-status-success" />}
                        Scanning Progress
                    </CardTitle>
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 text-sm text-text-secondary">
                            <Clock className="w-4 h-4" />
                            <span>Elapsed: 02:45</span>
                        </div>
                        {status === 'running' && (
                            <Button variant="danger" size="sm">Stop Scan</Button>
                        )}
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                {/* Progress Bar */}
                <div className="w-full bg-background-tertiary rounded-full h-4 mb-6 overflow-hidden">
                    <div
                        className="bg-accent-primary h-full transition-all duration-500 ease-out relative"
                        style={{ width: `${progress}%` }}
                    >
                        <div className="absolute inset-0 bg-white/20 animate-pulse" />
                    </div>
                </div>

                {/* Module Status Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                    {modules.map((mod) => (
                        <div
                            key={mod.name}
                            className={cn(
                                "flex items-center gap-2 p-3 rounded-lg border",
                                mod.status === 'completed' && "bg-status-success/10 border-status-success/20 text-text-primary",
                                mod.status === 'running' && "bg-accent-primary/10 border-accent-primary/20 text-text-primary",
                                mod.status === 'pending' && "bg-background-tertiary border-transparent text-text-secondary",
                                mod.status === 'failed' && "bg-status-danger/10 border-status-danger/20 text-text-primary"
                            )}
                        >
                            <StatusIcon status={mod.status} />
                            <span className="text-sm font-medium">{mod.label}</span>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
};

const StatusIcon = ({ status }) => {
    switch (status) {
        case 'completed': return <CheckCircle2 className="w-4 h-4 text-status-success" />;
        case 'running': return <Loader2 className="w-4 h-4 animate-spin text-accent-primary" />;
        case 'failed': return <XCircle className="w-4 h-4 text-status-danger" />;
        default: return <div className="w-4 h-4 rounded-full border-2 border-text-secondary/30" />;
    }
};

export default ScanProgress;
