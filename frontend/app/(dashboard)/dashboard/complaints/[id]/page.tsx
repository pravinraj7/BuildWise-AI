"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft, Bot, Wrench, Clock, CheckCircle2, AlertTriangle,
  MapPin, Building2, DollarSign, Calendar, User, Loader2,
  RefreshCw, Image
} from "lucide-react";
import { complaintsApi, agentsApi } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { formatDistanceToNow, format } from "date-fns";
import toast from "react-hot-toast";

const STATUS_STEPS = ["submitted", "ai_processing", "diagnosed", "assigned", "in_progress", "completed"];

function StatusStepper({ status }: { status: string }) {
  const idx = STATUS_STEPS.indexOf(status);
  return (
    <div className="flex items-center gap-0">
      {STATUS_STEPS.map((step, i) => (
        <div key={step} className="flex items-center">
          <div className={`flex flex-col items-center ${i <= idx ? "opacity-100" : "opacity-30"}`}>
            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-colors ${i < idx ? "bg-green-500 border-green-500 text-white" : i === idx ? "border-primary text-primary bg-primary/10" : "border-muted-foreground text-muted-foreground"}`}>
              {i < idx ? <CheckCircle2 className="w-4 h-4" /> : <span>{i + 1}</span>}
            </div>
            <span className="text-[9px] text-muted-foreground mt-1 capitalize hidden md:block">{step.replace("_", " ")}</span>
          </div>
          {i < STATUS_STEPS.length - 1 && (
            <div className={`h-0.5 w-8 md:w-12 mx-1 transition-colors ${i < idx ? "bg-green-500" : "bg-white/10"}`} />
          )}
        </div>
      ))}
    </div>
  );
}

export default function ComplaintDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuthStore();
  const [complaint, setComplaint] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const fetch = async () => {
    try {
      const res = await complaintsApi.get(id);
      setComplaint(res.data);
    } catch (e) {
      toast.error("Complaint not found");
      router.push("/dashboard/complaints");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetch(); }, [id]);

  const runAgents = async () => {
    setRunning(true);
    try {
      await agentsApi.run(id);
      toast.success("AI agents running…");
      setTimeout(fetch, 3000);
    } catch (e) {
      toast.error("Failed to run agents");
    } finally {
      setRunning(false);
    }
  };

  const updateStatus = async (newStatus: string) => {
    try {
      await complaintsApi.update(id, { status: newStatus });
      toast.success(`Status updated to ${newStatus.replace("_", " ")}`);
      fetch();
    } catch (e) {
      toast.error("Failed to update status");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-primary" />
      </div>
    );
  }

  if (!complaint) return null;

  return (
    <div className="max-w-4xl space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => router.back()} className="w-8 h-8 rounded-lg glass-card flex items-center justify-center text-muted-foreground hover:text-foreground">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold">{complaint.title}</h1>
            <span className={`badge-${complaint.priority}`}>{complaint.priority}</span>
          </div>
          <p className="text-muted-foreground text-sm">{complaint.ticket_number}</p>
        </div>
        <button onClick={runAgents} disabled={running} className="btn-secondary text-sm">
          {running ? <><Loader2 className="w-4 h-4 animate-spin" /> Running…</> : <><Bot className="w-4 h-4" /> Run AI Agents</>}
        </button>
      </div>

      {/* Status stepper */}
      <div className="glass-card p-5">
        <p className="text-xs text-muted-foreground mb-4 uppercase font-semibold tracking-wide">Workflow Progress</p>
        <StatusStepper status={complaint.status} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Main info */}
        <div className="lg:col-span-2 space-y-4">
          {/* Description */}
          <div className="glass-card p-5 space-y-3">
            <h2 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">Description</h2>
            <p className="text-sm leading-relaxed">{complaint.description}</p>
            <div className="flex flex-wrap gap-3 text-xs text-muted-foreground pt-2 border-t border-white/5">
              <span className="flex items-center gap-1"><Building2 className="w-3.5 h-3.5" /> {complaint.building_id ? "Building linked" : "No building"}</span>
              <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {complaint.location_description || "Location not specified"}</span>
              <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {formatDistanceToNow(new Date(complaint.created_at), { addSuffix: true })}</span>
            </div>
          </div>

          {/* AI Diagnosis */}
          {complaint.diagnosis && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5 space-y-3 border border-primary/20">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-primary" />
                <h2 className="font-semibold text-sm gradient-text">AI Diagnosis</h2>
              </div>
              <p className="text-sm leading-relaxed">{complaint.diagnosis}</p>
              {complaint.suggested_repair && (
                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                  <p className="text-xs font-medium text-muted-foreground mb-1">Suggested Repair</p>
                  <p className="text-sm">{complaint.suggested_repair}</p>
                </div>
              )}
              {complaint.priority_reasoning && (
                <div className="p-3 rounded-xl bg-primary/5 border border-primary/10">
                  <p className="text-xs font-medium text-muted-foreground mb-1">Priority Reasoning</p>
                  <p className="text-sm">{complaint.priority_reasoning}</p>
                </div>
              )}
            </motion.div>
          )}

          {/* Timeline */}
          {complaint.timeline?.length > 0 && (
            <div className="glass-card p-5 space-y-3">
              <h2 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">Timeline</h2>
              <div className="space-y-3">
                {complaint.timeline.map((event: any, i: number) => (
                  <div key={i} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <div className="w-7 h-7 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center flex-shrink-0">
                        <span className="text-[10px] text-primary">{i + 1}</span>
                      </div>
                      {i < complaint.timeline.length - 1 && <div className="w-0.5 h-full bg-white/5 mt-1" />}
                    </div>
                    <div className="pb-3">
                      <p className="text-sm font-medium">{event.action}</p>
                      {(event.notes || event.description) && (
                        <p className="text-xs text-muted-foreground">{event.notes || event.description}</p>
                      )}
                      <p className="text-[10px] text-muted-foreground mt-1">
                        {(() => {
                          const dateVal = event.timestamp || event.created_at;
                          if (!dateVal) return "Just now";
                          try {
                            return format(new Date(dateVal), "MMM d, yyyy h:mm a");
                          } catch (err) {
                            return "Just now";
                          }
                        })()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Side panel */}
        <div className="space-y-4">
          {/* Action Card */}
          {user && ["super_admin", "facility_manager", "building_admin", "technician"].includes(user.role) && ["assigned", "in_progress"].includes(complaint.status) && (
            <div className="glass-card p-5 space-y-3 border border-emerald-500/10">
              <h2 className="font-semibold text-sm">Update Work Progress</h2>
              <p className="text-xs text-muted-foreground leading-relaxed">
                As the building operator, you can transition this complaint through the execution steps.
              </p>
              {complaint.status === "assigned" && (
                <button
                  onClick={() => updateStatus("in_progress")}
                  className="w-full btn-primary text-sm justify-center bg-emerald-500 hover:bg-emerald-600 border-none"
                >
                  <Wrench className="w-4 h-4" /> Start Work (In Progress)
                </button>
              )}
              {complaint.status === "in_progress" && (
                <button
                  onClick={() => updateStatus("completed")}
                  className="w-full btn-primary text-sm justify-center bg-blue-500 hover:bg-blue-600 border-none"
                >
                  <CheckCircle2 className="w-4 h-4" /> Mark as Completed
                </button>
              )}
            </div>
          )}
          
          {complaint.status === "completed" && (
            <div className="glass-card p-5 space-y-2 border border-blue-500/10 text-center">
              <span className="text-3xl">🎉</span>
              <h2 className="font-semibold text-sm text-blue-400">Complaint Resolved</h2>
              <p className="text-xs text-muted-foreground">
                This complaint is fully completed and resolved.
              </p>
            </div>
          )}
          {/* Cost estimates */}
          {complaint.estimated_total_cost && (
            <div className="glass-card p-5 space-y-3">
              <div className="flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-amber-400" />
                <h2 className="font-semibold text-sm">Cost Estimate</h2>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Labor</span>
                  <span>₹{complaint.estimated_labor_cost?.toFixed(0) || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Materials</span>
                  <span>₹{complaint.estimated_material_cost?.toFixed(0) || 0}</span>
                </div>
                <div className="flex justify-between text-sm font-bold border-t border-white/5 pt-2">
                  <span>Total</span>
                  <span className="text-amber-400">₹{complaint.estimated_total_cost?.toFixed(0)}</span>
                </div>
              </div>
            </div>
          )}

          {/* Assigned technician */}
          {complaint.assigned_technician_id && (
            <div className="glass-card p-5 space-y-3">
              <div className="flex items-center gap-2">
                <Wrench className="w-4 h-4 text-emerald-400" />
                <h2 className="font-semibold text-sm">Assigned Technician</h2>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center text-sm font-bold text-emerald-400">T</div>
                <div>
                  <p className="text-sm font-medium">Technician #{complaint.assigned_technician_id?.slice(-6)}</p>
                  <p className="text-xs text-muted-foreground">Assigned</p>
                </div>
              </div>
            </div>
          )}

          {/* Schedule */}
          {complaint.scheduled_start && (
            <div className="glass-card p-5 space-y-3">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-blue-400" />
                <h2 className="font-semibold text-sm">Scheduled</h2>
              </div>
              <p className="text-sm">{format(new Date(complaint.scheduled_start), "MMM d, yyyy h:mm a")}</p>
              {complaint.scheduled_end && (
                <p className="text-xs text-muted-foreground">Until {format(new Date(complaint.scheduled_end), "h:mm a")}</p>
              )}
            </div>
          )}

          {/* Metadata */}
          <div className="glass-card p-5 space-y-2">
            <h2 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide mb-3">Details</h2>
            {[
              { label: "Category", value: complaint.category?.replace("_", " "), icon: null },
              { label: "Status", value: complaint.status?.replace("_", " "), icon: null },
              { label: "AI Confidence", value: complaint.ai_confidence ? `${(complaint.ai_confidence * 100).toFixed(0)}%` : "—", icon: null },
              { label: "Submitted", value: format(new Date(complaint.created_at), "MMM d, yyyy"), icon: null },
            ].map((item) => (
              <div key={item.label} className="flex justify-between text-sm py-1.5 border-b border-white/[0.03] last:border-0">
                <span className="text-muted-foreground">{item.label}</span>
                <span className="font-medium capitalize">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
