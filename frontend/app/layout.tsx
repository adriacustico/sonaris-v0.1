import type { Metadata } from "next";
import "../styles/globals.css";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "Sonaris",
  description: "Plataforma SaaS para calculos acusticos."
};

type RootLayoutProps = {
  children: React.ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps): JSX.Element {
  return (
    <html lang="es">
      <body>
        <Header />
        <main>{children}</main>
      </body>
    </html>
  );
}
