"use client";

import { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactFlow, {
  Node, Edge, Background, Controls, MiniMap,
  useNodesState, useEdgesState, MarkerType, Handle, Position,
} from "reactflow";
import "reactflow/dist/style.css";
import {
  Bot, Zap, CheckCircle2, Clock, AlertCircle,
  Play, RefreshCw, Info
} from "lucide-react";
import { agentsApi } from "@/lib/api";

const AGENT_DEFINITIONS = [
  { id: "coordinator",       label: "Coordinator",        emoji: "🎯", color: "#6366f1", desc: "Orchestrates all agents" },
  { id: "understanding",     label: "Understanding",       emoji: "🧠", color: "#3b82f6", desc: "Extracts issue details" },
  { id: "diagnosis",         label: "Diagnosis",           emoji: "🔍", color: "#8b5cf6", desc: "Diagnoses the problem" },
  { id: "priority",          label: "Priority",            emoji: "⚡", color: "#f59e0b", desc: "Classifies urgency" },
  { id: "knowledge",         label: "Knowledge RAG",       emoji: "📚", color: "#10b981", desc: "Retrieves procedures" },
  { id: "technician",        label: "Technician AI",       emoji: "👷", color: "#06b6d4", desc: "Recommends best tech" },
  { id: "scheduling",        label: "Scheduling",          emoji: "📅", color: "#ec4899", desc: "Optimizes schedule" },
  { id: "cost",              label: "Cost Estimator",      emoji: "💰", color: "#f97316", desc: "Predicts costs" },
  { id: "predictive",        label: "Predictive ML",       emoji: "🔮", color: "#84cc16", desc: "Predicts failures" },
  { id: "analytics",         label: "Analytics",           emoji: "📊", color: "#a855f7", desc: "Updates KPIs" },
];

type AgentStatus = "idle" | "running" | "completed" | "error";

function AgentNode({ data }: { data: any }) {
  return (
    <div className={`agent-node ${data.status}`} style={{ borderColor: data.status === "running" ? data.color : data.status === "completed" ? "#10b981" : data.status === "error" ? "#ef4444" : "rgba(255,255,255,0.08)" }}>
      <Handle type="target" position={Position.Top} style={{ background: data.color, border: "none", width: 8, height: 8 }} />
      <div className="flex flex-col items-center gap-1.5 px-2 py-1">
        <div className="text-2xl">{data.emoji}</div>
        <div className="text-xs font-semibold text-foreground">{data.label}</div>
        <div className="text-[10px] text-muted-foreground text-center">{data.desc}</div>
        <div className="flex items-center gap-1">
          {data.status === "running" && (
            <span className="flex items-center gap-1 text-[10px] text-primary">
              <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" /> Running
            </span>
          )}
          {data.status === "completed" && (
            <span className="flex items-center gap-1 text-[10px] text-green-400">
              <CheckCircle2 className="w-3 h-3" /> Done
            </span>
          )}
          {data.status === "idle" && (
            <span className="text-[10px] text-muted-foreground">Idle</span>
          )}
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} style={{ background: data.color, border: "none", width: 8, height: 8 }} />
    </div>
  );
}

const nodeTypes = { agentNode: AgentNode };

const FLOW_POSITIONS: Record<string, [number, number]> = {
  coordinator:   [400, 20],
  understanding: [200, 160],
  diagnosis:     [600, 160],
  priority:      [400, 300],
  knowledge:     [100, 440],
  technician:    [350, 440],
  scheduling:    [600, 440],
  cost:          [200, 580],
  predictive:    [450, 580],
  analytics:     [700, 580],
};

export default function AgentsPage() {
  const [statuses, setStatuses] = useState<Record<string, AgentStatus>>(
    Object.fromEntries(AGENT_DEFINITIONS.map((a) => [a.id, "idle"]))
  );
  const [selectedAgent, setSelectedAgent] = useState<typeof AGENT_DEFINITIONS[0] | null>(null);
  const [running, setRunning] = useState(false);

  // Build React Flow nodes
  const initialNodes: Node[] = AGENT_DEFINITIONS.map((agent) => ({
    id: agent.id,
    type: "agentNode",
    position: { x: FLOW_POSITIONS[agent.id][0], y: FLOW_POSITIONS[agent.id][1] },
    data: { ...agent, status: statuses[agent.id] },
  }));

  const initialEdges: Edge[] = [
    { id: "c-u", source: "coordinator", target: "understanding", animated: true, style: { stroke: "#6366f1", strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: "#6366f1" } },
    { id: "c-d", source: "coordinator", target: "diagnosis", animated: true, style: { stroke: "#6366f1", strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: "#6366f1" } },
    { id: "u-p", source: "understanding", target: "priority", style: { stroke: "#3b82f6", strokeWidth: 1.5 }, markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
    { id: "d-p", source: "diagnosis", target: "priority", style: { stroke: "#8b5cf6", strokeWidth: 1.5 }, markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
    { id: "p-k", source: "priority", target: "knowledge", style: { stroke: "#f59e0b", strokeWidth: 1.5 }, markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" } },
    { id: "p-t", source: "priority", target: "technician", style: { stroke: "#f59e0b", strokeWidth: 1.5 }, markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" } },
    { id: "p-s", source: "priority", target: "scheduling", style: { stroke: "#f59e0b", strokeWidth: 1.5 }, markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" } },
    { id: "t-c", source: "technician", target: "cost", style: { stroke: "#06b6d4", strokeWidth: 1.5 }, markerEnd: { type: MarkerType.ArrowClosed, color: "#06b6d4" } },
    { id: "s-c", source: "scheduling", target: "cost", style: { stroke: "#ec4899", strokeWidth: 1.5 }, markerEnd: { type: MarkerType.ArrowClosed, color: "#ec4899" } },
    { id: "c-pred", source: "cost", target: "predictive", style: { stroke: "#f97316", strokeWidth: 1.5 }, markerEnd: { type: MarkerType.ArrowClosed, color: "#f97316" } },
    { id: "pred-a", source: "predictive", target: "analytics", style: { stroke: "#84cc16", strokeWidth: 1.5 }, markerEnd: { type: MarkerType.ArrowClosed, color: "#84cc16" } },
  ];

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Demo simulation of agent pipeline
  const simulateWorkflow = async () => {
    setRunning(true);
    const order = ["coordinator", "understanding", "diagnosis", "priority", "knowledge", "technician", "scheduling", "cost", "predictive", "analytics"];
    
    for (const agentId of order) {
      setStatuses((prev) => ({ ...prev, [agentId]: "running" }));
      setNodes((nds) => nds.map((n) => n.id === agentId ? { ...n, data: { ...n.data, status: "running" } } : n));
      await new Promise((r) => setTimeout(r, 800 + Math.random() * 400));
      setStatuses((prev) => ({ ...prev, [agentId]: "completed" }));
      setNodes((nds) => nds.map((n) => n.id === agentId ? { ...n, data: { ...n.data, status: "completed" } } : n));
    }
    setRunning(false);
  };

  const resetWorkflow = () => {
    setStatuses(Object.fromEntries(AGENT_DEFINITIONS.map((a) => [a.id, "idle"])));
    setNodes((nds) => nds.map((n) => ({ ...n, data: { ...n.data, status: "idle" } })));
    setRunning(false);
  };

  return (
    <div className="space-y-5 h-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">AI Agent Workflow</h1>
          <p className="text-muted-foreground text-sm">Live visualization of the multi-agent orchestration pipeline</p>
        </div>
        <div className="flex gap-2">
          <button onClick={resetWorkflow} disabled={running} className="btn-secondary text-sm">
            <RefreshCw className="w-4 h-4" /> Reset
          </button>
          <button onClick={simulateWorkflow} disabled={running} className="btn-primary text-sm">
            {running ? (
              <><RefreshCw className="w-4 h-4 animate-spin" /> Running…</>
            ) : (
              <><Play className="w-4 h-4" /> Simulate Pipeline</>
            )}
          </button>
        </div>
      </div>

      {/* Agent Cards Row */}
      <div className="grid grid-cols-5 gap-2">
        {AGENT_DEFINITIONS.slice(0, 5).map((agent) => (
          <motion.div
            key={agent.id}
            whileHover={{ scale: 1.02 }}
            onClick={() => setSelectedAgent(agent)}
            className={`glass-card-hover p-3 cursor-pointer ${selectedAgent?.id === agent.id ? "border-primary/40" : ""}`}
          >
            <div className="flex items-center gap-2">
              <span className="text-xl">{agent.emoji}</span>
              <div>
                <p className="text-xs font-medium">{agent.label}</p>
                <div className={`w-1.5 h-1.5 rounded-full mt-1 ${statuses[agent.id] === "running" ? "bg-primary animate-pulse" : statuses[agent.id] === "completed" ? "bg-green-500" : "bg-muted-foreground/30"}`} />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* React Flow Canvas */}
      <div className="glass-card overflow-hidden" style={{ height: 600 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-right"
        >
          <Background color="rgba(255,255,255,0.03)" gap={24} />
          <Controls style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)" }} />
          <MiniMap
            nodeColor={(n) => n.data?.color || "#6366f1"}
            style={{ background: "rgba(0,0,0,0.5)", border: "1px solid rgba(255,255,255,0.08)" }}
          />
        </ReactFlow>
      </div>

      {/* Agent Detail Panel */}
      <AnimatePresence>
        {selectedAgent && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="glass-card p-5"
          >
            <div className="flex items-start gap-4">
              <div className="text-4xl">{selectedAgent.emoji}</div>
              <div>
                <h3 className="font-bold text-lg">{selectedAgent.label} Agent</h3>
                <p className="text-muted-foreground text-sm">{selectedAgent.desc}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className={`badge-${statuses[selectedAgent.id] === "completed" ? "completed" : statuses[selectedAgent.id] === "running" ? "in_progress" : "submitted"}`}>
                    {statuses[selectedAgent.id]}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
