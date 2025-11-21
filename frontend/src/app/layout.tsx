import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner"; // <-- 1. Importa el Toaster de 'sonner'

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SBC FIUNJU",
  description: "Sistema Basado en Conocimiento - FI UNJu",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className={inter.className}>
        {children}
        <Toaster richColors /> {/* <-- 2. Añade el Toaster aquí (richColors es opcional pero se ve bien) */}
      </body>
    </html>
  );
}