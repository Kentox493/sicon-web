import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Smartphone, Globe, Lock, Cpu, Server, Sparkles, Terminal, LogIn, Github } from 'lucide-react';
import { Button } from '../components/common/Button';
import { useAuthStore } from '../store/authStore';
import logo from '../assets/logo.png';

const Landing = () => {
    const { isAuthenticated } = useAuthStore();
    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated) {
            navigate('/');
        }
    }, [isAuthenticated, navigate]);

    return (
        <div className="min-h-screen bg-background-primary text-text-primary overflow-x-hidden selection:bg-accent-primary/30">
            {/* Header */}
            <header className="fixed top-0 w-full z-50 bg-background-primary/80 backdrop-blur-md border-b border-border/10">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <img src={logo} alt="S1C0N" className="h-10 w-auto" />
                    </div>
                    <div className="flex items-center gap-4">
                        <Link to="/login">
                            <Button variant="ghost" size="sm" className="hidden md:flex">Sign In</Button>
                        </Link>
                        <Link to="/register">
                            <Button size="sm" className="shadow-lg shadow-accent-primary/20">
                                <Sparkles className="w-4 h-4 mr-2" />
                                Get Started
                            </Button>
                        </Link>
                    </div>
                </div>
            </header>

            {/* Hero Section */}
            <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 px-6">
                {/* Background Grid */}
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>
                <div className="absolute inset-0 bg-grid-white/[0.02] pointer-events-none"></div>

                <div className="max-w-5xl mx-auto text-center relative z-10 animate-in fade-in slide-in-from-bottom-8 duration-700">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-primary/10 border border-accent-primary/20 text-accent-primary text-sm font-mono mb-8">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-primary opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-primary"></span>
                        </span>
                        v2.0 AI-Enhanced Reporting
                    </div>

                    <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 leading-tight">
                        Advanced Reconnaissance <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-primary via-accent-secondary to-accent-primary bg-300% animate-gradient">
                            With Intelligent Analysis
                        </span>
                    </h1>

                    <p className="text-xl md:text-2xl text-text-secondary max-w-2xl mx-auto mb-12 leading-relaxed">
                        Automate your security assessments finding WAFs, ports, and subdomains.
                        Let AI analyze the results to generate actionable executive reports.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Link to="/register" className="w-full sm:w-auto">
                            <Button size="lg" className="w-full sm:w-auto h-14 text-lg px-8 shadow-xl shadow-accent-primary/20 hover:shadow-accent-primary/40 transition-all hover:-translate-y-1">
                                Launch Console <Terminal className="w-5 h-5 ml-2" />
                            </Button>
                        </Link>
                        <Link to="/login" className="w-full sm:w-auto">
                            <Button variant="secondary" size="lg" className="w-full sm:w-auto h-14 text-lg px-8 border-border/40 hover:bg-background-tertiary">
                                Live Demo <Globe className="w-5 h-5 ml-2" />
                            </Button>
                        </Link>
                    </div>

                    {/* Terminal Preview */}
                    <div className="mt-20 mx-auto max-w-4xl bg-[#0D1117] rounded-xl border border-border/20 shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-16 duration-1000 delay-200">
                        <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5 bg-white/5">
                            <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                            <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                            <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
                            <div className="ml-4 font-mono text-xs text-text-secondary">s1c0n-cli — scan — 80x24</div>
                        </div>
                        <div className="p-6 font-mono text-sm text-left overflow-hidden">
                            <div className="text-accent-primary mb-2">$ s1c0n scan target.com --generate-report</div>
                            <div className="text-text-secondary">
                                <span className="text-green-400">✔</span> Target resolved: 104.21.55.2<br />
                                <span className="text-green-400">✔</span> WAF Detected: Cloudflare (Confidence: 99%)<br />
                                <span className="text-green-400">✔</span> 12 Open Ports Discovered<br />
                                <span className="text-green-400">✔</span> 45 Subdomains Enumerated<br />
                                <span className="text-green-400">✔</span> Generating PDF Report...<br />
                            </div>
                            <div className="mt-4 p-4 bg-accent-primary/5 border-l-2 border-accent-primary rounded-r">
                                <span className="text-accent-primary font-bold">REPORT GENERATED:</span><br />
                                AI Analysis of scan results complete.
                                - 3 Critical findings highlighted
                                - CVE correlations identified
                                - Executive summary created
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Grid */}
            <section className="py-24 px-6 bg-background-tertiary/20 border-y border-border/10">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-5xl font-bold mb-6">Why Choose S1C0N?</h2>
                        <p className="text-text-secondary max-w-2xl mx-auto text-lg">
                            Built for modern security teams who need speed, accuracy, and depth in their reconnaissance phase.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {[
                            {
                                icon: <Cpu className="w-8 h-8" />,
                                title: "AI-Enhanced Reporting",
                                desc: "Leverage Gemini 2.5 Flash to analyze scan results, correlate findings, and generate professional executive summaries."
                            },
                            {
                                icon: <Shield className="w-8 h-8" />,
                                title: "WAF & Tech Detection",
                                desc: "Advanced fingerprinting to identify WAFs (Cloudflare, AWS, etc.) and underlying technology stacks instantly."
                            },
                            {
                                icon: <Globe className="w-8 h-8" />,
                                title: "Deep Subdomain Recon",
                                desc: "Discover hidden attack surfaces with high-performance subdomain enumeration and directory scanning."
                            },
                            {
                                icon: <Server className="w-8 h-8" />,
                                title: "Port & Service Scanning",
                                desc: "Fast, non-intrusive port scanning to map out exposed services and potential entry points."
                            },
                            {
                                icon: <Lock className="w-8 h-8" />,
                                title: "Secure & Private",
                                desc: "Your API keys and scan data are encrypted. We prioritize your operational security above all."
                            },
                            {
                                icon: <Terminal className="w-8 h-8" />,
                                title: "Detailed PDF Reports",
                                desc: "Generate professional, branded reports with data visualizations and actionable remediation steps."
                            }
                        ].map((feature, idx) => (
                            <div key={idx} className="p-8 rounded-2xl bg-background-primary border border-border/10 hover:border-accent-primary/30 hover:bg-background-tertiary transition-all duration-300 group">
                                <div className="w-14 h-14 rounded-xl bg-accent-primary/10 flex items-center justify-center text-accent-primary mb-6 group-hover:scale-110 transition-transform">
                                    {feature.icon}
                                </div>
                                <h3 className="text-xl font-bold mb-3 group-hover:text-accent-primary transition-colors">{feature.title}</h3>
                                <p className="text-text-secondary leading-relaxed">{feature.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-24 px-6 relative overflow-hidden">
                <div className="absolute inset-0 bg-accent-primary/5"></div>
                <div className="max-w-4xl mx-auto text-center relative z-10">
                    <h2 className="text-4xl md:text-5xl font-bold mb-8">Ready to Secure Your Infrastructure?</h2>
                    <p className="text-xl text-text-secondary mb-10 max-w-2xl mx-auto">
                        Join thousands of security professionals using S1C0N for their daily reconnaissance workflows.
                    </p>
                    <Link to="/register">
                        <Button size="lg" className="h-16 text-xl px-12 rounded-full shadow-2xl shadow-accent-primary/30 hover:shadow-accent-primary/50">
                            Start Scanning Now
                        </Button>
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 px-6 border-t border-border/10">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6 text-text-secondary text-sm">
                    <div className="flex items-center gap-2">
                        <img src={logo} alt="S1C0N" className="h-6 w-auto grayscale opacity-50" />
                        <span>© 2024 S1C0N Platform. All rights reserved.</span>
                    </div>
                    <div className="flex gap-8">
                        <a href="#" className="hover:text-accent-primary transition-colors">Privacy</a>
                        <a href="#" className="hover:text-accent-primary transition-colors">Terms</a>
                        <a href="#" className="hover:text-accent-primary transition-colors">Documentation</a>
                        <a href="#" className="hover:text-accent-primary transition-colors">GitHub</a>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default Landing;
