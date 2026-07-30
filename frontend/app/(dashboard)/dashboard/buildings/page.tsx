"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Plus, Building2, MapPin, Trash2, Loader2, Users } from "lucide-react";
import { buildingsApi, getErrorMessage } from "@/lib/api";
import toast from "react-hot-toast";

const BUILDING_TYPE_ICONS: Record<string, string> = {
  college: "🎓", hospital: "🏥", office: "🏢", mall: "🏬",
  residential: "🏠", hotel: "🏨", factory: "🏭", airport: "✈️", general: "🏗️"
};

function HealthBar({ score }: { score: number }) {
  const color = score >= 80 ? "#10b981" : score >= 60 ? "#f59e0b" : "#ef4444";
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">Health Score</span>
        <span className="font-bold" style={{ color }}>{score?.toFixed(1)}%</span>
      </div>
      <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
        <motion.div initial={{ width: 0 }} animate={{ width: `${score}%` }} transition={{ delay: 0.3, duration: 0.8 }} className="h-full rounded-full" style={{ background: color }} />
      </div>
    </div>
  );
}

export default function BuildingsPage() {
  const [buildings, setBuildings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [name, setName] = useState("");
  const [type, setType] = useState("office");
  const [address, setAddress] = useState("");
  const [floors, setFloors] = useState(5);
  const [submitting, setSubmitting] = useState(false);

  const fetchBuildings = async () => {
    try {
      const res = await buildingsApi.list();
      setBuildings(res.data || []);
    } catch (e) {} finally { setLoading(false); }
  };

  useEffect(() => { fetchBuildings(); }, []);

  const addBuilding = async () => {
    if (!name.trim()) return;
    setSubmitting(true);
    try {
      const generatedCode = name.replace(/[^a-zA-Z0-9]/g, "").toUpperCase().slice(0, 6) + "-" + Math.floor(1000 + Math.random() * 9000);
      await buildingsApi.create({
        name,
        code: generatedCode,
        building_type: type,
        address: address || "N/A",
        total_floors: floors
      });
      toast.success("Building added!");
      setShowAdd(false);
      setName(""); setAddress("");
      fetchBuildings();
    } catch (e: any) {
      toast.error(getErrorMessage(e, "Failed to add building"));
    } finally { setSubmitting(false); }
  };

  const deleteBuilding = async (id: string) => {
    if (!confirm("Delete this building? This will remove all associated data.")) return;
    try {
      await buildingsApi.delete(id);
      setBuildings((b) => b.filter((x) => x.id !== id));
      toast.success("Building deleted");
    } catch (e) { toast.error("Failed to delete"); }
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Buildings</h1>
          <p className="text-muted-foreground text-sm">Manage your building portfolio</p>
        </div>
        <button onClick={() => setShowAdd(true)} className="btn-primary text-sm">
          <Plus className="w-4 h-4" /> Add Building
        </button>
      </div>

      {/* Add form */}
      {showAdd && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5 space-y-4">
          <h2 className="font-semibold text-sm">Add New Building</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Building Name *</label>
              <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g., Engineering Block A" className="bw-input" />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Type</label>
              <select value={type} onChange={(e) => setType(e.target.value)} className="bw-input">
                {Object.keys(BUILDING_TYPE_ICONS).map((t) => (
                  <option key={t} value={t}>{BUILDING_TYPE_ICONS[t]} {t.charAt(0).toUpperCase() + t.slice(1)}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Address</label>
              <input value={address} onChange={(e) => setAddress(e.target.value)} placeholder="Full address" className="bw-input" />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Total Floors</label>
              <input type="number" min={1} max={200} value={floors} onChange={(e) => setFloors(Number(e.target.value))} className="bw-input" />
            </div>
          </div>
          <div className="flex gap-2 justify-end">
            <button onClick={() => setShowAdd(false)} className="btn-secondary text-sm">Cancel</button>
            <button onClick={addBuilding} disabled={submitting || !name.trim()} className="btn-primary text-sm">
              {submitting ? <><Loader2 className="w-3 h-3 animate-spin" /> Adding…</> : "Add Building"}
            </button>
          </div>
        </motion.div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => <div key={i} className="glass-card p-5 h-48 shimmer" />)}
        </div>
      ) : buildings.length === 0 ? (
        <div className="glass-card p-12 text-center space-y-3">
          <Building2 className="w-12 h-12 mx-auto text-muted-foreground/30" />
          <p className="text-muted-foreground">No buildings yet. Add your first building to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {buildings.map((b: any, i: number) => (
            <motion.div key={b.id} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }} className="glass-card-hover p-5 space-y-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="text-2xl">{BUILDING_TYPE_ICONS[b.building_type] || "🏗️"}</div>
                  <div>
                    <h3 className="font-semibold">{b.name}</h3>
                    <p className="text-xs text-muted-foreground capitalize">{b.building_type} · {b.total_floors} floors</p>
                  </div>
                </div>
                <button onClick={() => deleteBuilding(b.id)} className="text-muted-foreground hover:text-red-400 transition-colors">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              {b.address && (
                <div className="flex items-start gap-2 text-xs text-muted-foreground">
                  <MapPin className="w-3 h-3 flex-shrink-0 mt-0.5" />
                  <span>{b.address}</span>
                </div>
              )}

              <HealthBar score={b.health_score || 100} />

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/5">
                <div className="text-center">
                  <div className="text-lg font-bold text-primary">{b.total_complaints || 0}</div>
                  <div className="text-[10px] text-muted-foreground">Complaints</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-amber-400">{b.active_complaints || 0}</div>
                  <div className="text-[10px] text-muted-foreground">Active</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
