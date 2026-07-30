"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import Link from "next/link";
import toast from "react-hot-toast";
import {
  Eye,
  EyeOff,
  Loader2,
  UserPlus,
  User,
  Mail,
  Lock,
  Phone,
  Briefcase,
} from "lucide-react";
import Image from "next/image";
import { authApi, getErrorMessage } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

const registerSchema = z
  .object({
    full_name: z.string().min(2, "Full name must be at least 2 characters"),
    username: z
      .string()
      .min(3, "Username must be at least 3 characters")
      .regex(/^[a-zA-Z0-9_]+$/, "Only letters, numbers, and underscores"),
    email: z.string().email("Invalid email address"),
    phone: z.string().optional(),
    role: z.enum(["manager", "technician", "resident", "admin"]),
    department: z.string().optional(),
    password: z.string().min(6, "Password must be at least 6 characters"),
    confirmPassword: z.string(),
  })
  .refine((d) => d.password === d.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

type RegisterForm = z.infer<typeof registerSchema>;

const roles = [
  { value: "resident", label: "Resident / Tenant" },
  { value: "technician", label: "Technician" },
  { value: "manager", label: "Facility Manager" },
  { value: "admin", label: "Administrator" },
];

export default function RegisterPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: { role: "resident" },
  });

  const onSubmit = async (data: RegisterForm) => {
    setIsLoading(true);
    try {
      const { confirmPassword, ...payload } = data;
      const res = await authApi.register(payload);
      setAuth(res.data.access_token, res.data.user);
      toast.success(`Welcome to BuildWise AI, ${res.data.user.full_name}! 🏢`);
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(getErrorMessage(err, "Registration failed. Please try again."));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden py-10">
      {/* Animated background blobs */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-3/4 left-1/2 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-2000" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="w-full max-w-lg px-4"
      >
        <div className="glass-card p-8 space-y-7">
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
                width={90}
                height={90}
                className="object-contain drop-shadow-lg"
                priority
              />
            </motion.div>
            <div>
              <h1 className="text-2xl font-bold gradient-text">BuildWise AI</h1>
              <p className="text-muted-foreground text-sm mt-1">
                Create your account to get started
              </p>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Full Name + Username */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-foreground/80 flex items-center gap-1.5">
                  <User className="w-3.5 h-3.5" /> Full Name
                </label>
                <input
                  {...register("full_name")}
                  type="text"
                  placeholder="John Smith"
                  className="bw-input"
                  autoComplete="name"
                />
                {errors.full_name && (
                  <p className="text-xs text-red-400">{errors.full_name.message}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-foreground/80 flex items-center gap-1.5">
                  <User className="w-3.5 h-3.5" /> Username
                </label>
                <input
                  {...register("username")}
                  type="text"
                  placeholder="john_smith"
                  className="bw-input"
                  autoComplete="username"
                />
                {errors.username && (
                  <p className="text-xs text-red-400">{errors.username.message}</p>
                )}
              </div>
            </div>

            {/* Email */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground/80 flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5" /> Email Address
              </label>
              <input
                {...register("email")}
                type="email"
                placeholder="john@building.com"
                className="bw-input"
                autoComplete="email"
              />
              {errors.email && (
                <p className="text-xs text-red-400">{errors.email.message}</p>
              )}
            </div>

            {/* Phone + Role */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-foreground/80 flex items-center gap-1.5">
                  <Phone className="w-3.5 h-3.5" /> Phone{" "}
                  <span className="text-muted-foreground text-xs">(optional)</span>
                </label>
                <input
                  {...register("phone")}
                  type="tel"
                  placeholder="+1 555 000 0000"
                  className="bw-input"
                  autoComplete="tel"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-foreground/80 flex items-center gap-1.5">
                  <Briefcase className="w-3.5 h-3.5" /> Role
                </label>
                <select {...register("role")} className="bw-input">
                  {roles.map((r) => (
                    <option key={r.value} value={r.value} className="bg-[#0d1117]">
                      {r.label}
                    </option>
                  ))}
                </select>
                {errors.role && (
                  <p className="text-xs text-red-400">{errors.role.message}</p>
                )}
              </div>
            </div>

            {/* Department */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground/80 flex items-center gap-1.5">
                <Briefcase className="w-3.5 h-3.5" /> Department{" "}
                <span className="text-muted-foreground text-xs">(optional)</span>
              </label>
              <input
                {...register("department")}
                type="text"
                placeholder="e.g. Engineering, Operations"
                className="bw-input"
              />
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground/80 flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5" /> Password
              </label>
              <div className="relative">
                <input
                  {...register("password")}
                  type={showPassword ? "text" : "password"}
                  placeholder="At least 6 characters"
                  className="bw-input pr-10"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="text-xs text-red-400">{errors.password.message}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-foreground/80 flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5" /> Confirm Password
              </label>
              <div className="relative">
                <input
                  {...register("confirmPassword")}
                  type={showConfirm ? "text" : "password"}
                  placeholder="Repeat your password"
                  className="bw-input pr-10"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirm(!showConfirm)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showConfirm ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="text-xs text-red-400">
                  {errors.confirmPassword.message}
                </p>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full py-3 text-base mt-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Creating account…
                </>
              ) : (
                <>
                  <UserPlus className="w-4 h-4" />
                  Create Account
                </>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link
              href="/login"
              className="text-primary hover:text-primary/80 font-medium transition-colors"
            >
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
