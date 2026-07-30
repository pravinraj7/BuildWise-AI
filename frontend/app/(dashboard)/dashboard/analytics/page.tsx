"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { analyticsApi } from "@/lib/api";
import { BarChart3, TrendingUp, Users, DollarSign } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Legend, AreaChart, Area
} from "recharts";

const COLORS = ["#6366f1", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#f43f5e", "#3b82f6"];

export default function AnalyticsPage() {
  const [dashboard, setDashboard] = useState<any>(null);
  const [techPerf, setTechPerf] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  useEffect(() => {
    Promise.all([
      analyticsApi.dashboard(undefined, days),
      analyticsApi.technicianPerformance(),
    ]).then(([dRes, tRes]) => {
      setDashboard(dRes.data);
      setTechPerf(tRes.data || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, [days]);

  const kpis = dashboard?.kpis || {};
  const trend = dashboard?.trend || [];
  const byCategory = Object.entries(dashboard?.by_category || {}).map(([name, value], i) => ({
    name: name.replace("_", " "), value, color: COLORS[i % COLORS.length]
  }));
  const byPriority = Object.entries(dashboard?.by_priority || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1), value,
    color: { low: "#10b981", medium: "#3b82f6", high: "#f59e0b", critical: "#f97316", emergency: "#ef4444" }[name] || "#6366f1"
  }));

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Analytics</h1>
          <p className="text-muted-foreground text-sm">Comprehensive facility performance intelligence</p>
        </div>
        <div className="flex gap-1 glass-card p-1 rounded-xl">
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-all ${days === d ? "bg-primary/20 text-primary" : "text-muted-foreground hover:text-foreground"}`}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-5 gap-3">
        {[
          { label: "Total", value: kpis.total_complaints || 0, color: "#6366f1" },
          { label: "Resolution Rate", value: `${kpis.resolution_rate || 0}%`, color: "#10b981" },
          { label: "Avg Hours", value: `${kpis.avg_resolution_hours || 0}h`, color: "#3b82f6" },
          { label: "Health Score", value: `${kpis.building_health_score || 100}%`, color: "#06b6d4" },
          { label: "Cost (₹)", value: `${((kpis.total_maintenance_cost || 0) / 1000).toFixed(1)}K`, color: "#f97316" },
        ].map((k) => (
          <div key={k.label} className="glass-card p-4 text-center">
            <div className="text-2xl font-bold tabular-nums" style={{ color: k.color }}>{k.value}</div>
            <div className="text-xs text-muted-foreground">{k.label}</div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Trend */}
        <div className="glass-card p-5">
          <h2 className="font-semibold text-sm mb-4">Complaint Trend</h2>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={trend}>
              <defs>
                <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.4)" }} />
              <YAxis tick={{ fontSize: 10, fill: "rgba(255,255,255,0.4)" }} />
              <Tooltip contentStyle={{ background: "hsl(222 47% 8%)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "12px" }} />
              <Area type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} fill="url(#grad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Category pie */}
        <div className="glass-card p-5">
          <h2 className="font-semibold text-sm mb-4">By Category</h2>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={byCategory} cx="45%" cy="50%" outerRadius={80} innerRadius={45} dataKey="value" paddingAngle={3}>
                {byCategory.map((e, i) => <Cell key={i} fill={e.color} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "hsl(222 47% 8%)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "12px" }} />
              <Legend formatter={(v) => <span className="text-xs text-muted-foreground">{v}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Priority bar */}
        <div className="glass-card p-5">
          <h2 className="font-semibold text-sm mb-4">By Priority</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={byPriority} margin={{ left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: "rgba(255,255,255,0.4)" }} />
              <YAxis tick={{ fontSize: 11, fill: "rgba(255,255,255,0.4)" }} />
              <Tooltip contentStyle={{ background: "hsl(222 47% 8%)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "12px" }} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {byPriority.map((e, i) => <Cell key={i} fill={e.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Technician performance */}
        <div className="glass-card p-5">
          <h2 className="font-semibold text-sm mb-4">Top Technicians</h2>
          <div className="space-y-3">
            {techPerf.slice(0, 5).map((t: any, i: number) => (
              <div key={t.id} className="flex items-center gap-3">
                <span className="text-muted-foreground text-sm w-4">{i + 1}</span>
                <div className="w-7 h-7 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary">
                  {t.name?.[0]}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{t.name}</p>
                  <div className="h-1 bg-white/5 rounded-full mt-1">
                    <div className="h-full rounded-full bg-primary" style={{ width: `${t.performance_score}%` }} />
                  </div>
                </div>
                <div className="text-right text-xs">
                  <div className="font-bold text-amber-400">⭐ {t.rating?.toFixed(1)}</div>
                  <div className="text-muted-foreground">{t.completed_jobs} jobs</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
