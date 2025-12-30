import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Radar, History, FileText, Settings } from 'lucide-react';
import { cn } from '../../utils/cn';
import logo from '../../assets/logo.png';

const Sidebar = ({ className }) => {
    const navItems = [
        { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
        { icon: Radar, label: 'Active Scan', path: '/scan' },
        { icon: History, label: 'Scan History', path: '/history' },
        { icon: FileText, label: 'Reports', path: '/reports' },
        { icon: Settings, label: 'Settings', path: '/settings' },
    ];

    return (
        <aside className={cn('flex flex-col w-64 border-r border-border/10 bg-background-secondary h-screen', className)}>
            <div className="flex items-center justify-center p-6 border-b border-border/10">
                <img src={logo} alt="S1C0N Logo" className="h-12 w-auto object-contain" />
            </div>

            <nav className="flex-1 p-4 space-y-2">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            cn(
                                'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 text-sm font-medium border border-transparent',
                                isActive
                                    ? 'bg-accent-primary/10 text-accent-primary border-accent-primary/20 shadow-[0_0_15px_rgba(37,211,102,0.1)]'
                                    : 'text-text-secondary hover:bg-background-tertiary hover:text-text-primary'
                            )
                        }
                    >
                        <item.icon className="w-5 h-5" />
                        {item.label}
                    </NavLink>
                ))}
            </nav>

            <div className="p-4 border-t border-border/10">
                <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-background-primary border border-border/20">
                    <div className="w-8 h-8 rounded-full bg-accent-secondary/20 flex items-center justify-center text-accent-secondary font-bold text-xs ring-1 ring-accent-secondary/50">
                        XD
                    </div>
                    <div className="flex flex-col">
                        <span className="text-sm font-medium text-text-primary">x0rr-dan</span>
                        <span className="text-xs text-text-secondary">Admin</span>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
