"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, Users, ArrowLeftRight, AlertTriangle } from "lucide-react";

const links = [
  { href: "/books", label: "Books", icon: BookOpen },
  { href: "/members", label: "Members", icon: Users },
  { href: "/loans", label: "Loans", icon: ArrowLeftRight },
  { href: "/loans/overdue", label: "Overdue", icon: AlertTriangle },
];

export default function Nav() {
  const pathname = usePathname();
  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-4 max-w-6xl flex items-center gap-8 h-14">
        <Link href="/" className="font-bold text-lg text-indigo-600 flex items-center gap-2">
          <BookOpen size={20} />
          Library
        </Link>
        <div className="flex gap-1">
          {links.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  active
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <Icon size={15} />
                {label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
