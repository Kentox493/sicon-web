import { create } from 'zustand';

export const useNotificationStore = create((set, get) => ({
    notifications: [],
    unreadCount: 0,

    // Add a new notification
    addNotification: (notification) => {
        const newNotif = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            read: false,
            ...notification, // { type: 'success'|'info'|'warning'|'error', title, message }
        };
        set((state) => ({
            notifications: [newNotif, ...state.notifications].slice(0, 50), // Keep last 50
            unreadCount: state.unreadCount + 1,
        }));
    },

    // Mark a notification as read
    markAsRead: (id) => {
        set((state) => ({
            notifications: state.notifications.map((n) =>
                n.id === id ? { ...n, read: true } : n
            ),
            unreadCount: Math.max(0, state.unreadCount - 1),
        }));
    },

    // Mark all as read
    markAllAsRead: () => {
        set((state) => ({
            notifications: state.notifications.map((n) => ({ ...n, read: true })),
            unreadCount: 0,
        }));
    },

    // Clear all notifications
    clearAll: () => {
        set({ notifications: [], unreadCount: 0 });
    },

    // Remove a specific notification
    removeNotification: (id) => {
        set((state) => {
            const notif = state.notifications.find((n) => n.id === id);
            return {
                notifications: state.notifications.filter((n) => n.id !== id),
                unreadCount: notif && !notif.read ? state.unreadCount - 1 : state.unreadCount,
            };
        });
    },
}));
