import type { Metadata } from "next";
import { Footer } from "@/components/layout/Footer";
import { GlobalAiWidget } from "@/components/layout/GlobalAiWidget";
import { Header } from "@/components/layout/Header";
import "@/styles/globals.scss";

export const metadata: Metadata = {
  title: "CareNow",
  description: "Doctor appointment booking foundation",
};

type RootLayoutProps = {
  children: React.ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white text-slate-900 antialiased">
        <div className="flex min-h-screen flex-col">
          <Header />
          <main className="flex-1">
            <div className="mx-auto w-full max-w-[1600px] px-4 py-0 sm:px-6 lg:px-8 xl:px-10">
              {children}
            </div>
          </main>
          <Footer />
          <GlobalAiWidget />
        </div>
      </body>
    </html>
  );
}
