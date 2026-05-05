type DashboardLayoutProps = {
  children: React.ReactNode;
};

export default function DashboardLayout({ children }: DashboardLayoutProps): JSX.Element {
  return <section className="mx-auto max-w-6xl px-6 py-8">{children}</section>;
}
