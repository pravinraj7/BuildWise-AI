"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  Plus, Search, Filter, MessageSquare, Clock, CheckCircle2,
  AlertTriangle, Loader2, ChevronRight, Building2
} from "lucide-react";
import { complaintsApi } from "@/lib/api";
import { formatDistanceToNow } from "date-fns";

const STATUS_COLORS: Record<string, string> = {
  submitted: "badge-submitted",
  ai_processing: "badge-in_progress",
  diagnosed: "badge-assigned",
  assigned: "badge-assigned",
  in_progress: "badge-in_progress",
  completed: "badge-completed",
  cancelled: "badge-submitted",
};

const PRIORITY_ICONS: Record<string, React.ElementType> = {
  low: CheckCircle2,
  medium: Clock,
  high: AlertTriangle,
  critical: AlertTriangle,
  emergency: AlertTriangle,
};

export default function ComplaintsPage() {
  const router = useRouter();
  const [complaints, setComplaints] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>({});
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const fetchComplaints = async () => {
    setLoading(true);
    try {
      const [listRes, statsRes] = await Promise.all([
        complaintsApi.list({ page, limit: 15, search, status: statusFilter, priority: priorityFilter }),
        complaintsApi.stats(),
      ]);
      setComplaints(listRes.data.data || []);
      setTotal(listRes.data.total || 0);
      setStats(statsRes.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchComplaints(); }, [page, statusFilter, priorityFilter]);
  useEffect(() => {
    const timeout = setTimeout(fetchComplaints, 400);
    return () => clearTimeout(timeout);
  }, [search]);

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Complaints</h1>
          <p className="text-muted-foreground text-sm">Manage and track all maintenance requests</p>
        </div>
        <button onClick={() => router.push("/dashboard/complaints/new")} className="btn-primary">
          <Plus className="w-4 h-4" /> New Complaint
        </button>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-5 gap-3">
        {[
          { label: "Total", value: stats.total ?? 0, color: "#6366f1" },
          { label: "Pending", value: stats.pending ?? 0, color: "#f59e0b" },
          { label: "In Progress", value: stats.in_progress ?? 0, color: "#3b82f6" },
          { label: "Resolved", value: stats.resolved ?? 0, color: "#10b981" },
          { label: "Critical", value: stats.critical ?? 0, color: "#ef4444" },
        ].map((s) => (
          <div key={s.label} className="glass-card p-3 text-center">
            <div className="text-xl font-bold" style={{ color: s.color }}>{s.value}</div>
            <div className="text-xs text-muted-foreground">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="glass-card p-4 flex flex-wrap items-center gap-3">
        <div className="flex-1 min-w-48 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search complaints..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bw-input pl-9"
          />
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="bw-input w-40">
          <option value="">All Statuses</option>
          <option value="submitted">Submitted</option>
          <option value="ai_processing">AI Processing</option>
          <option value="diagnosed">Diagnosed</option>
          <option value="assigned">Assigned</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>
        <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)} className="bw-input w-36">
          <option value="">All Priorities</option>
          <option value="emergency">Emergency</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        {loading ? (
          <div className="p-8 flex items-center justify-center">
            <Loader2 className="w-6 h-6 animate-spin text-primary" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/5">
                  {["Ticket", "Title", "Category", "Priority", "Status", "Building", "Created", ""].map((h) => (
                    <th key={h} className="text-left text-xs font-semibold text-muted-foreground px-4 py-3 first:pl-5">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.03]">
                {complaints.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="text-center text-muted-foreground py-10 text-sm">
                      No complaints found
                    </td>
                  </tr>
                ) : (
                  complaints.map((c, i) => {
                    const PIcon = PRIORITY_ICONS[c.priority] || Clock;
                    return (
                      <motion.tr
                        key={c.id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.03 }}
                        onClick={() => router.push(`/dashboard/complaints/${c.id}`)}
                        className="hover:bg-white/[0.02] cursor-pointer transition-colors"
                      >
                        <td className="px-4 py-3 pl-5">
                          <span className="text-xs font-mono text-primary">{c.ticket_number}</span>
                        </td>
                        <td className="px-4 py-3 max-w-[200px]">
                          <span className="text-sm font-medium truncate block">{c.title}</span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-xs text-muted-foreground capitalize">{c.category?.replace("_", " ")}</span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`badge-${c.priority}`}>{c.priority}</span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={STATUS_COLORS[c.status] || "badge-submitted"}>
                            {c.status?.replace("_", " ")}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-xs text-muted-foreground">{c.building_id ? "Building" : "—"}</span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-xs text-muted-foreground">
                            {formatDistanceToNow(new Date(c.created_at), { addSuffix: true })}
                          </span>
                        </td>
                        <td className="px-4 py-3 pr-5">
                          <ChevronRight className="w-4 h-4 text-muted-foreground" />
                        </td>
                      </motion.tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {total > 15 && (
          <div className="flex items-center justify-between px-5 py-3 border-t border-white/5">
            <span className="text-xs text-muted-foreground">Showing {(page - 1) * 15 + 1}–{Math.min(page * 15, total)} of {total}</span>
            <div className="flex gap-2">
              <button disabled={page === 1} onClick={() => setPage(page - 1)} className="btn-secondary text-xs px-3 py-1.5">← Prev</button>
              <button disabled={page * 15 >= total} onClick={() => setPage(page + 1)} className="btn-secondary text-xs px-3 py-1.5">Next →</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
