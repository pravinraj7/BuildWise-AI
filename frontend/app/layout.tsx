import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: {
    default: "BuildWise AI — Autonomous Facility Management Platform",
    template: "%s | BuildWise AI",
  },
  description:
    "AI-powered multi-agent building maintenance and facility management platform. Autonomous complaint handling, predictive maintenance, and intelligent technician dispatch.",
  keywords: ["facility management", "building maintenance", "AI agents", "predictive maintenance"],
  authors: [{ name: "BuildWise AI" }],
  creator: "BuildWise AI",
  openGraph: {
    type: "website",
    locale: "en_US",
    title: "BuildWise AI — Autonomous Facility Management",
    description: "Multi-agent AI platform for intelligent building maintenance",
    siteName: "BuildWise AI",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "hsl(222 47% 8%)",
              color: "hsl(210 40% 98%)",
              border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: "12px",
            },
          }}
        />
      </body>
    </html>
  );
}
