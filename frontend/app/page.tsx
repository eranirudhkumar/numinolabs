import Link from "next/link";
import { BookOpen, Users, ArrowLeftRight, AlertTriangle } from "lucide-react";

const cards = [
  {
    href: "/books",
    icon: BookOpen,
    title: "Books",
    desc: "Manage the library catalog — add, update, and track inventory.",
    color: "bg-indigo-50 text-indigo-700",
  },
  {
    href: "/members",
    icon: Users,
    title: "Members",
    desc: "Register and manage library cardholders.",
    color: "bg-emerald-50 text-emerald-700",
  },
  {
    href: "/loans",
    icon: ArrowLeftRight,
    title: "Loans",
    desc: "Record borrowing and returning of books.",
    color: "bg-amber-50 text-amber-700",
  },
  {
    href: "/loans/overdue",
    icon: AlertTriangle,
    title: "Overdue",
    desc: "View all loans past their due date and outstanding fines.",
    color: "bg-rose-50 text-rose-700",
  },
];

export default function Home() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">Neighborhood Library</h1>
      <p className="text-gray-500 mb-8">Staff management portal</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {cards.map(({ href, icon: Icon, title, desc, color }) => (
          <Link
            key={href}
            href={href}
            className="bg-white rounded-xl border border-gray-200 p-6 flex gap-4 hover:shadow-md transition-shadow"
          >
            <div className={`rounded-lg p-3 h-fit ${color}`}>
              <Icon size={22} />
            </div>
            <div>
              <h2 className="font-semibold text-lg">{title}</h2>
              <p className="text-gray-500 text-sm mt-1">{desc}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
