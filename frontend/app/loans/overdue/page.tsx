"use client";
import { useEffect, useState, useCallback } from "react";
import { loanApi } from "@/lib/api";
import type { Loan } from "@/lib/types";
import toast from "react-hot-toast";
import { AlertTriangle, RotateCcw } from "lucide-react";

export default function OverdueLoansPage() {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await loanApi.overdue();
      setLoans(data.loans);
    } catch {
      toast.error("Failed to load overdue loans");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleReturn = async (loanId: string, bookTitle: string) => {
    if (!window.confirm(`Return "${bookTitle}"? This will finalize the overdue fine.`)) return;
    try {
      const returned = await loanApi.return(loanId);
      toast.success(
        returned.fine_amount > 0
          ? `Book returned. Fine: $${returned.fine_amount.toFixed(2)}`
          : "Book returned successfully"
      );
      load();
    } catch (e: unknown) {
      const msg =
        (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Failed to return book";
      toast.error(msg);
    }
  };

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <AlertTriangle size={22} className="text-rose-600" />
        <div>
          <h1 className="text-2xl font-bold">Overdue Loans</h1>
          <p className="text-gray-500 text-sm mt-0.5">
            {loans.length} overdue {loans.length === 1 ? "loan" : "loans"}
          </p>
        </div>
      </div>

      {loading ? (
        <p className="text-gray-400 text-sm">Loading…</p>
      ) : loans.length === 0 ? (
        <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center text-green-700">
          No overdue loans — all books are on time!
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-rose-200 bg-white">
          <table className="w-full text-sm">
            <thead className="bg-rose-50 text-rose-700 text-left">
              <tr>
                {["Book", "Member", "Email", "Borrowed", "Due Date", "Days Late", "Est. Fine", "Actions"].map(
                  (h) => <th key={h} className="px-4 py-3 font-medium">{h}</th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loans.map((loan) => {
                const daysLate = Math.max(
                  1,
                  Math.floor(
                    (Date.now() - new Date(loan.due_date).getTime()) /
                      (1000 * 60 * 60 * 24)
                  )
                );
                const estFine = (daysLate * 0.5).toFixed(2);
                return (
                  <tr key={loan.id} className="hover:bg-rose-50">
                    <td className="px-4 py-3 font-medium max-w-[150px] truncate">
                      {loan.book.title}
                    </td>
                    <td className="px-4 py-3">
                      {loan.member.first_name} {loan.member.last_name}
                    </td>
                    <td className="px-4 py-3 text-gray-500">{loan.member.email}</td>
                    <td className="px-4 py-3 text-gray-500">
                      {new Date(loan.borrowed_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-red-600 font-medium">
                      {new Date(loan.due_date).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-red-700 font-semibold">
                      {daysLate}d
                    </td>
                    <td className="px-4 py-3 text-red-700 font-semibold">
                      ${estFine}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleReturn(loan.id, loan.book.title)}
                        className="flex items-center gap-1 text-xs text-amber-600 hover:text-amber-800"
                      >
                        <RotateCcw size={14} /> Return
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
