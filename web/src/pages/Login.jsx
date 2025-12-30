import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, LogIn, AlertCircle } from 'lucide-react';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { useAuthStore } from '../store/authStore';
import logo from '../assets/logo.png';

const Login = () => {
    const navigate = useNavigate();
    const { login, isLoading, error, clearError } = useAuthStore();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        clearError();
        const success = await login(username, password);
        if (success) {
            navigate('/');
        }
    };

    return (
        <div className="min-h-screen bg-background-primary flex items-center justify-center p-4">
            <div className="w-full max-w-md space-y-8">
                <div className="text-center">
                    <img src={logo} alt="S1C0N" className="h-16 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-text-primary">Welcome Back</h2>
                    <p className="text-text-secondary mt-2">Sign in to your account</p>
                </div>

                <Card className="border-accent-primary/20">
                    <CardContent className="p-6">
                        <form onSubmit={handleSubmit} className="space-y-6">
                            {error && (
                                <div className="flex items-center gap-2 p-3 rounded-lg bg-status-danger/10 border border-status-danger/20 text-status-danger text-sm">
                                    <AlertCircle className="w-4 h-4" />
                                    {error}
                                </div>
                            )}

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-text-secondary">Username</label>
                                <Input
                                    type="text"
                                    placeholder="Enter your username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-text-secondary">Password</label>
                                <Input
                                    type="password"
                                    placeholder="Enter your password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>

                            <Button type="submit" className="w-full" size="lg" isLoading={isLoading}>
                                <LogIn className="w-4 h-4 mr-2" />
                                Sign In
                            </Button>
                        </form>

                        <div className="mt-6 text-center text-sm">
                            <span className="text-text-secondary">Don't have an account? </span>
                            <Link to="/register" className="text-accent-primary hover:underline font-medium">
                                Create one
                            </Link>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default Login;
