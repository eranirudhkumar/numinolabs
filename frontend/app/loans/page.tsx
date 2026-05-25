"use client";
import { useEffect, useState, useCallback } from "react";
import { bookApi, loanApi, memberApi } from "@/lib/api";
import type { Book, Loan, Member } from "@/lib/types";
import toast from "react-hot-toast";
import { ArrowLeftRight, Plus, RotateCcw } from "lucide-react";

const STATUS_COLORS = {
  active: "bg-blue-100 text-blue-700",
  returned: "bg-green-100 text-green-700",
  overdue: "bg-red-100 text-red-700",
};

export default function LoansPage() {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await loanApi.list();
      setLoans(data.loans);
      setTotal(data.total);
    } catch {
      toast.error("Failed to load loans");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleReturn = async (loanId: string, bookTitle: string) => {
    if (!window.confirm(`Return "${bookTitle}"? This cannot be undone.`)) return;
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
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <ArrowLeftRight size={22} className="text-amber-600" /> Loans
          </h1>
          <p className="text-gray-500 text-sm mt-1">{total} total records</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-amber-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-amber-700 transition-colors"
        >
          <Plus size={16} /> Borrow Book
        </button>
      </div>

      {showForm && (
        <BorrowForm
          onSave={() => { setShowForm(false); load(); }}
          onCancel={() => setShowForm(false)}
        />
      )}

      {loading ? (
        <p className="text-gray-400 text-sm">Loading…</p>
      ) : loans.length === 0 ? (
        <p className="text-gray-400 text-sm">No loans found.</p>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-500 text-left">
              <tr>
                {["Book", "Member", "Borrowed", "Due", "Status", "Fine", "Actions"].map((h) => (
                  <th key={h} className="px-4 py-3 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loans.map((loan) => (
                <tr key={loan.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium max-w-[180px] truncate">{loan.book.title}</td>
                  <td className="px-4 py-3 text-gray-600">
                    {loan.member.first_name} {loan.member.last_name}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(loan.borrowed_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(loan.due_date).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${STATUS_COLORS[loan.status]}`}>
                      {loan.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {loan.fine_amount > 0 ? (
                      <span className="text-red-600 font-medium">${loan.fine_amount.toFixed(2)}</span>
                    ) : "—"}
                  </td>
                  <td className="px-4 py-3">
                    {loan.status !== "returned" && (
                      <button
                        onClick={() => handleReturn(loan.id, loan.book.title)}
                        title="Return book"
                        className="text-amber-600 hover:text-amber-800 flex items-center gap-1 text-xs"
                      >
                        <RotateCcw size={14} /> Return
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function BorrowForm({
  onSave,
  onCancel,
}: {
  onSave: () => void;
  onCancel: () => void;
}) {
  const [books, setBooks] = useState<Book[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [bookId, setBookId] = useState("");
  const [memberId, setMemberId] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    bookApi.list({ page_size: 100 })
      .then((d) => setBooks(d.books))
      .catch(() => toast.error("Failed to load books"));
    memberApi.list({ page_size: 100 })
      .then((d) => setMembers(d.members))
      .catch(() => toast.error("Failed to load members"));
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await loanApi.borrow({ book_id: bookId, member_id: memberId });
      toast.success("Book borrowed successfully");
      onSave();
    } catch (e: unknown) {
      const msg =
        (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Failed to borrow book";
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const availableBooks = books.filter((b) => b.available_copies > 0);
  const activeMembers = members.filter((m) => m.membership_status === "active");

  return (
    <form
      onSubmit={submit}
      className="bg-white border border-amber-200 rounded-xl p-5 mb-6 shadow-sm"
    >
      <h2 className="font-semibold mb-4">Borrow a Book</h2>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-gray-500 block mb-1">Book *</label>
          <select
            required
            value={bookId}
            onChange={(e) => setBookId(e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-2 w-full text-sm focus:outline-none focus:ring-2 focus:ring-amber-300"
          >
            <option value="">— select —</option>
            {availableBooks.map((b) => (
              <option key={b.id} value={b.id}>
                {b.title} ({b.available_copies} available)
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Member *</label>
          <select
            required
            value={memberId}
            onChange={(e) => setMemberId(e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-2 w-full text-sm focus:outline-none focus:ring-2 focus:ring-amber-300"
          >
            <option value="">— select —</option>
            {activeMembers.map((m) => (
              <option key={m.id} value={m.id}>
                {m.first_name} {m.last_name} ({m.email})
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="flex gap-2 mt-4">
        <button
          type="submit"
          disabled={submitting}
          className="bg-amber-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-amber-700 disabled:opacity-60"
        >
          {submitting ? "Processing…" : "Borrow"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="border border-gray-200 px-4 py-2 rounded-lg text-sm hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
