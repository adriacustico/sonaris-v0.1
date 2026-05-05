import Link from "next/link";

const links: Array<{ href: string; label: string }> = [
  { href: "/", label: "Inicio" },
  { href: "/projects", label: "Proyectos" },
  { href: "/dashboard", label: "Dashboard" }
];

export function Navigation(): JSX.Element {
  return (
    <nav className="flex items-center gap-4 text-sm text-slate-700">
      {links.map((link) => (
        <Link key={link.href} href={link.href} className="hover:text-signal">
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
