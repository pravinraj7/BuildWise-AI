"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard, MessageSquare, Bot, Users, Wrench,
  BarChart3, BookOpen, Activity, Settings, Bell, LogOut,
  Building2, Menu, X, ChevronRight, Zap, ShieldAlert,
  TrendingUp, Eye
} from "lucide-react";
import Image from "next/image";
import { useAuthStore, useUIStore } from "@/lib/store";
import { notificationsApi } from "@/lib/api";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, group: "main" },
  { href: "/dashboard/complaints", label: "Complaints", icon: MessageSquare, group: "main" },
  { href: "/dashboard/agents", label: "AI Agents", icon: Bot, group: "ai", badge: "LIVE" },
  { href: "/dashboard/predictive", label: "Predictive ML", icon: TrendingUp, group: "ai" },
  { href: "/dashboard/computer-vision", label: "Computer Vision", icon: Eye, group: "ai" },
  { href: "/dashboard/knowledge", label: "Knowledge Base", icon: BookOpen, group: "ai" },
  { href: "/dashboard/technicians", label: "Technicians", icon: Wrench, group: "people" },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3, group: "insights" },
  { href: "/dashboard/buildings", label: "Buildings", icon: Building2, group: "settings" },
  { href: "/dashboard/settings", label: "Settings", icon: Settings, group: "settings" },
];

const groupLabels: Record<string, string> = {
  main: "Overview",
  ai: "AI Intelligence",
  people: "People",
  insights: "Insights",
  settings: "Administration",
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const [unreadCount, setUnreadCount] = useState(0);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Load unread notification count
    notificationsApi.unreadCount().then((res) => setUnreadCount(res.data.unread_count)).catch(() => {});
  }, []);

  if (!mounted) return null;

  const groups = [...new Set(navItems.map((i) => i.group))];

  return (
    <div className="min-h-screen flex">
      {/* ── Sidebar ──────────────────────────────────────────────────────── */}
      <AnimatePresence mode="wait">
        {sidebarOpen && (
          <motion.aside
            key="sidebar"
            initial={{ x: -280, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -280, opacity: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="fixed left-0 top-0 bottom-0 z-40 w-64 flex flex-col glass-card rounded-none border-r border-white/5"
          >
            {/* Logo */}
            <div className="p-5 border-b border-white/5">
              <Link href="/dashboard" className="flex items-center gap-3">
                <div className="w-9 h-9 flex items-center justify-center">
                  <Image
                    src="/logo.png"
                    alt="BuildWise AI Logo"
                    width={36}
                    height={36}
                    className="object-contain"
                  />
                </div>
                <div>
                  <span className="font-bold text-sm gradient-text">BuildWise AI</span>
                  <p className="text-[10px] text-muted-foreground">Facility Management</p>
                </div>
              </Link>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-5">
              {groups.map((group) => (
                <div key={group}>
                  <p className="text-[10px] font-semibold text-muted-foreground/50 uppercase tracking-widest px-3 mb-2">
                    {groupLabels[group]}
                  </p>
                  <div className="space-y-0.5">
                    {navItems.filter((i) => i.group === group).map((item) => {
                      const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
                      return (
                        <Link key={item.href} href={item.href}>
                          <div className={`sidebar-item ${isActive ? "active" : ""}`}>
                            <item.icon className={`sidebar-icon w-4 h-4 flex-shrink-0 ${isActive ? "text-primary" : "text-muted-foreground"}`} />
                            <span className="flex-1">{item.label}</span>
                            {item.badge && (
                              <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-primary/20 text-primary border border-primary/30">
                                {item.badge}
                              </span>
                            )}
                            {isActive && <ChevronRight className="w-3 h-3 text-primary/50" />}
                          </div>
                        </Link>
                      );
                    })}
                  </div>
                </div>
              ))}
            </nav>

            {/* User Profile */}
            <div className="p-3 border-t border-white/5">
              <div className="glass-card p-3 flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-sm font-bold text-primary">
                  {user?.full_name?.[0] || "U"}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{user?.full_name || "User"}</p>
                  <p className="text-[11px] text-muted-foreground capitalize">{user?.role?.replace("_", " ") || "Member"}</p>
                </div>
                <button onClick={logout} className="text-muted-foreground hover:text-red-400 transition-colors p-1">
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* ── Main Content ──────────────────────────────────────────────────── */}
      <main className={`flex-1 flex flex-col min-h-screen transition-all duration-300 ${sidebarOpen ? "ml-64" : "ml-0"}`}>
        {/* Top navbar */}
        <header className="sticky top-0 z-30 h-14 flex items-center px-5 border-b border-white/5 bg-background/80 backdrop-blur-xl">
          <button
            onClick={toggleSidebar}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-white/5 transition-colors"
          >
            {sidebarOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>

          <div className="flex-1 flex items-center px-4">
            {/* Breadcrumb */}
            <nav className="flex items-center gap-1 text-sm text-muted-foreground">
              <span>BuildWise</span>
              <ChevronRight className="w-3 h-3" />
              <span className="text-foreground capitalize">
                {pathname.split("/").filter(Boolean).pop()?.replace("-", " ") || "Dashboard"}
              </span>
            </nav>
          </div>

          <div className="flex items-center gap-2">
            {/* Emergency indicator */}
            <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-green-500/10 border border-green-500/20">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs text-green-400 font-medium">AI Active</span>
            </div>

            {/* Notifications */}
            <Link href="/dashboard/notifications" className="relative w-8 h-8 rounded-lg flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-white/5 transition-colors">
              <Bell className="w-4 h-4" />
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-red-500 text-[10px] font-bold text-white flex items-center justify-center">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </Link>
          </div>
        </header>

        {/* Page content */}
        <div className="flex-1 p-6 overflow-auto">
          <motion.div
            key={pathname}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
          >
            {children}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
