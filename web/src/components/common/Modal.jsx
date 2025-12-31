import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { X, AlertTriangle } from 'lucide-react';
import { Button } from './Button';
import { cn } from '../../utils/cn';

export const Modal = ({ isOpen, onClose, title, children, footer, variant = 'default' }) => {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [isOpen]);

    if (!mounted || !isOpen) return null;

    return createPortal(
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
                onClick={onClose}
            />

            {/* Modal Content */}
            <div className={cn(
                "relative bg-background-secondary border border-border/50 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200",
                variant === 'danger' && "border-status-danger/30"
            )}>
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-border/10">
                    <h3 className={cn(
                        "text-xl font-bold",
                        variant === 'danger' ? "text-status-danger" : "text-text-primary"
                    )}>
                        {title}
                    </h3>
                    <button
                        onClick={onClose}
                        className="p-1 rounded-lg hover:bg-background-tertiary text-text-secondary transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Body */}
                <div className="p-6">
                    {children}
                </div>

                {/* Footer */}
                {footer && (
                    <div className="p-6 pt-0 flex justify-end gap-3">
                        {footer}
                    </div>
                )}
            </div>
        </div>,
        document.body
    );
};

export const ConfirmModal = ({ isOpen, onClose, onConfirm, title, message, confirmText = "Confirm", cancelText = "Cancel", isDanger = false, isLoading = false }) => {
    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title={title}
            variant={isDanger ? 'danger' : 'default'}
            footer={
                <>
                    <Button variant="ghost" onClick={onClose} disabled={isLoading}>
                        {cancelText}
                    </Button>
                    <Button
                        variant={isDanger ? 'destructive' : 'primary'}
                        onClick={onConfirm}
                        isLoading={isLoading}
                    >
                        {confirmText}
                    </Button>
                </>
            }
        >
            <div className="flex gap-4">
                {isDanger && (
                    <div className="w-12 h-12 rounded-full bg-status-danger/10 flex items-center justify-center flex-shrink-0">
                        <AlertTriangle className="w-6 h-6 text-status-danger" />
                    </div>
                )}
                <div className="space-y-2">
                    <p className="text-text-secondary leading-relaxed">
                        {message}
                    </p>
                </div>
            </div>
        </Modal>
    );
};
