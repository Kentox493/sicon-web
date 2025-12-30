import React from 'react';
import { cn } from '../../utils/cn';

const Badge = ({ className, variant = 'default', children, ...props }) => {
    const variants = {
        default: 'bg-background-tertiary text-text-primary',
        success: 'bg-status-success/20 text-status-success border-status-success/20',
        warning: 'bg-status-warning/20 text-status-warning border-status-warning/20',
        danger: 'bg-status-danger/20 text-status-danger border-status-danger/20',
        outline: 'text-text-primary border border-border',
    };

    return (
        <div
            className={cn(
                'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
                variants[variant],
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
};

export { Badge };
