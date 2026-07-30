"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  MessageSquare, CheckCircle2, Clock, AlertTriangle, Activity,
  Wrench, TrendingUp, DollarSign, Building2, Bot, ArrowUpRight,
  ArrowDownRight, Zap, Shield
} from "lucide-react";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend
} from "recharts";
import { analyticsApi, complaintsApi } from "@/lib/api";
import { formatDistanceToNow } from "date-fns";

// ── Types ─────────────────────────────────────────────────────────────────────
interface KPIs {
  total_complaints: number;
  resolved: number;
  pending: number;
  in_progress: number;
  critical: number;
  resolution_rate: number;
  total_maintenance_cost: number;
  avg_resolution_hours: number;
  building_health_score: number;
  active_technicians: number;
}

const PRIORITY_COLORS: Record<string, string> = {
  low: "#10b981",
  medium: "#3b82f6",
  high: "#f59e0b",
  critical: "#f97316",
  emergency: "#ef4444",
};

const CATEGORY_COLORS = ["#6366f1", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#f43f5e", "#3b82f6"];

function KPICard({ title, value, subtitle, icon: Icon, color, trend }: {
  title: string; value: string | number; subtitle?: string;
  icon: React.ElementType; color: string; trend?: { value: number; positive: boolean };
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="kpi-card"
    >
      <div className="flex items-start justify-between">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center`} style={{ backgroundColor: `${color}20`, border: `1px solid ${color}30` }}>
          <Icon className="w-5 h-5" style={{ color }} />
        </div>
        {trend && (
          <div className={`flex items-center gap-0.5 text-xs font-medium ${trend.positive ? "text-green-400" : "text-red-400"}`}>
            {trend.positive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
            {Math.abs(trend.value)}%
          </div>
        )}
      </div>
      <div>
        <div className="text-2xl font-bold tabular-nums">{value}</div>
        <div className="text-sm font-medium text-foreground/80">{title}</div>
        {subtitle && <div className="text-xs text-muted-foreground mt-0.5">{subtitle}</div>}
      </div>
    </motion.div>
  );
}

export default function DashboardPage() {
  const [kpis, setKpis] = useState<KPIs | null>(null);
  const [byCategory, setByCategory] = useState<Record<string, number>>({});
  const [byPriority, setByPriority] = useState<Record<string, number>>({});
  const [trend, setTrend] = useState<Array<{ date: string; count: number }>>([]);
  const [recentComplaints, setRecentComplaints] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [buildingHealth, setBuildingHealth] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([
      analyticsApi.dashboard(),
      complaintsApi.list({ limit: 6 }),
      analyticsApi.buildingHealth(),
    ]).then(([analyticsRes, complaintsRes, healthRes]) => {
      const data = analyticsRes.data;
      setKpis(data.kpis);
      setByCategory(data.by_category || {});
      setByPriority(data.by_priority || {});
      setTrend(data.trend || []);
      setRecentComplaints(complaintsRes.data?.data || []);
      setBuildingHealth(healthRes.data || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const categoryData = Object.entries(byCategory).map(([name, value], i) => ({
    name: name.replace("_", " "),
    value,
    color: CATEGORY_COLORS[i % CATEGORY_COLORS.length],
  }));

  const priorityData = Object.entries(byPriority).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
    color: PRIORITY_COLORS[name] || "#6366f1",
  }));

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="kpi-card">
            <div className="w-10 h-10 rounded-xl shimmer" />
            <div className="space-y-2">
              <div className="h-7 w-20 rounded shimmer" />
              <div className="h-4 w-28 rounded shimmer" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Operations Dashboard</h1>
          <p className="text-muted-foreground text-sm mt-0.5">Real-time overview of your facility intelligence</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1.5 glass-card rounded-xl text-xs">
            <Bot className="w-3.5 h-3.5 text-primary" />
            <span className="text-muted-foreground">10 AI Agents Active</span>
          </div>
          <a href="/dashboard/complaints/new">
            <button className="btn-primary text-sm">
              <MessageSquare className="w-4 h-4" />
              New Complaint
            </button>
          </a>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard title="Total Complaints" value={kpis?.total_complaints ?? 0} icon={MessageSquare} color="#6366f1" trend={{ value: 12, positive: false }} subtitle="Last 30 days" />
        <KPICard title="Pending" value={kpis?.pending ?? 0} icon={Clock} color="#f59e0b" subtitle="Awaiting resolution" />
        <KPICard title="Resolved" value={kpis?.resolved ?? 0} icon={CheckCircle2} color="#10b981" trend={{ value: 8, positive: true }} subtitle={`${kpis?.resolution_rate ?? 0}% rate`} />
        <KPICard title="Critical / Emergency" value={kpis?.critical ?? 0} icon={AlertTriangle} color="#ef4444" subtitle="Needs immediate attention" />
        <KPICard title="Building Health" value={`${kpis?.building_health_score?.toFixed(1) ?? 100}%`} icon={Shield} color="#06b6d4" subtitle="Average across all buildings" />
        <KPICard title="Active Technicians" value={kpis?.active_technicians ?? 0} icon={Wrench} color="#8b5cf6" subtitle="Currently available" />
        <KPICard title="Avg Resolution" value={`${kpis?.avg_resolution_hours?.toFixed(1) ?? 0}h`} icon={TrendingUp} color="#84cc16" trend={{ value: 5, positive: true }} subtitle="Mean time to resolve" />
        <KPICard title="Monthly Cost" value={`₹${((kpis?.total_maintenance_cost ?? 0) / 1000).toFixed(1)}K`} icon={DollarSign} color="#f97316" subtitle="Total maintenance spend" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Complaint Trend */}
        <div className="lg:col-span-2 glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-sm">Complaint Trend (30 days)</h2>
            <span className="text-xs text-muted-foreground">Daily count</span>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={trend.length ? trend : Array.from({ length: 30 }, (_, i) => ({ date: `Day ${i + 1}`, count: Math.floor(Math.random() * 15) + 2 }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: "rgba(255,255,255,0.4)" }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "rgba(255,255,255,0.4)" }} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{ background: "hsl(222 47% 8%)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "12px", fontSize: "12px" }}
                labelStyle={{ color: "rgba(255,255,255,0.6)" }}
              />
              <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2.5} dot={false} activeDot={{ r: 5, fill: "#6366f1" }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Category Breakdown */}
        <div className="glass-card p-5">
          <h2 className="font-semibold text-sm mb-4">By Category</h2>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={categoryData.length ? categoryData : [{ name: "No data", value: 1, color: "#6366f1" }]} cx="50%" cy="50%" innerRadius={55} outerRadius={90} dataKey="value" paddingAngle={3}>
                {(categoryData.length ? categoryData : [{ color: "#6366f1" }]).map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "hsl(222 47% 8%)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "12px", fontSize: "12px" }} />
              <Legend formatter={(value) => <span className="text-xs text-muted-foreground">{value}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Recent Complaints */}
        <div className="glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-sm">Recent Complaints</h2>
            <a href="/dashboard/complaints" className="text-xs text-primary hover:text-primary/80 transition-colors">
              View all →
            </a>
          </div>
          <div className="space-y-2">
            {recentComplaints.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">No complaints yet</p>
            ) : (
              recentComplaints.slice(0, 5).map((c: any) => (
                <a key={c.id} href={`/dashboard/complaints/${c.id}`}>
                  <div className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-white/5 transition-colors cursor-pointer">
                    <div className={`badge-${c.priority}`}>
                      {c.priority}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{c.title}</p>
                      <p className="text-xs text-muted-foreground">{c.ticket_number}</p>
                    </div>
                    <span className="text-xs text-muted-foreground flex-shrink-0">
                      {formatDistanceToNow(new Date(c.created_at), { addSuffix: true })}
                    </span>
                  </div>
                </a>
              ))
            )}
          </div>
        </div>

        {/* Building Health */}
        <div className="glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-sm">Building Health Scores</h2>
            <a href="/dashboard/buildings" className="text-xs text-primary hover:text-primary/80">View all →</a>
          </div>
          <div className="space-y-3">
            {buildingHealth.length === 0 ? (
              <div className="text-sm text-muted-foreground text-center py-4">No buildings configured</div>
            ) : (
              buildingHealth.slice(0, 5).map((b: any) => (
                <div key={b.id} className="space-y-1.5">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{b.name}</span>
                    <span className={`font-bold tabular-nums ${b.health_score >= 80 ? "text-green-400" : b.health_score >= 60 ? "text-yellow-400" : "text-red-400"}`}>
                      {b.health_score?.toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${b.health_score}%` }}
                      transition={{ delay: 0.2, duration: 0.8 }}
                      className="h-full rounded-full"
                      style={{
                        background: b.health_score >= 80 ? "#10b981" : b.health_score >= 60 ? "#f59e0b" : "#ef4444"
                      }}
                    />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
