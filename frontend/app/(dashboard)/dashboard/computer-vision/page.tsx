"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useDropzone } from "react-dropzone";
import { Upload, Eye, AlertCircle, Loader2, Image as ImageIcon, CheckCircle2, ZoomIn } from "lucide-react";
import { cvApi } from "@/lib/api";
import toast from "react-hot-toast";

const SEVERITY_COLORS: Record<string, string> = { high: "#ef4444", medium: "#f59e0b", low: "#10b981" };

export default function ComputerVisionPage() {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [annotatedUrl, setAnnotatedUrl] = useState<string | null>(null);
  const [showAnnotated, setShowAnnotated] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;
    setImageFile(file);
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setAnnotatedUrl(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".jpg", ".jpeg", ".png", ".webp"] },
    maxFiles: 1,
  });

  const analyze = async () => {
    if (!imageFile) return;
    setAnalyzing(true);
    try {
      const fd = new FormData();
      fd.append("file", imageFile);
      const res = await cvApi.detect(fd);
      setResult(res.data);
      if (res.data.annotated_image_url) {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        setAnnotatedUrl(`${apiUrl}${res.data.annotated_image_url}`);
      }
      toast.success(`Detected ${res.data.detections?.length || 0} issues`);
    } catch (e: any) {
      toast.error("Analysis failed. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-5">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold gradient-text">Computer Vision</h1>
        <p className="text-muted-foreground text-sm">Upload building images for AI-powered damage detection using YOLOv8</p>
      </div>

      {/* Supported damage types */}
      <div className="glass-card p-4">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">Detectable Damage Types</p>
        <div className="flex flex-wrap gap-2">
          {["Pipe Leakage", "Wall Crack", "Broken Switch", "Broken Window", "Electrical Damage", "AC Damage", "Ceiling Damage", "Fire Damage", "Water Damage", "Structural Damage"].map((type) => (
            <span key={type} className="px-2.5 py-1 rounded-lg bg-primary/10 border border-primary/20 text-xs text-primary">
              {type}
            </span>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Upload Area */}
        <div className="space-y-4">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${isDragActive ? "border-primary bg-primary/5" : "border-white/10 hover:border-primary/40 hover:bg-white/[0.02]"}`}
          >
            <input {...getInputProps()} />
            {preview ? (
              <div className="space-y-3">
                <img src={preview} alt="Upload preview" className="max-h-64 mx-auto rounded-xl object-contain" />
                <p className="text-xs text-muted-foreground">{imageFile?.name}</p>
              </div>
            ) : (
              <div className="space-y-3">
                <ImageIcon className="w-12 h-12 mx-auto text-muted-foreground/40" />
                <div>
                  <p className="text-sm font-medium">Drop image here or click to upload</p>
                  <p className="text-xs text-muted-foreground mt-1">JPEG, PNG, WebP supported</p>
                </div>
              </div>
            )}
          </div>

          {imageFile && (
            <button onClick={analyze} disabled={analyzing} className="btn-primary w-full py-3">
              {analyzing ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing with YOLOv8…</>
              ) : (
                <><Eye className="w-4 h-4" /> Detect Damage</>
              )}
            </button>
          )}
        </div>

        {/* Results */}
        <div className="space-y-4">
          {!result && !analyzing && (
            <div className="glass-card p-8 text-center space-y-3">
              <ZoomIn className="w-10 h-10 mx-auto text-muted-foreground/30" />
              <p className="text-muted-foreground text-sm">Upload and analyze an image to see detection results</p>
            </div>
          )}

          {analyzing && (
            <div className="glass-card p-8 text-center space-y-3">
              <Loader2 className="w-10 h-10 mx-auto text-primary animate-spin" />
              <p className="text-sm font-medium">YOLOv8 analyzing image…</p>
              <p className="text-xs text-muted-foreground">Detecting structural, electrical, and plumbing issues</p>
            </div>
          )}

          {result && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
              {/* Summary */}
              <div className="glass-card p-4 space-y-3">
                <h3 className="font-semibold text-sm">Detection Summary</h3>
                <div className="grid grid-cols-3 gap-2">
                  <div className="text-center p-2 rounded-xl bg-white/[0.03]">
                    <div className="text-xl font-bold text-primary">{result.summary?.total_detections ?? 0}</div>
                    <div className="text-[10px] text-muted-foreground">Detected</div>
                  </div>
                  <div className="text-center p-2 rounded-xl bg-white/[0.03]">
                    <div className="text-xl font-bold" style={{ color: SEVERITY_COLORS[result.summary?.highest_severity] || "#10b981" }}>
                      {result.summary?.highest_severity || "none"}
                    </div>
                    <div className="text-[10px] text-muted-foreground">Max Severity</div>
                  </div>
                  <div className="text-center p-2 rounded-xl bg-white/[0.03]">
                    <div className="text-xl font-bold text-amber-400">{((result.summary?.avg_confidence ?? 0) * 100).toFixed(0)}%</div>
                    <div className="text-[10px] text-muted-foreground">Avg Confidence</div>
                  </div>
                </div>
              </div>

              {/* Annotated image toggle */}
              {annotatedUrl && (
                <div className="glass-card p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-sm">Annotated Image</h3>
                    <button onClick={() => setShowAnnotated(!showAnnotated)} className="text-xs text-primary hover:text-primary/80">
                      {showAnnotated ? "Hide" : "Show"} →
                    </button>
                  </div>
                  {showAnnotated && (
                    <img src={annotatedUrl} alt="Annotated" className="w-full rounded-xl object-contain border border-white/10" />
                  )}
                </div>
              )}

              {/* Detection list */}
              {result.detections?.length > 0 && (
                <div className="glass-card p-4 space-y-3">
                  <h3 className="font-semibold text-sm">Detections ({result.detections.length})</h3>
                  <div className="space-y-2">
                    {result.detections.map((d: any, i: number) => (
                      <div key={i} className="flex items-center gap-3 p-2.5 rounded-xl bg-white/[0.02] border border-white/5">
                        <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: SEVERITY_COLORS[d.severity] || "#6366f1" }} />
                        <div className="flex-1">
                          <p className="text-sm font-medium">{d.label}</p>
                          <p className="text-xs text-muted-foreground">Confidence: {(d.confidence * 100).toFixed(1)}%</p>
                        </div>
                        <span className={`badge-${d.severity === "high" ? "critical" : d.severity === "medium" ? "high" : "medium"}`}>
                          {d.severity}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {result.detections?.length === 0 && (
                <div className="glass-card p-5 text-center space-y-2">
                  <CheckCircle2 className="w-8 h-8 mx-auto text-green-400" />
                  <p className="text-sm font-medium text-green-400">No damage detected</p>
                  <p className="text-xs text-muted-foreground">The image appears to show normal building conditions</p>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
