"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { User, Lock, Bell, Database, Bot, Save, Loader2, Eye, EyeOff } from "lucide-react";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import toast from "react-hot-toast";

export default function SettingsPage() {
  const { user, setAuth, token } = useAuthStore();
  const [activeTab, setActiveTab] = useState("profile");
  const [saving, setSaving] = useState(false);
  const [name, setName] = useState(user?.full_name || "");
  const [phone, setPhone] = useState(user?.phone || "");
  const [showApiKey, setShowApiKey] = useState(false);

  const saveProfile = async () => {
    setSaving(true);
    try {
      const res = await authApi.updateMe({ full_name: name, phone });
      if (token) setAuth(token, { ...user!, full_name: name, phone });
      toast.success("Profile updated!");
    } catch (e) {
      toast.error("Failed to save profile");
    } finally {
      setSaving(false);
    }
  };

  const TABS = [
    { id: "profile", label: "Profile", icon: User },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "ai", label: "AI Configuration", icon: Bot },
    { id: "system", label: "System", icon: Database },
  ];

  return (
    <div className="max-w-3xl space-y-5">
      <div>
        <h1 className="text-2xl font-bold gradient-text">Settings</h1>
        <p className="text-muted-foreground text-sm">Manage your account and platform configuration</p>
      </div>

      <div className="flex gap-1 glass-card p-1 rounded-xl w-fit">
        {TABS.map((tab) => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id ? "bg-primary/20 text-primary" : "text-muted-foreground hover:text-foreground"}`}>
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "profile" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card p-6 space-y-5">
          <h2 className="font-semibold">Profile Information</h2>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-primary/20 border-2 border-primary/20 flex items-center justify-center text-2xl font-bold text-primary">
              {user?.full_name?.[0] || "U"}
            </div>
            <div>
              <p className="font-medium">{user?.full_name}</p>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
              <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20 capitalize mt-1 inline-block">
                {user?.role?.replace("_", " ")}
              </span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Full Name</label>
              <input value={name} onChange={(e) => setName(e.target.value)} className="bw-input" />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Phone Number</label>
              <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+91 XXXXX XXXXX" className="bw-input" />
            </div>
            <div className="space-y-1.5 col-span-2">
              <label className="text-sm font-medium">Email (read-only)</label>
              <input value={user?.email || ""} disabled className="bw-input opacity-50 cursor-not-allowed" />
            </div>
          </div>
          <button onClick={saveProfile} disabled={saving} className="btn-primary text-sm">
            {saving ? <><Loader2 className="w-4 h-4 animate-spin" /> Saving…</> : <><Save className="w-4 h-4" /> Save Profile</>}
          </button>
        </motion.div>
      )}

      {activeTab === "ai" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card p-6 space-y-5">
          <h2 className="font-semibold">AI Configuration</h2>
          <div className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">LLM Provider</label>
              <select className="bw-input">
                <option value="ollama">🦙 Ollama (Local — Llama 3.1)</option>
                <option value="openai">🌐 OpenAI GPT-4o</option>
                <option value="anthropic">🤖 Anthropic Claude</option>
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">OpenAI API Key</label>
              <div className="relative">
                <input type={showApiKey ? "text" : "password"} placeholder="sk-..." className="bw-input pr-10" />
                <button onClick={() => setShowApiKey(!showApiKey)} type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                  {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Ollama Server URL</label>
              <input defaultValue="http://localhost:11434" className="bw-input" />
            </div>
            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
              <p className="text-xs text-amber-400">⚠️ API key changes require a backend restart to take effect. Update the .env file and redeploy for production.</p>
            </div>
          </div>
        </motion.div>
      )}

      {activeTab === "notifications" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card p-6 space-y-4">
          <h2 className="font-semibold">Notification Preferences</h2>
          {[
            { label: "Emergency alerts", desc: "Immediate notifications for critical/emergency complaints", enabled: true },
            { label: "Assignment notifications", desc: "When a complaint is assigned to you", enabled: true },
            { label: "Status updates", desc: "When complaint status changes", enabled: true },
            { label: "Prediction alerts", desc: "When equipment failure probability exceeds threshold", enabled: true },
            { label: "Daily digest", desc: "Daily summary of facility activity", enabled: false },
          ].map((item) => (
            <div key={item.label} className="flex items-start justify-between p-3 rounded-xl bg-white/[0.02] border border-white/5">
              <div>
                <p className="text-sm font-medium">{item.label}</p>
                <p className="text-xs text-muted-foreground">{item.desc}</p>
              </div>
              <div className={`w-10 h-5 rounded-full cursor-pointer transition-colors ${item.enabled ? "bg-primary" : "bg-white/10"}`}>
                <div className={`w-4 h-4 rounded-full bg-white shadow transition-transform m-0.5 ${item.enabled ? "translate-x-5" : "translate-x-0"}`} />
              </div>
            </div>
          ))}
        </motion.div>
      )}

      {activeTab === "system" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card p-6 space-y-4">
          <h2 className="font-semibold">System Information</h2>
          <div className="space-y-2">
            {[
              { label: "Platform", value: "BuildWise AI v1.0.0" },
              { label: "API Version", value: "v1" },
              { label: "Database", value: "PostgreSQL (Async)" },
              { label: "Vector DB", value: "ChromaDB" },
              { label: "ML Models", value: "XGBoost + Isolation Forest" },
              { label: "CV Model", value: "YOLOv8n" },
              { label: "Agent Framework", value: "LangGraph / Custom Pipeline" },
            ].map((item) => (
              <div key={item.label} className="flex justify-between py-2 border-b border-white/5 last:border-0">
                <span className="text-sm text-muted-foreground">{item.label}</span>
                <span className="text-sm font-mono text-primary">{item.value}</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
