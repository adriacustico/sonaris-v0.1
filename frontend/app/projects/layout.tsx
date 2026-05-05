type ProjectsLayoutProps = {
  children: React.ReactNode;
};

export default function ProjectsLayout({ children }: ProjectsLayoutProps): JSX.Element {
  return <section className="mx-auto max-w-6xl px-6 py-8">{children}</section>;
}
