import React, { useEffect, useState } from 'react';
import { X, CheckCircle2, AlertTriangle, Info, AlertCircle } from 'lucide-react';
import { useNotificationStore } from '../../store/notificationStore';
import { cn } from '../../utils/cn';

const Toast = () => {
    const { notifications, removeNotification } = useNotificationStore();
    const [visibleToasts, setVisibleToasts] = useState([]);

    useEffect(() => {
        // Show only the latest 3 notifications as toasts
        const latest = notifications.slice(0, 3);
        setVisibleToasts(latest);

        // Auto-remove toasts after 5 seconds
        if (latest.length > 0) {
            const timer = setTimeout(() => {
                // We don't remove from store, just hide from toast view
                // Actually, for a toast system, we might want to auto-dismiss
                // But let's keep it simple: The store handles persistence (bell icon), 
                // this component handles fleeting visibility.
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [notifications]);

    // Handle fleeting display: 
    // We'll create a local state implementation that listens to addNotification 
    // But since our store is simple, let's just render the top unread ones 
    // and animate them out. 
    // Better approach: The store should ideally have a 'shown' state or we emulate it here.
    // For now, let's just render the most recent unread one if it was added < 5 sec ago.

    // Actually, let's just map the latest few notifications.
    return (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 pointer-events-none">
            {notifications.slice(0, 3).map((notif, index) => (
                <ToastItem key={notif.id} notification={notif} onClose={() => removeNotification(notif.id)} />
            ))}
        </div>
    );
};

const ToastItem = ({ notification, onClose }) => {
    const [visible, setVisible] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => {
            setVisible(false);
        }, 5000);
        return () => clearTimeout(timer);
    }, []);

    if (!visible) return null;

    const icons = {
        success: <CheckCircle2 className="w-5 h-5 text-status-success" />,
        warning: <AlertTriangle className="w-5 h-5 text-status-warning" />,
        error: <AlertCircle className="w-5 h-5 text-status-danger" />,
        info: <Info className="w-5 h-5 text-accent-primary" />,
    };

    const borders = {
        success: 'border-status-success/30 bg-status-success/10',
        warning: 'border-status-warning/30 bg-status-warning/10',
        error: 'border-status-danger/30 bg-status-danger/10',
        info: 'border-accent-primary/30 bg-accent-primary/10',
    };

    return (
        <div className={cn(
            "pointer-events-auto w-80 p-4 rounded-xl border backdrop-blur-md shadow-2xl flex items-start gap-3 transition-all duration-300 animate-in slide-in-from-right-10 fade-in",
            borders[notification.type] || borders.info
        )}>
            {icons[notification.type] || icons.info}
            <div className="flex-1">
                <h4 className="font-semibold text-sm text-text-primary">{notification.title}</h4>
                <p className="text-xs text-text-secondary mt-1 leading-relaxed">{notification.message}</p>
            </div>
            <button onClick={() => setVisible(false)} className="text-text-secondary hover:text-text-primary">
                <X className="w-4 h-4" />
            </button>
        </div>
    );
};

export default Toast;
