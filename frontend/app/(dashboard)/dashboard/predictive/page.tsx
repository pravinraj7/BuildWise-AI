"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { analyticsApi, equipmentApi, predictionsApi } from "@/lib/api";
import { TrendingUp, AlertTriangle, Shield, Cpu, RefreshCw, Loader2, Zap } from "lucide-react";
import toast from "react-hot-toast";
import {
  RadialBarChart, RadialBar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell
} from "recharts";

function RiskBadge({ risk }: { risk: string }) {
  const colors: Record<string, string> = { critical: "badge-critical", high: "badge-high", medium: "badge-medium", low: "badge-low" };
  return <span className={colors[risk] || "badge-low"}>{risk}</span>;
}

function HealthGauge({ score }: { score: number }) {
  const color = score >= 80 ? "#10b981" : score >= 60 ? "#f59e0b" : "#ef4444";
  return (
    <div className="relative w-16 h-16">
      <svg viewBox="0 0 36 36" className="w-16 h-16 -rotate-90">
        <circle cx="18" cy="18" r="15" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="3" />
        <circle
          cx="18" cy="18" r="15" fill="none" stroke={color} strokeWidth="3"
          strokeDasharray={`${(score / 100) * 94} 94`}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-xs font-bold" style={{ color }}>{score.toFixed(0)}</span>
      </div>
    </div>
  );
}

export default function PredictivePage() {
  const [equipment, setEquipment] = useState<any[]>([]);
  const [riskData, setRiskData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [runningPrediction, setRunningPrediction] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      equipmentApi.list({ limit: 20 }),
      analyticsApi.equipmentRisk(),
    ]).then(([eqRes, riskRes]) => {
      setEquipment(eqRes.data?.data || []);
      setRiskData(riskRes.data || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const runPrediction = async (equipmentId: string, equipmentName: string) => {
    setRunningPrediction(equipmentId);
    try {
      await predictionsApi.run(equipmentId);
      toast.success(`Prediction started for ${equipmentName}`);
      // Refresh
      const res = await equipmentApi.list({ limit: 20 });
      setEquipment(res.data?.data || []);
    } catch (e) {
      toast.error("Failed to run prediction");
    } finally {
      setRunningPrediction(null);
    }
  };

  const barData = riskData.map((e) => ({
    name: e.name.length > 12 ? e.name.slice(0, 12) + "…" : e.name,
    probability: Math.round(e.failure_probability * 100),
    color: e.failure_probability >= 0.7 ? "#ef4444" : e.failure_probability >= 0.5 ? "#f97316" : "#f59e0b",
  }));

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold gradient-text">Predictive Maintenance</h1>
        <p className="text-muted-foreground text-sm">ML-powered failure prediction using XGBoost, LightGBM & Isolation Forest</p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Equipment Monitored", value: equipment.length, icon: Cpu, color: "#6366f1" },
          { label: "High Risk", value: riskData.filter((e) => e.failure_probability > 0.6).length, icon: AlertTriangle, color: "#ef4444" },
          { label: "Avg Health Score", value: `${equipment.length ? (equipment.reduce((s, e) => s + (e.health_score || 0), 0) / equipment.length).toFixed(1) : "—"}%`, icon: Shield, color: "#10b981" },
          { label: "Failures Predicted", value: riskData.length, icon: TrendingUp, color: "#f97316" },
        ].map((c) => (
          <div key={c.label} className="kpi-card">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${c.color}20`, border: `1px solid ${c.color}30` }}>
              <c.icon className="w-5 h-5" style={{ color: c.color }} />
            </div>
            <div>
              <div className="text-2xl font-bold">{c.value}</div>
              <div className="text-sm text-foreground/80">{c.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Risk chart */}
      {barData.length > 0 && (
        <div className="glass-card p-5">
          <h2 className="font-semibold text-sm mb-4">Failure Probability by Equipment</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={barData} margin={{ top: 0, right: 20, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: "rgba(255,255,255,0.4)" }} />
              <YAxis tick={{ fontSize: 11, fill: "rgba(255,255,255,0.4)" }} tickFormatter={(v) => `${v}%`} />
              <Tooltip
                formatter={(v) => `${v}%`}
                contentStyle={{ background: "hsl(222 47% 8%)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "12px", fontSize: "12px" }}
              />
              <Bar dataKey="probability" radius={[4, 4, 0, 0]}>
                {barData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Equipment table */}
      <div className="glass-card overflow-hidden">
        <div className="p-4 border-b border-white/5">
          <h2 className="font-semibold text-sm">Equipment Health Monitor</h2>
        </div>
        {loading ? (
          <div className="p-8 flex items-center justify-center">
            <Loader2 className="w-6 h-6 animate-spin text-primary" />
          </div>
        ) : equipment.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground text-sm">No equipment configured yet</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/5">
                  {["Equipment", "Type", "Health", "Failure Prob.", "RUL (days)", "Status", "Risk", ""].map((h) => (
                    <th key={h} className="text-left text-xs font-semibold text-muted-foreground px-4 py-3 first:pl-5">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.03]">
                {equipment.map((e: any, i: number) => (
                  <motion.tr key={e.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.04 }}>
                    <td className="px-4 py-3 pl-5">
                      <div>
                        <p className="text-sm font-medium">{e.name}</p>
                        {e.model_number && <p className="text-xs text-muted-foreground">{e.model_number}</p>}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs text-muted-foreground capitalize">{e.equipment_type?.replace("_", " ")}</span>
                    </td>
                    <td className="px-4 py-3">
                      <HealthGauge score={e.health_score || 100} />
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden w-16">
                          <div
                            className="h-full rounded-full"
                            style={{
                              width: `${(e.failure_probability || 0) * 100}%`,
                              background: (e.failure_probability || 0) >= 0.7 ? "#ef4444" : (e.failure_probability || 0) >= 0.5 ? "#f97316" : "#10b981"
                            }}
                          />
                        </div>
                        <span className="text-xs tabular-nums">{((e.failure_probability || 0) * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm tabular-nums">{e.remaining_useful_life_days ?? "—"}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`badge-${e.status === "operational" ? "completed" : e.status === "degraded" ? "high" : "critical"}`}>
                        {e.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <RiskBadge risk={e.failure_probability >= 0.7 ? "critical" : e.failure_probability >= 0.5 ? "high" : e.failure_probability >= 0.3 ? "medium" : "low"} />
                    </td>
                    <td className="px-4 py-3 pr-5">
                      <button
                        onClick={() => runPrediction(e.id, e.name)}
                        disabled={runningPrediction === e.id}
                        className="flex items-center gap-1 text-xs text-primary hover:text-primary/80 transition-colors"
                      >
                        {runningPrediction === e.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
                        Predict
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
