import type { Metadata } from "next";
import { Montserrat } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/ThemeProvider";
import { AnimationProvider } from "@/components/AnimationProvider";
import { ScrollProgress } from "@/components/ScrollProgress";
import { Toaster } from "sonner";

const montserrat = Montserrat({
  variable: "--font-montserrat",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "Ahead Of Everyone | Daily Tech Digest",
  description: "Five minutes. Then you are ahead of everyone.",
  icons: {
    icon: "/logo.jpg",
    shortcut: "/logo.jpg",
    apple: "/logo.jpg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className={`${montserrat.variable} antialiased`} data-scroll-behavior="smooth">
      <body className="font-sans min-h-screen flex flex-col bg-background text-foreground transition-colors duration-300">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <AnimationProvider>
            <ScrollProgress />
            <div className="flex-1 flex flex-col">
              {children}
            </div>
            <Toaster position="bottom-right" richColors theme="system" />
          </AnimationProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
