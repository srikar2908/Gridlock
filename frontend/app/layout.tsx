import type { Metadata } from "next";
import "leaflet/dist/leaflet.css";
import "./globals.css";
import { QueryProvider } from "@/components/providers/query-provider";

export const metadata: Metadata = {
  title: "SENTINEL Traffic Command Center",
  description: "Bengaluru AI traffic operations command center",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
