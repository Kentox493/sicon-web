import React from 'react';
import { FileText, Download, Share2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';

const Reports = () => {
    const reports = [
        { id: 1, name: 'Report_example.com_FULL.pdf', date: '2 hours ago', size: '2.4 MB' },
        { id: 2, name: 'Report_test-site.org_WAF.json', date: '1 day ago', size: '156 KB' },
        { id: 3, name: 'Report_corp.net_VULN.html', date: '2 days ago', size: '1.1 MB' },
    ];

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-text-primary">Reports</h1>
                    <p className="text-text-secondary mt-1">Generated scan reports and documentation.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {reports.map((report) => (
                    <Card key={report.id} className="group hover:border-accent-primary/50 transition-all cursor-pointer">
                        <CardContent className="p-6 flex flex-col gap-4">
                            <div className="flex items-start justify-between">
                                <div className="p-3 rounded-lg bg-background-tertiary group-hover:bg-accent-primary/10 transition-colors">
                                    <FileText className="w-8 h-8 text-accent-primary" />
                                </div>
                                <Button variant="ghost" size="icon" className="text-text-secondary hover:text-text-primary">
                                    <MoreVerticalIcon />
                                </Button>
                            </div>

                            <div>
                                <h3 className="font-semibold text-text-primary truncate" title={report.name}>{report.name}</h3>
                                <div className="flex items-center gap-2 mt-1 text-sm text-text-secondary">
                                    <span>{report.date}</span>
                                    <span>•</span>
                                    <span>{report.size}</span>
                                </div>
                            </div>

                            <div className="pt-4 mt-auto flex gap-2 border-t border-border/50">
                                <Button className="flex-1 bg-accent-primary/10 text-accent-primary hover:bg-accent-primary hover:text-background-primary transition-colors">
                                    <Download className="w-4 h-4 mr-2" /> Download
                                </Button>
                                <Button variant="secondary" size="icon">
                                    <Share2 className="w-4 h-4" />
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
};

const MoreVerticalIcon = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="1" />
        <circle cx="12" cy="5" r="1" />
        <circle cx="12" cy="19" r="1" />
    </svg>
);

export default Reports;
