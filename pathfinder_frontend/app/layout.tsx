import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PATHFINDER - Runtime Policy & Cryptographic Audit",
  description: "Next.js Console for PATHFINDER Policy Enforcement",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased bg-slate-950 text-slate-100" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
