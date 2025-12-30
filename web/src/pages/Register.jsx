import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { UserPlus, AlertCircle } from 'lucide-react';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Card, CardContent } from '../components/common/Card';
import { useAuthStore } from '../store/authStore';
import logo from '../assets/logo.png';

const Register = () => {
    const navigate = useNavigate();
    const { register, isLoading, error, clearError } = useAuthStore();
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [localError, setLocalError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        clearError();
        setLocalError('');

        if (password !== confirmPassword) {
            setLocalError('Passwords do not match');
            return;
        }

        if (password.length < 6) {
            setLocalError('Password must be at least 6 characters');
            return;
        }

        const success = await register(username, email, password);
        if (success) {
            navigate('/');
        }
    };

    return (
        <div className="min-h-screen bg-background-primary flex items-center justify-center p-4">
            <div className="w-full max-w-md space-y-8">
                <div className="text-center">
                    <img src={logo} alt="S1C0N" className="h-16 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-text-primary">Create Account</h2>
                    <p className="text-text-secondary mt-2">Join the reconnaissance platform</p>
                </div>

                <Card className="border-accent-primary/20">
                    <CardContent className="p-6">
                        <form onSubmit={handleSubmit} className="space-y-5">
                            {(error || localError) && (
                                <div className="flex items-center gap-2 p-3 rounded-lg bg-status-danger/10 border border-status-danger/20 text-status-danger text-sm">
                                    <AlertCircle className="w-4 h-4" />
                                    {error || localError}
                                </div>
                            )}

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-text-secondary">Username</label>
                                <Input
                                    type="text"
                                    placeholder="Choose a username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-text-secondary">Email</label>
                                <Input
                                    type="email"
                                    placeholder="Enter your email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-text-secondary">Password</label>
                                <Input
                                    type="password"
                                    placeholder="Create a password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-text-secondary">Confirm Password</label>
                                <Input
                                    type="password"
                                    placeholder="Confirm your password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    required
                                />
                            </div>

                            <Button type="submit" className="w-full" size="lg" isLoading={isLoading}>
                                <UserPlus className="w-4 h-4 mr-2" />
                                Create Account
                            </Button>
                        </form>

                        <div className="mt-6 text-center text-sm">
                            <span className="text-text-secondary">Already have an account? </span>
                            <Link to="/login" className="text-accent-primary hover:underline font-medium">
                                Sign in
                            </Link>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default Register;
