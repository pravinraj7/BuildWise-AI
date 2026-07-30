"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Plus, Search, Star, Wrench, Phone, Mail, X, Loader2, AlertCircle
} from "lucide-react";
import { techniciansApi, getErrorMessage } from "@/lib/api";

const STATUS_CONFIG: Record<string, { label: string; color: string; dot: string }> = {
  available: { label: "Available", color: "text-green-400", dot: "bg-green-500" },
  busy: { label: "Busy", color: "text-amber-400", dot: "bg-amber-500" },
  off_duty: { label: "Off Duty", color: "text-muted-foreground", dot: "bg-slate-500" },
  on_leave: { label: "On Leave", color: "text-blue-400", dot: "bg-blue-500" },
};

const INITIAL_FORM = {
  employee_id: "",
  full_name: "",
  email: "",
  phone: "",
  specialization: "",
  experience_years: 0,
  skills: "",
  certifications: "",
  max_concurrent_jobs: 3,
  shift_start: "09:00",
  shift_end: "18:00",
};

export default function TechniciansPage() {
  const [technicians, setTechnicians] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(INITIAL_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState("");

  const fetchTechnicians = async () => {
    setLoading(true);
    try {
      const res = await techniciansApi.list({ search, status: statusFilter, limit: 50 });
      setTechnicians(res.data?.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchTechnicians(); }, [statusFilter]);
  useEffect(() => {
    const t = setTimeout(fetchTechnicians, 400);
    return () => clearTimeout(t);
  }, [search]);

  const stats = {
    total: technicians.length,
    available: technicians.filter((t) => t.status === "available").length,
    busy: technicians.filter((t) => t.status === "busy").length,
    avgRating: technicians.length
      ? (technicians.reduce((s, t) => s + (t.rating || 0), 0) / technicians.length).toFixed(1)
      : "—",
  };

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: name === "experience_years" || name === "max_concurrent_jobs" ? Number(value) : value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        skills: form.skills ? form.skills.split(",").map((s) => s.trim()).filter(Boolean) : [],
        certifications: form.certifications ? form.certifications.split(",").map((s) => s.trim()).filter(Boolean) : [],
        work_days: ["Mon", "Tue", "Wed", "Thu", "Fri"],
      };
      await techniciansApi.create(payload);
      setShowModal(false);
      setForm(INITIAL_FORM);
      fetchTechnicians();
    } catch (err: any) {
      setFormError(getErrorMessage(err, "Failed to create technician"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Technicians</h1>
          <p className="text-muted-foreground text-sm">Manage your maintenance workforce</p>
        </div>
        <button id="add-technician-btn" className="btn-primary text-sm" onClick={() => setShowModal(true)}>
          <Plus className="w-4 h-4" /> Add Technician
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: "Total", value: stats.total, color: "#6366f1" },
          { label: "Available", value: stats.available, color: "#10b981" },
          { label: "Busy", value: stats.busy, color: "#f59e0b" },
          { label: "Avg Rating", value: `⭐ ${stats.avgRating}`, color: "#f97316" },
        ].map((s) => (
          <div key={s.label} className="glass-card p-3 text-center">
            <div className="text-xl font-bold" style={{ color: s.color }}>{s.value}</div>
            <div className="text-xs text-muted-foreground">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="glass-card p-4 flex gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input type="text" placeholder="Search technicians…" value={search} onChange={(e) => setSearch(e.target.value)} className="bw-input pl-9" />
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="bw-input w-40">
          <option value="">All Status</option>
          <option value="available">Available</option>
          <option value="busy">Busy</option>
          <option value="off_duty">Off Duty</option>
        </select>
      </div>

      {/* Technician Cards */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="glass-card p-5 space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full shimmer" />
                <div className="space-y-2 flex-1">
                  <div className="h-4 w-3/4 shimmer rounded" />
                  <div className="h-3 w-1/2 shimmer rounded" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : technicians.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <Wrench className="w-12 h-12 mx-auto text-muted-foreground/30 mb-3" />
          <p className="text-muted-foreground">No technicians found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {technicians.map((tech: any, i: number) => {
            const sc = STATUS_CONFIG[tech.status] || STATUS_CONFIG.available;
            const completionRate = tech.total_jobs ? Math.round((tech.completed_jobs / tech.total_jobs) * 100) : 0;
            return (
              <motion.div
                key={tech.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className="glass-card-hover p-5 space-y-4"
              >
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <div className="w-12 h-12 rounded-full bg-primary/20 border-2 border-primary/20 flex items-center justify-center text-lg font-bold text-primary">
                        {tech.full_name?.[0] || "T"}
                      </div>
                      <div className={`absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full border-2 border-background ${sc.dot}`} />
                    </div>
                    <div>
                      <p className="font-semibold text-sm">{tech.full_name}</p>
                      <p className="text-xs text-muted-foreground">{tech.employee_id}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 text-amber-400 text-xs font-bold">
                    <Star className="w-3 h-3 fill-amber-400" />
                    {tech.rating?.toFixed(1) || "—"}
                  </div>
                </div>

                {/* Skills */}
                <div className="flex flex-wrap gap-1">
                  {(tech.skills || []).map((skill: string) => (
                    <span key={skill} className="px-2 py-0.5 rounded-full text-[10px] bg-primary/10 text-primary border border-primary/20 capitalize">{skill}</span>
                  ))}
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="p-1.5 rounded-lg bg-white/[0.02]">
                    <div className="text-sm font-bold">{tech.total_jobs || 0}</div>
                    <div className="text-[10px] text-muted-foreground">Jobs</div>
                  </div>
                  <div className="p-1.5 rounded-lg bg-white/[0.02]">
                    <div className="text-sm font-bold">{completionRate}%</div>
                    <div className="text-[10px] text-muted-foreground">Completion</div>
                  </div>
                  <div className="p-1.5 rounded-lg bg-white/[0.02]">
                    <div className="text-sm font-bold">{tech.experience_years || 0}yr</div>
                    <div className="text-[10px] text-muted-foreground">Exp.</div>
                  </div>
                </div>

                {/* Workload bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Workload</span>
                    <span>{tech.current_workload}/{tech.max_concurrent_jobs} jobs</span>
                  </div>
                  <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${((tech.current_workload || 0) / (tech.max_concurrent_jobs || 3)) * 100}%`,
                        background: (tech.current_workload || 0) >= (tech.max_concurrent_jobs || 3) ? "#ef4444" : "#6366f1"
                      }}
                    />
                  </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between pt-2 border-t border-white/5">
                  <span className={`flex items-center gap-1 text-xs ${sc.color}`}>
                    <div className={`w-1.5 h-1.5 rounded-full ${sc.dot}`} />
                    {sc.label}
                  </span>
                  <div className="flex gap-2 text-muted-foreground">
                    <a href={`tel:${tech.phone}`} className="hover:text-foreground transition-colors"><Phone className="w-3.5 h-3.5" /></a>
                    <a href={`mailto:${tech.email}`} className="hover:text-foreground transition-colors"><Mail className="w-3.5 h-3.5" /></a>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Add Technician Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShowModal(false)} />
            <motion.div
              className="relative z-10 glass-card w-full max-w-lg p-6 space-y-5 max-h-[90vh] overflow-y-auto"
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold gradient-text">Add Technician</h2>
                  <p className="text-xs text-muted-foreground">Fill in the technician's details</p>
                </div>
                <button onClick={() => setShowModal(false)} className="p-1.5 rounded-lg hover:bg-white/5 transition-colors text-muted-foreground hover:text-foreground">
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-xs text-muted-foreground font-medium">Employee ID *</label>
                    <input id="tech-employee-id" name="employee_id" required value={form.employee_id} onChange={handleFormChange} placeholder="EMP-001" className="bw-input w-full" />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-muted-foreground font-medium">Full Name *</label>
                    <input id="tech-full-name" name="full_name" required value={form.full_name} onChange={handleFormChange} placeholder="John Smith" className="bw-input w-full" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-xs text-muted-foreground font-medium">Email *</label>
                    <input id="tech-email" name="email" type="email" required value={form.email} onChange={handleFormChange} placeholder="john@example.com" className="bw-input w-full" />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-muted-foreground font-medium">Phone *</label>
                    <input id="tech-phone" name="phone" required value={form.phone} onChange={handleFormChange} placeholder="+1 555-0100" className="bw-input w-full" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-xs text-muted-foreground font-medium">Specialization</label>
                    <input id="tech-specialization" name="specialization" value={form.specialization} onChange={handleFormChange} placeholder="HVAC, Electrical…" className="bw-input w-full" />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-muted-foreground font-medium">Experience (years)</label>
                    <input id="tech-experience" name="experience_years" type="number" min={0} value={form.experience_years} onChange={handleFormChange} className="bw-input w-full" />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-muted-foreground font-medium">Skills <span className="text-muted-foreground/60">(comma-separated)</span></label>
                  <input id="tech-skills" name="skills" value={form.skills} onChange={handleFormChange} placeholder="electrical, plumbing, hvac" className="bw-input w-full" />
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-muted-foreground font-medium">Certifications <span className="text-muted-foreground/60">(comma-separated)</span></label>
                  <input id="tech-certifications" name="certifications" value={form.certifications} onChange={handleFormChange} placeholder="OSHA-30, EPA-608" className="bw-input w-full" />
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="space-y-1">
                    <label className="text-xs text-muted-foreground font-medium">Max Jobs</label>
                    <input id="tech-max-jobs" name="max_concurrent_jobs" type="number" min={1} max={10} value={form.max_concurrent_jobs} onChange={handleFormChange} className="bw-input w-full" />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-muted-foreground font-medium">Shift Start</label>
                    <input id="tech-shift-start" name="shift_start" type="time" value={form.shift_start} onChange={handleFormChange} className="bw-input w-full" />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-muted-foreground font-medium">Shift End</label>
                    <input id="tech-shift-end" name="shift_end" type="time" value={form.shift_end} onChange={handleFormChange} className="bw-input w-full" />
                  </div>
                </div>

                {formError && (
                  <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg p-3">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    {formError}
                  </div>
                )}

                <div className="flex gap-3 pt-2">
                  <button type="button" onClick={() => setShowModal(false)} className="flex-1 px-4 py-2 rounded-lg border border-white/10 text-sm hover:bg-white/5 transition-colors">
                    Cancel
                  </button>
                  <button id="tech-submit-btn" type="submit" disabled={submitting} className="flex-1 btn-primary text-sm justify-center">
                    {submitting ? <><Loader2 className="w-4 h-4 animate-spin" /> Creating…</> : <><Plus className="w-4 h-4" /> Add Technician</>}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
