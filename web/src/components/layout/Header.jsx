import React, { useState, useRef, useEffect } from 'react';
import { Bell, Menu, X, Check, Trash2, CheckCheck } from 'lucide-react';
import { Button } from '../common/Button';
import { useNotificationStore } from '../../store/notificationStore';
import logo from '../../assets/logo.png';

const Header = ({ onMenuClick }) => {
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const dropdownRef = useRef(null);

    const { notifications, unreadCount, markAsRead, markAllAsRead, removeNotification, clearAll } = useNotificationStore();

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setDropdownOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const formatTime = (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = (now - date) / 1000; // seconds

        if (diff < 60) return 'Just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        return date.toLocaleDateString();
    };

    const getTypeColor = (type) => {
        switch (type) {
            case 'success': return 'text-status-success border-status-success/30';
            case 'warning': return 'text-status-warning border-status-warning/30';
            case 'error': return 'text-status-danger border-status-danger/30';
            default: return 'text-accent-primary border-accent-primary/30';
        }
    };

    return (
        <header className="h-16 border-b border-border/10 bg-background-secondary/50 backdrop-blur-md flex items-center justify-between px-6 sticky top-0 z-10">
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" className="md:hidden" onClick={onMenuClick}>
                    <Menu className="w-5 h-5" />
                </Button>
                <div className="flex items-center gap-2 md:hidden">
                    <img src={logo} alt="S1C0N" className="h-8 w-auto" />
                </div>
                <h2 className="hidden md:block text-lg font-semibold text-text-primary tracking-tight">
                    System Status: <span className="text-status-success text-sm ml-2 font-mono">● ONLINE</span>
                </h2>
            </div>

            <div className="relative" ref={dropdownRef}>
                <Button
                    variant="ghost"
                    size="icon"
                    className="relative hover:bg-accent-primary/10 hover:text-accent-primary transition-colors"
                    onClick={() => setDropdownOpen(!dropdownOpen)}
                >
                    <Bell className="w-5 h-5" />
                    {unreadCount > 0 && (
                        <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] flex items-center justify-center rounded-full bg-status-danger text-white text-xs font-bold px-1">
                            {unreadCount > 9 ? '9+' : unreadCount}
                        </span>
                    )}
                </Button>

                {/* Notification Dropdown */}
                {dropdownOpen && (
                    <div className="absolute right-0 top-12 w-80 md:w-96 bg-background-secondary border border-border/20 rounded-xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200 z-50">
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 border-b border-border/10">
                            <h3 className="font-semibold text-text-primary">Notifications</h3>
                            <div className="flex gap-2">
                                {unreadCount > 0 && (
                                    <Button variant="ghost" size="sm" onClick={markAllAsRead} title="Mark all as read">
                                        <CheckCheck className="w-4 h-4" />
                                    </Button>
                                )}
                                {notifications.length > 0 && (
                                    <Button variant="ghost" size="sm" onClick={clearAll} title="Clear all">
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                )}
                            </div>
                        </div>

                        {/* Notification List */}
                        <div className="max-h-80 overflow-y-auto">
                            {notifications.length === 0 ? (
                                <div className="p-8 text-center text-text-secondary">
                                    <Bell className="w-10 h-10 mx-auto mb-3 opacity-30" />
                                    <p className="text-sm">No notifications yet</p>
                                </div>
                            ) : (
                                notifications.map((notif) => (
                                    <div
                                        key={notif.id}
                                        className={`p-4 border-b border-border/10 hover:bg-background-tertiary/50 transition-colors cursor-pointer group ${!notif.read ? 'bg-accent-primary/5' : ''
                                            }`}
                                        onClick={() => markAsRead(notif.id)}
                                    >
                                        <div className="flex items-start gap-3">
                                            <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${notif.read ? 'bg-transparent' : 'bg-accent-primary'
                                                }`} />
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center justify-between gap-2">
                                                    <p className={`text-sm font-medium ${getTypeColor(notif.type)}`}>
                                                        {notif.title}
                                                    </p>
                                                    <span className="text-xs text-text-secondary whitespace-nowrap">
                                                        {formatTime(notif.timestamp)}
                                                    </span>
                                                </div>
                                                <p className="text-sm text-text-secondary mt-1 truncate">
                                                    {notif.message}
                                                </p>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="opacity-0 group-hover:opacity-100 transition-opacity w-6 h-6"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    removeNotification(notif.id);
                                                }}
                                            >
                                                <X className="w-3 h-3" />
                                            </Button>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                )}
            </div>
        </header>
    );
};

export default Header;
