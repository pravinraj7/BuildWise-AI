"use client";

import { useState, useRef } from "react";
import { motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import {
  ArrowLeft, Upload, Mic, Image, Loader2, Bot, Sparkles,
  AlertTriangle, CheckCircle2, X, FileImage
} from "lucide-react";
import { complaintsApi, uploadsApi, agentsApi, buildingsApi, getErrorMessage } from "@/lib/api";
import { useEffect } from "react";
import { motion as m } from "framer-motion";

const schema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters"),
  description: z.string().min(20, "Please describe the issue in more detail"),
  building_id: z.string().min(1, "Please select a building"),
  category: z.string().min(1, "Please select a category"),
  floor_id: z.string().optional(),
  location_description: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

const CATEGORIES = [
  { value: "electrical", label: "⚡ Electrical" },
  { value: "plumbing", label: "🔧 Plumbing" },
  { value: "hvac", label: "❄️ HVAC / AC" },
  { value: "structural", label: "🏗️ Structural" },
  { value: "elevator", label: "🛗 Elevator / Lift" },
  { value: "fire_safety", label: "🔥 Fire Safety" },
  { value: "security", label: "🔒 Security" },
  { value: "cleaning", label: "🧹 Cleaning" },
  { value: "it_network", label: "📡 IT / Network" },
  { value: "general", label: "🔨 General" },
];

export default function NewComplaintPage() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [images, setImages] = useState<File[]>([]);
  const [imageUrls, setImageUrls] = useState<string[]>([]);
  const [buildings, setBuildings] = useState<any[]>([]);
  const [aiPriority, setAiPriority] = useState<any>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const { register, handleSubmit, watch, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { category: "", building_id: "" },
  });

  const description = watch("description");
  const title = watch("title");
  const category = watch("category");

  useEffect(() => {
    buildingsApi.list().then((res) => setBuildings(res.data)).catch(() => {});
  }, []);

  // Real-time AI priority analysis
  useEffect(() => {
    if (title?.length > 5 && description?.length > 20) {
      const timeout = setTimeout(async () => {
        setAnalyzing(true);
        try {
          const res = await agentsApi.analyzeComplaint({ title, description, category });
          setAiPriority(res.data);
        } catch (e) {}
        finally { setAnalyzing(false); }
      }, 1500);
      return () => clearTimeout(timeout);
    }
  }, [title, description, category]);

  const handleImageChange = (files: FileList | null) => {
    if (!files) return;
    const newFiles = Array.from(files).slice(0, 5);
    setImages((prev) => [...prev, ...newFiles].slice(0, 5));
    newFiles.forEach((file) => {
      const url = URL.createObjectURL(file);
      setImageUrls((prev) => [...prev, url].slice(0, 5));
    });
  };

  const onSubmit = async (data: FormData) => {
    setSubmitting(true);
    try {
      // Upload images first
      const uploadedUrls: string[] = [];
      for (const img of images) {
        const fd = new FormData();
        fd.append("file", img);
        try {
          const res = await uploadsApi.image(fd);
          uploadedUrls.push(res.data.file_url);
        } catch (e) {}
      }

      const res = await complaintsApi.create({ ...data });
      toast.success(`Complaint submitted! Ticket: ${res.data.ticket_number} 🤖 AI is analyzing...`);
      router.push(`/dashboard/complaints/${res.data.id}`);
    } catch (err: any) {
      toast.error(getErrorMessage(err, "Failed to submit complaint"));
    } finally {
      setSubmitting(false);
    }
  };

  const priorityColors: Record<string, string> = {
    emergency: "#ef4444", critical: "#f97316", high: "#f59e0b", medium: "#3b82f6", low: "#10b981"
  };

  return (
    <div className="max-w-3xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => router.back()} className="w-8 h-8 rounded-lg glass-card flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div>
          <h1 className="text-xl font-bold gradient-text">Submit Complaint</h1>
          <p className="text-muted-foreground text-sm">AI agents will automatically analyze and prioritize your request</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="lg:col-span-2 space-y-5">
          <div className="glass-card p-5 space-y-4">
            <h2 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">Issue Details</h2>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Issue Title *</label>
              <input {...register("title")} placeholder="e.g., Water leaking from ceiling in Room 302" className="bw-input" />
              {errors.title && <p className="text-xs text-red-400">{errors.title.message}</p>}
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Detailed Description *</label>
              <textarea
                {...register("description")}
                rows={5}
                placeholder="Describe the issue in detail — when it started, how severe it is, any safety concerns..."
                className="bw-input resize-none"
              />
              {errors.description && <p className="text-xs text-red-400">{errors.description.message}</p>}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Category *</label>
                <select {...register("category")} className="bw-input">
                  <option value="">Select category</option>
                  {CATEGORIES.map((c) => (
                    <option key={c.value} value={c.value}>{c.label}</option>
                  ))}
                </select>
                {errors.category && <p className="text-xs text-red-400">{errors.category.message}</p>}
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium">Building *</label>
                <select {...register("building_id")} className="bw-input">
                  <option value="">Select building</option>
                  {buildings.map((b: any) => (
                    <option key={b.id} value={b.id}>{b.name}</option>
                  ))}
                </select>
                {errors.building_id && <p className="text-xs text-red-400">{errors.building_id.message}</p>}
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Location Description</label>
              <input {...register("location_description")} placeholder="e.g., 3rd floor, near staircase B" className="bw-input" />
            </div>
          </div>

          {/* Image Upload */}
          <div className="glass-card p-5 space-y-3">
            <h2 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">Attachments</h2>
            <div
              onClick={() => fileRef.current?.click()}
              className="border-2 border-dashed border-white/10 rounded-xl p-6 text-center cursor-pointer hover:border-primary/40 transition-colors"
            >
              <Upload className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground">Click to upload images (max 5)</p>
              <p className="text-xs text-muted-foreground/50 mt-1">JPEG, PNG, WebP — 50MB max</p>
            </div>
            <input ref={fileRef} type="file" multiple accept="image/*" className="hidden" onChange={(e) => handleImageChange(e.target.files)} />

            {imageUrls.length > 0 && (
              <div className="flex gap-2 flex-wrap">
                {imageUrls.map((url, i) => (
                  <div key={i} className="relative w-20 h-20 rounded-xl overflow-hidden border border-white/10">
                    <img src={url} alt="" className="w-full h-full object-cover" />
                    <button
                      type="button"
                      onClick={() => {
                        setImages((p) => p.filter((_, j) => j !== i));
                        setImageUrls((p) => p.filter((_, j) => j !== i));
                      }}
                      className="absolute top-1 right-1 w-5 h-5 rounded-full bg-red-500/80 flex items-center justify-center"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button type="submit" disabled={submitting} className="btn-primary w-full py-3 text-base">
            {submitting ? (
              <><Loader2 className="w-4 h-4 animate-spin" /> Submitting…</>
            ) : (
              <><Bot className="w-4 h-4" /> Submit to AI Agents</>
            )}
          </button>
        </form>

        {/* AI Panel */}
        <div className="space-y-4">
          {/* Real-time AI analysis */}
          <div className="glass-card p-4 space-y-3">
            <div className="flex items-center gap-2">
              <Bot className="w-4 h-4 text-primary" />
              <span className="text-sm font-semibold gradient-text">AI Pre-Analysis</span>
              {analyzing && <Loader2 className="w-3 h-3 animate-spin text-muted-foreground" />}
            </div>

            {!aiPriority && !analyzing && (
              <p className="text-xs text-muted-foreground">Start typing your complaint to get instant AI analysis…</p>
            )}

            {aiPriority && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">Predicted Priority:</span>
                  <span
                    className={`badge-${aiPriority.priority}`}
                    style={{ borderColor: `${priorityColors[aiPriority.priority]}50` }}
                  >
                    {aiPriority.priority?.toUpperCase()}
                  </span>
                </div>
                {aiPriority.is_emergency && (
                  <div className="flex items-center gap-2 p-2 bg-red-500/10 border border-red-500/20 rounded-lg">
                    <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0" />
                    <span className="text-xs text-red-400">Emergency detected — immediate response triggered</span>
                  </div>
                )}
                {aiPriority.extracted_category && (
                  <div className="text-xs text-muted-foreground">
                    Detected category: <span className="text-foreground capitalize">{aiPriority.extracted_category}</span>
                  </div>
                )}
                {aiPriority.priority_reasoning && (
                  <p className="text-xs text-muted-foreground border-t border-white/5 pt-2 mt-2">{aiPriority.priority_reasoning}</p>
                )}
              </motion.div>
            )}
          </div>

          {/* Agent workflow info */}
          <div className="glass-card p-4 space-y-2">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">After submission, AI will:</p>
            {[
              "📋 Understand your complaint",
              "🔍 Diagnose the issue",
              "⚡ Set priority level",
              "📚 Find repair procedures",
              "👷 Assign best technician",
              "📅 Schedule repair slot",
              "💰 Estimate total cost",
            ].map((step, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-muted-foreground">
                <CheckCircle2 className="w-3 h-3 text-primary flex-shrink-0" />
                {step}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
