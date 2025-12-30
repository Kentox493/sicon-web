import React, { useState } from 'react';
import { Shield, Globe, Server, Layers, FileCode, Folder } from 'lucide-react';
import { cn } from '../../utils/cn';
import { Card } from '../common/Card';

const tabs = [
    { id: 'waf', label: 'WAF', icon: Shield },
    { id: 'ports', label: 'Ports', icon: Server },
    { id: 'subdomains', label: 'Subdomains', icon: Globe },
    { id: 'cms', label: 'CMS Status', icon: Layers },
    { id: 'tech', label: 'Technologies', icon: FileCode },
    { id: 'dirs', label: 'Directories', icon: Folder },
];

const ResultTabs = ({ activeTab, onTabChange }) => {
    return (
        <div className="flex overflow-x-auto pb-2 gap-2 scrollbar-thin">
            {tabs.map((tab) => (
                <button
                    key={tab.id}
                    onClick={() => onTabChange(tab.id)}
                    className={cn(
                        "flex items-center gap-2 px-4 py-3 rounded-lg border transition-all whitespace-nowrap min-w-[120px]",
                        activeTab === tab.id
                            ? "bg-accent-primary/10 border-accent-primary text-text-primary shadow-sm"
                            : "bg-background-secondary border-border text-text-secondary hover:bg-background-tertiary"
                    )}
                >
                    <tab.icon className={cn("w-4 h-4", activeTab === tab.id ? "text-accent-primary" : "text-text-secondary")} />
                    <span className="text-sm font-medium">{tab.label}</span>
                </button>
            ))}
        </div>
    );
};

export default ResultTabs;
