import React from 'react';
import { Save, User, Fingerprint, Network, Terminal } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Badge } from '../components/common/Badge';

const Settings = () => {
    return (
        <div className="max-w-4xl space-y-8 animate-in fade-in duration-500">
            <div>
                <h1 className="text-3xl font-bold text-text-primary">Settings</h1>
                <p className="text-text-secondary mt-1">Configure global application preferences.</p>
            </div>

            <div className="grid gap-8">
                {/* Network Settings */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Network className="w-5 h-5 text-accent-primary" />
                            Network Configuration
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-text-secondary">Default Proxy</label>
                                <Input placeholder="socks5://127.0.0.1:9050" />
                                <p className="text-xs text-text-secondary">Used for all scans unless overridden.</p>
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-text-secondary">Timeout (seconds)</label>
                                <Input type="number" defaultValue="30" />
                            </div>
                        </div>

                        <div className="flex items-center gap-4 pt-2">
                            <div className="flex items-center gap-2">
                                <input type="checkbox" id="tor" className="rounded bg-background-tertiary border-border text-accent-primary focus:ring-accent-primary" />
                                <label htmlFor="tor" className="text-sm text-text-primary">Enable Tor Network by default</label>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* API Keys */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Fingerprint className="w-5 h-5 text-accent-primary" />
                            API Keys
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-text-secondary">Shodan API Key</label>
                            <Input type="password" placeholder="sk_live_..." />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-text-secondary">SecurityTrails Key</label>
                            <Input type="password" placeholder="Enter key..." />
                        </div>
                    </CardContent>
                </Card>

                {/* System */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Terminal className="w-5 h-5 text-accent-primary" />
                            System Paths
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="p-4 rounded bg-background-tertiary font-mono text-xs text-text-secondary">
                            <div className="flex justify-between mb-2"><span>Nmap Path:</span> <span className="text-status-success">/usr/bin/nmap</span></div>
                            <div className="flex justify-between mb-2"><span>Wafw00f Path:</span> <span className="text-status-success">/usr/bin/wafw00f</span></div>
                            <div className="flex justify-between"><span>Python Path:</span> <span className="text-status-success">/usr/bin/python3</span></div>
                        </div>
                    </CardContent>
                </Card>

                <div className="flex justify-end pt-4">
                    <Button size="lg" className="font-bold">
                        <Save className="w-4 h-4 mr-2" /> Save Changes
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default Settings;
