import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Calendar, Filter, Eye, Download, Trash2, RefreshCw, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { ConfirmModal } from '../components/common/Modal';
import { useScanStore } from '../store/scanStore';

const History = () => {
    const navigate = useNavigate();
    const { scans, fetchScans, deleteScan, isLoading } = useScanStore();
    const [deleteId, setDeleteId] = useState(null);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    useEffect(() => {
        fetchScans();
    }, [fetchScans]);

    const handleView = (scanId) => {
        navigate(`/scan?id=${scanId}`);
    };

    const confirmDelete = async () => {
        if (!deleteId) return;
        setIsDeleting(true);
        await deleteScan(deleteId);
        setIsDeleting(false);
        setShowDeleteConfirm(false);
        setDeleteId(null);
    };

    const handleDeleteClick = (scanId) => {
        setDeleteId(scanId);
        setShowDeleteConfirm(true);
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <ConfirmModal
                isOpen={showDeleteConfirm}
                onClose={() => setShowDeleteConfirm(false)}
                onConfirm={confirmDelete}
                title="Delete Scan History"
                message="Are you sure you want to delete this scan record? This action cannot be undone."
                confirmText="Delete"
                isDanger
                isLoading={isDeleting}
            />

            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-text-primary">Scan History</h1>
                    <p className="text-text-secondary mt-1">Review and manage your past reconnaissance activities.</p>
                </div>
                <Button variant="secondary" onClick={() => fetchScans()}>
                    <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} /> Refresh
                </Button>
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
                    {isLoading && scans.length === 0 ? (
                        <div className="flex items-center justify-center py-12">
                            <Loader2 className="w-6 h-6 animate-spin text-accent-primary" />
                        </div>
                    ) : scans.length === 0 ? (
                        <div className="text-center py-12 text-text-secondary">
                            No scans found. Start a new scan from the Dashboard.
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm">
                                <thead className="bg-background-tertiary text-text-secondary uppercase text-xs font-semibold">
                                    <tr>
                                        <th className="px-6 py-4">ID</th>
                                        <th className="px-6 py-4">Target</th>
                                        <th className="px-6 py-4">Type</th>
                                        <th className="px-6 py-4">Status</th>
                                        <th className="px-6 py-4">Date</th>
                                        <th className="px-6 py-4 text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-border/50">
                                    {scans.map((scan) => (
                                        <tr key={scan.id} className="hover:bg-background-tertiary/50 transition-colors group">
                                            <td className="px-6 py-4 font-mono text-text-secondary">#{scan.id}</td>
                                            <td className="px-6 py-4 font-medium text-text-primary">{scan.target}</td>
                                            <td className="px-6 py-4 text-text-secondary capitalize">{scan.scan_type}</td>
                                            <td className="px-6 py-4">
                                                <StatusBadge status={scan.status} />
                                            </td>
                                            <td className="px-6 py-4 text-text-secondary">
                                                {new Date(scan.created_at).toLocaleDateString()}
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                    <Button variant="ghost" size="icon" className="h-8 w-8 hover:text-accent-primary" onClick={() => handleView(scan.id)}>
                                                        <Eye className="w-4 h-4" />
                                                    </Button>
                                                    <Button variant="ghost" size="icon" className="h-8 w-8 hover:text-status-danger" onClick={() => handleDeleteClick(scan.id)}>
                                                        <Trash2 className="w-4 h-4" />
                                                    </Button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
};

const StatusBadge = ({ status }) => {
    const styles = {
        completed: 'bg-status-success/10 text-status-success border-status-success/20',
        running: 'bg-status-warning/10 text-status-warning border-status-warning/20',
        pending: 'bg-accent-primary/10 text-accent-primary border-accent-primary/20',
        failed: 'bg-status-danger/10 text-status-danger border-status-danger/20',
    };

    return (
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles[status] || styles.pending}`}>
            {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
    );
};

export default History;
