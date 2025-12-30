import React from 'react';
import { Bell, Menu } from 'lucide-react';
import { Button } from '../common/Button';
import logo from '../../assets/logo.png';

const Header = ({ onMenuClick }) => {
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

            <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" className="relative hover:bg-accent-primary/10 hover:text-accent-primary transition-colors">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-status-danger animate-pulse box-shadow-glow" />
                </Button>
            </div>
        </header>
    );
};

export default Header;
