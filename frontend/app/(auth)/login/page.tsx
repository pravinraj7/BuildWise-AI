"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { Eye, EyeOff, Loader2, LogIn, Sparkles } from "lucide-react";
import Image from "next/image";
import { api, getErrorMessage } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { register, handleSubmit, setValue, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    try {
      const res = await api.post("/auth/login", data);
      setAuth(res.data.access_token, res.data.user);
      toast.success(`Welcome back, ${res.data.user.full_name}! 🏢`);
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(getErrorMessage(err, "Login failed. Please try again."));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-3/4 left-1/2 w-64 h-64 bg-cyan-500/08 rounded-full blur-3xl animate-pulse delay-2000" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="w-full max-w-md px-4"
      >
        <div className="glass-card p-8 space-y-8">
          {/* Logo */}
          <div className="text-center space-y-3">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
              className="inline-flex items-center justify-center mx-auto"
            >
              <Image
                src="/logo.png"
                alt="BuildWise AI Logo"
                width={100}
                height={100}
                className="object-contain drop-shadow-lg"
                priority
              />
            </motion.div>
            <div>
              <h1 className="text-2xl font-bold gradient-text">BuildWise AI</h1>
              <p className="text-muted-foreground text-sm mt-1">
                Autonomous Facility Management Platform
              </p>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground/80">Email Address</label>
              <input
                {...register("email")}
                type="email"
                placeholder="manager@building.com"
                className="bw-input"
                autoComplete="email"
              />
              {errors.email && <p className="text-xs text-red-400">{errors.email.message}</p>}
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground/80">Password</label>
              <div className="relative">
                <input
                  {...register("password")}
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  className="bw-input pr-10"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="text-xs text-red-400">{errors.password.message}</p>}
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 text-muted-foreground cursor-pointer">
                <input type="checkbox" className="rounded" />
                Remember me
              </label>
              <button type="button" className="text-primary hover:text-primary/80 transition-colors">
                Forgot password?
              </button>
            </div>

            <button type="submit" disabled={isLoading} className="btn-primary w-full py-3 text-base">
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Signing in…
                </>
              ) : (
                <>
                  <LogIn className="w-4 h-4" />
                  Sign In
                </>
              )}
            </button>
          </form>

          {/* Demo accounts */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="flex-1 h-px bg-white/10" />
              <span className="text-xs text-muted-foreground px-2 flex items-center gap-1">
                <Sparkles className="w-3 h-3" /> Demo Accounts
              </span>
              <div className="flex-1 h-px bg-white/10" />
            </div>
            <div className="grid grid-cols-2 gap-2">
              {[
                { label: "Manager", email: "manager@buildwise.ai", pass: "Admin@123" },
                { label: "Technician", email: "technician@buildwise.ai", pass: "Admin@123" },
                { label: "Admin", email: "admin@buildwise.ai", pass: "Admin@123" },
                { label: "Resident", email: "resident@buildwise.ai", pass: "Admin@123" },
              ].map((acc) => (
                <button
                  key={acc.label}
                  type="button"
                  className="btn-secondary text-xs py-2"
                  onClick={() => {
                    setValue("email", acc.email, { shouldValidate: true });
                    setValue("password", acc.pass, { shouldValidate: true });
                    onSubmit({ email: acc.email, password: acc.pass });
                  }}
                >
                  👤 {acc.label}
                </button>
              ))}
            </div>
          </div>

          <p className="text-center text-sm text-muted-foreground">
            Don&apos;t have an account?{" "}
            <a href="/register" className="text-primary hover:text-primary/80 font-medium transition-colors">
              Sign up
            </a>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
