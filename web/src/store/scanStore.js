import { create } from 'zustand';
import { scansAPI } from '../services/api';

export const useScanStore = create((set, get) => ({
    scans: [],
    currentScan: null,
    isLoading: false,
    error: null,

    // Fetch all scans for current user
    fetchScans: async () => {
        set({ isLoading: true, error: null });
        try {
            const scans = await scansAPI.list();
            set({ scans, isLoading: false });
        } catch (error) {
            set({
                error: error.response?.data?.detail || 'Failed to fetch scans',
                isLoading: false
            });
        }
    },

    // Start a new scan
    startScan: async (target, options) => {
        set({ isLoading: true, error: null });
        try {
            const scan = await scansAPI.create(target, options);
            set((state) => ({
                scans: [scan, ...state.scans],
                currentScan: scan,
                isLoading: false
            }));
            return scan;
        } catch (error) {
            set({
                error: error.response?.data?.detail || 'Failed to start scan',
                isLoading: false
            });
            return null;
        }
    },

    // Get scan by ID
    getScan: async (scanId) => {
        set({ isLoading: true, error: null });
        try {
            const scan = await scansAPI.get(scanId);
            set({ currentScan: scan, isLoading: false });
            return scan;
        } catch (error) {
            set({
                error: error.response?.data?.detail || 'Failed to fetch scan',
                isLoading: false
            });
            return null;
        }
    },

    // Delete a scan
    deleteScan: async (scanId) => {
        try {
            await scansAPI.delete(scanId);
            set((state) => ({
                scans: state.scans.filter(s => s.id !== scanId)
            }));
            return true;
        } catch (error) {
            set({ error: error.response?.data?.detail || 'Failed to delete scan' });
            return false;
        }
    },

    // Set current scan
    setCurrentScan: (scan) => set({ currentScan: scan }),

    // Clear current scan
    clearCurrentScan: () => set({ currentScan: null }),

    // Clear error
    clearError: () => set({ error: null }),
}));
