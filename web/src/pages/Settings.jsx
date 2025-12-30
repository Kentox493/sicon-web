import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Key, Save, Trash2, Eye, EyeOff, Loader2, Check, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Badge } from '../components/common/Badge';
import { settingsAPI } from '../services/api';

const Settings = () => {
    const [geminiKey, setGeminiKey] = useState('');
    const [showKey, setShowKey] = useState(false);
    const [hasKey, setHasKey] = useState(false);
    const [keyPreview, setKeyPreview] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        setIsLoading(true);
        try {
            const data = await settingsAPI.get();
            setHasKey(data.has_gemini_key);
            setKeyPreview(data.gemini_key_preview || '');
        } catch (error) {
            console.error('Failed to fetch settings:', error);
        }
        setIsLoading(false);
    };

    const handleSaveKey = async () => {
        if (!geminiKey.trim()) {
            setMessage({ type: 'error', text: 'Please enter an API key' });
            return;
        }

        setIsSaving(true);
        try {
            const result = await settingsAPI.update({ gemini_api_key: geminiKey });
            setHasKey(result.has_gemini_key);
            setKeyPreview(result.gemini_key_preview || '');
            setGeminiKey('');
            setMessage({ type: 'success', text: 'API Key saved successfully!' });
        } catch (error) {
            setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to save API key' });
        }
        setIsSaving(false);
    };

    const handleDeleteKey = async () => {
        if (!window.confirm('Are you sure you want to remove your Gemini API key?')) return;

        try {
            await settingsAPI.deleteGeminiKey();
            setHasKey(false);
            setKeyPreview('');
            setMessage({ type: 'success', text: 'API Key removed successfully!' });
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to remove API key' });
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div>
                <h1 className="text-3xl font-bold text-text-primary">Settings</h1>
                <p className="text-text-secondary mt-1">Configure your S1C0N preferences and API keys.</p>
            </div>

            {/* Message Alert */}
            {message.text && (
                <div className={`flex items-center gap-3 p-4 rounded-lg border ${message.type === 'success'
                        ? 'bg-status-success/10 border-status-success/20 text-status-success'
                        : 'bg-status-danger/10 border-status-danger/20 text-status-danger'
                    }`}>
                    {message.type === 'success' ? <Check className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                    <span>{message.text}</span>
                    <button onClick={() => setMessage({ type: '', text: '' })} className="ml-auto">✕</button>
                </div>
            )}

            {/* AI Settings */}
            <Card className="border-accent-primary/20">
                <CardHeader>
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <Key className="w-5 h-5 text-accent-primary" />
                        AI Configuration
                    </h2>
                </CardHeader>
                <CardContent className="space-y-6">
                    {isLoading ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="w-6 h-6 animate-spin text-accent-primary" />
                        </div>
                    ) : (
                        <>
                            {/* Current Status */}
                            <div className="flex items-center justify-between p-4 rounded-lg bg-background-tertiary/50">
                                <div>
                                    <p className="font-medium text-text-primary">Gemini API Key</p>
                                    <p className="text-sm text-text-secondary">
                                        {hasKey
                                            ? `Configured ${keyPreview}`
                                            : 'Not configured - AI features will be disabled'}
                                    </p>
                                </div>
                                <Badge variant={hasKey ? 'success' : 'warning'}>
                                    {hasKey ? 'Active' : 'Not Set'}
                                </Badge>
                            </div>

                            {/* Input New Key */}
                            <div className="space-y-3">
                                <label className="block text-sm font-medium text-text-secondary">
                                    {hasKey ? 'Update API Key' : 'Enter Gemini API Key'}
                                </label>
                                <div className="flex gap-3">
                                    <div className="relative flex-1">
                                        <Input
                                            type={showKey ? 'text' : 'password'}
                                            placeholder="AIza..."
                                            value={geminiKey}
                                            onChange={(e) => setGeminiKey(e.target.value)}
                                            className="pr-10"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowKey(!showKey)}
                                            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary hover:text-text-primary"
                                        >
                                            {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                        </button>
                                    </div>
                                    <Button onClick={handleSaveKey} disabled={isSaving}>
                                        {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                                        Save
                                    </Button>
                                </div>
                                <p className="text-xs text-text-secondary">
                                    Get your free API key from{' '}
                                    <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer"
                                        className="text-accent-primary hover:underline">
                                        Google AI Studio
                                    </a>
                                </p>
                            </div>

                            {/* Delete Key */}
                            {hasKey && (
                                <div className="pt-4 border-t border-border/10">
                                    <Button variant="ghost" className="text-status-danger hover:bg-status-danger/10" onClick={handleDeleteKey}>
                                        <Trash2 className="w-4 h-4 mr-2" />
                                        Remove API Key
                                    </Button>
                                </div>
                            )}
                        </>
                    )}
                </CardContent>
            </Card>

            {/* Additional Settings Placeholder */}
            <Card>
                <CardHeader>
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <SettingsIcon className="w-5 h-5 text-accent-primary" />
                        General Settings
                    </h2>
                </CardHeader>
                <CardContent>
                    <p className="text-text-secondary text-center py-8">More settings coming soon...</p>
                </CardContent>
            </Card>
        </div>
    );
};

export default Settings;
