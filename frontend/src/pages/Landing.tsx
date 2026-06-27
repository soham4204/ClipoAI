import { useEffect, useState } from "react";
import { Activity, Cpu, Database, Video, Zap, Shield } from "lucide-react";

interface HealthCheck {
  status: string;
  service: string;
  checks: Record<string, { status: string; error?: string }>;
}

function StatusDot({ healthy }: { healthy: boolean }) {
  return (
    <span className="relative flex h-3 w-3">
      {healthy && (
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
      )}
      <span
        className={`relative inline-flex rounded-full h-3 w-3 ${
          healthy ? "bg-emerald-500" : "bg-red-500"
        }`}
      />
    </span>
  );
}

function ServiceCard({
  name,
  icon: Icon,
  status,
  description,
  delay,
}: {
  name: string;
  icon: React.ElementType;
  status: "healthy" | "unhealthy" | "checking";
  description: string;
  delay: string;
}) {
  return (
    <div
      className="glass-card p-6 hover:border-brand-500/30 transition-all duration-300 hover:-translate-y-1 group animate-fade-in"
      style={{ animationDelay: delay }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="p-2.5 rounded-xl bg-brand-600/10 text-brand-400 group-hover:bg-brand-600/20 transition-colors">
          <Icon className="w-5 h-5" />
        </div>
        <StatusDot
          healthy={status === "healthy"}
        />
      </div>
      <h3 className="font-semibold text-surface-100 mb-1">{name}</h3>
      <p className="text-sm text-surface-400">{description}</p>
      <div className="mt-3">
        <span
          className={`text-xs font-medium px-2.5 py-1 rounded-full ${
            status === "healthy"
              ? "bg-emerald-500/10 text-emerald-400"
              : status === "checking"
              ? "bg-amber-500/10 text-amber-400 animate-pulse-soft"
              : "bg-red-500/10 text-red-400"
          }`}
        >
          {status === "checking" ? "Checking..." : status}
        </span>
      </div>
    </div>
  );
}

export default function LandingPage() {
  const [health, setHealth] = useState<HealthCheck | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch("/api/health");
        const data = await res.json();
        setHealth(data);
      } catch {
        setHealth(null);
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatus = (service: string): "healthy" | "unhealthy" | "checking" => {
    if (loading) return "checking";
    if (!health) return "unhealthy";
    return health.checks[service]?.status === "healthy" ? "healthy" : "unhealthy";
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background gradient effects */}
      <div className="absolute inset-0 bg-surface-950" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-brand-600/8 rounded-full blur-[120px]" />
      <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-brand-800/10 rounded-full blur-[100px]" />

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-16">
        {/* Header */}
        <header className="text-center mb-20 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand-600/10 border border-brand-500/20 text-brand-400 text-sm font-medium mb-8">
            <Zap className="w-4 h-4" />
            <span>Platform Status Monitor</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6 tracking-tight">
            <span className="gradient-text">ClipoAI</span>
          </h1>

          <p className="text-xl text-surface-400 max-w-2xl mx-auto leading-relaxed">
            Enterprise AI Video Processing Platform — Transform long-form videos
            into publish-ready short-form content with intelligent AI agents.
          </p>
        </header>

        {/* Overall Status */}
        <div className="glass-card p-6 mb-12 glow animate-slide-up">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div
                className={`p-3 rounded-xl ${
                  health?.status === "healthy"
                    ? "bg-emerald-500/10"
                    : "bg-amber-500/10"
                }`}
              >
                <Activity
                  className={`w-6 h-6 ${
                    health?.status === "healthy"
                      ? "text-emerald-400"
                      : "text-amber-400"
                  }`}
                />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-surface-100">
                  System Health
                </h2>
                <p className="text-sm text-surface-400">
                  {loading
                    ? "Checking services..."
                    : health?.status === "healthy"
                    ? "All systems operational"
                    : "Some services need attention"}
                </p>
              </div>
            </div>
            <StatusDot healthy={health?.status === "healthy"} />
          </div>
        </div>

        {/* Service Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          <ServiceCard
            name="PostgreSQL"
            icon={Database}
            status={getStatus("postgres")}
            description="Primary database for video metadata, users, and processing jobs"
            delay="0.1s"
          />
          <ServiceCard
            name="Redis"
            icon={Cpu}
            status={getStatus("redis")}
            description="In-memory cache and job queue broker for background workers"
            delay="0.2s"
          />
          <ServiceCard
            name="FastAPI Backend"
            icon={Zap}
            status={loading ? "checking" : health ? "healthy" : "unhealthy"}
            description="REST API server handling authentication, uploads, and orchestration"
            delay="0.3s"
          />
          <ServiceCard
            name="MinIO Storage"
            icon={Video}
            status={loading ? "checking" : "healthy"}
            description="S3-compatible object storage for video files and generated content"
            delay="0.4s"
          />
          <ServiceCard
            name="Qdrant"
            icon={Database}
            status={loading ? "checking" : "healthy"}
            description="Vector database for semantic search and transcript embeddings"
            delay="0.5s"
          />
          <ServiceCard
            name="Monitoring"
            icon={Shield}
            status={loading ? "checking" : "healthy"}
            description="Prometheus, Grafana & Loki for metrics, dashboards, and log aggregation"
            delay="0.6s"
          />
        </div>

        {/* Footer */}
        <footer className="text-center text-surface-500 text-sm">
          <p>
            ClipoAI v0.1.0 — Phase 1: Foundation & Intelligent Data Ingestion
          </p>
        </footer>
      </div>
    </div>
  );
}
