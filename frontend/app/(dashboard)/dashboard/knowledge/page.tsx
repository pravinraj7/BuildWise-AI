"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Upload, Search, FileText, Trash2, MessageSquare, Loader2,
  BookOpen, Send, Bot, CheckCircle2, X, FileUp
} from "lucide-react";
import { knowledgeApi, getErrorMessage } from "@/lib/api";
import toast from "react-hot-toast";
import { formatDistanceToNow } from "date-fns";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hello! I'm your BuildWise AI knowledge assistant. I can help you find repair procedures, safety guidelines, equipment manuals, and building regulations. What would you like to know?",
      sources: [],
    }
  ]);
  const [question, setQuestion] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"chat" | "documents">("chat");

  const fetchDocuments = async () => {
    try {
      const res = await knowledgeApi.list();
      setDocuments(res.data || []);
    } catch (e) {}
    finally { setLoading(false); }
  };

  useEffect(() => { fetchDocuments(); }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const fd = new FormData();
    fd.append("file", file);
    fd.append("title", file.name.replace(/\.[^/.]+$/, ""));
    fd.append("document_type", "manual");
    try {
      await knowledgeApi.upload(fd);
      toast.success("Document uploaded! AI is indexing it into the knowledge base…");
      fetchDocuments();
    } catch (e: any) {
      toast.error(getErrorMessage(e, "Upload failed"));
    } finally {
      setUploading(false);
    }
  };

  const sendMessage = async () => {
    if (!question.trim() || chatLoading) return;
    const q = question.trim();
    setQuestion("");
    setMessages((m) => [...m, { id: Date.now().toString(), role: "user", content: q }]);
    setChatLoading(true);
    try {
      const res = await knowledgeApi.chat(q);
      setMessages((m) => [...m, {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: res.data.answer || "I couldn't find relevant information in the knowledge base.",
        sources: res.data.sources || [],
      }]);
    } catch (e) {
      setMessages((m) => [...m, {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        sources: [],
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const deleteDocument = async (id: string) => {
    try {
      await knowledgeApi.delete(id);
      setDocuments((d) => d.filter((doc) => doc.id !== id));
      toast.success("Document deleted");
    } catch (e) {
      toast.error("Failed to delete document");
    }
  };

  return (
    <div className="space-y-5 h-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">Knowledge Base</h1>
          <p className="text-muted-foreground text-sm">RAG-powered document intelligence with semantic search</p>
        </div>
        <label className={`btn-primary cursor-pointer ${uploading ? "opacity-50 cursor-not-allowed" : ""}`}>
          {uploading ? <><Loader2 className="w-4 h-4 animate-spin" /> Uploading…</> : <><Upload className="w-4 h-4" /> Upload Document</>}
          <input type="file" accept=".pdf,.docx,.txt" className="hidden" onChange={handleUpload} disabled={uploading} />
        </label>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 glass-card p-1 w-fit rounded-xl">
        {[
          { key: "chat", label: "AI Chat", icon: Bot },
          { key: "documents", label: `Documents (${documents.length})`, icon: BookOpen },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.key ? "bg-primary/20 text-primary" : "text-muted-foreground hover:text-foreground"}`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "chat" ? (
        <div className="glass-card flex flex-col" style={{ height: "calc(100vh - 280px)" }}>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} gap-3`}
              >
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center flex-shrink-0 mt-1">
                    <Bot className="w-4 h-4 text-primary" />
                  </div>
                )}
                <div className={`max-w-[75%] rounded-2xl px-4 py-3 ${msg.role === "user" ? "bg-primary/20 border border-primary/20" : "glass-card"}`}>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-white/10">
                      <p className="text-[10px] text-muted-foreground mb-1">Sources:</p>
                      {msg.sources.map((s, i) => (
                        <span key={i} className="text-[10px] text-primary mr-2">📄 {s}</span>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
            {chatLoading && (
              <div className="flex justify-start gap-3">
                <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
                <div className="glass-card px-4 py-3 flex items-center gap-2">
                  <div className="flex gap-1">
                    {[0, 1, 2].map((i) => (
                      <div key={i} className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: `${i * 150}ms` }} />
                    ))}
                  </div>
                  <span className="text-xs text-muted-foreground">Searching knowledge base…</span>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-4 border-t border-white/5">
            <div className="flex gap-2">
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
                placeholder="Ask about repair procedures, safety guidelines, equipment specs…"
                className="bw-input flex-1"
              />
              <button onClick={sendMessage} disabled={chatLoading || !question.trim()} className="btn-primary px-4">
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {loading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="glass-card p-4 space-y-3">
                <div className="h-5 w-3/4 shimmer rounded" />
                <div className="h-3 w-1/2 shimmer rounded" />
                <div className="h-3 w-full shimmer rounded" />
              </div>
            ))
          ) : documents.length === 0 ? (
            <div className="col-span-3 text-center py-16 space-y-3">
              <FileUp className="w-12 h-12 mx-auto text-muted-foreground/30" />
              <p className="text-muted-foreground">No documents uploaded yet</p>
              <p className="text-sm text-muted-foreground/60">Upload PDFs, DOCX files, or text documents to build your knowledge base</p>
            </div>
          ) : (
            documents.map((doc: any) => (
              <motion.div key={doc.id} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="glass-card p-4 space-y-3">
                <div className="flex items-start justify-between">
                  <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-primary" />
                  </div>
                  <button onClick={() => deleteDocument(doc.id)} className="text-muted-foreground hover:text-red-400 transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <div>
                  <h3 className="font-medium text-sm truncate">{doc.title}</h3>
                  <p className="text-xs text-muted-foreground capitalize">{doc.document_type} · {doc.file_type?.toUpperCase()}</p>
                </div>
                <div className="flex items-center gap-2">
                  {doc.is_indexed ? (
                    <span className="flex items-center gap-1 text-[10px] text-green-400">
                      <CheckCircle2 className="w-3 h-3" /> Indexed ({doc.chunk_count} chunks)
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-[10px] text-muted-foreground">
                      <Loader2 className="w-3 h-3 animate-spin" /> Indexing…
                    </span>
                  )}
                </div>
                <p className="text-[10px] text-muted-foreground">
                  {formatDistanceToNow(new Date(doc.created_at), { addSuffix: true })}
                </p>
              </motion.div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
