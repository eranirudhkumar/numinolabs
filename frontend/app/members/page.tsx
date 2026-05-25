"use client";
import { useEffect, useState, useCallback } from "react";
import { memberApi } from "@/lib/api";
import type { Member, MemberCreate, MemberUpdate } from "@/lib/types";
import toast from "react-hot-toast";
import { Plus, Pencil, Users } from "lucide-react";

const STATUS_COLORS = {
  active: "bg-green-100 text-green-700",
  suspended: "bg-yellow-100 text-yellow-700",
  expired: "bg-gray-100 text-gray-600",
};

export default function MembersPage() {
  const [members, setMembers] = useState<Member[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Member | null>(null);
  const [search, setSearch] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await memberApi.list({ search: search || undefined });
      setMembers(data.members);
      setTotal(data.total);
    } catch {
      toast.error("Failed to load members");
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => { load(); }, [load]);

  const handleSave = async (form: MemberCreate | MemberUpdate) => {
    try {
      if (editing) {
        await memberApi.update(editing.id, form as MemberUpdate);
        toast.success("Member updated");
      } else {
        await memberApi.create(form as MemberCreate);
        toast.success("Member registered");
      }
      setShowForm(false);
      setEditing(null);
      load();
    } catch (e: unknown) {
      const msg =
        (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "An error occurred";
      toast.error(msg);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Users size={22} className="text-emerald-600" /> Members
          </h1>
          <p className="text-gray-500 text-sm mt-1">{total} total records</p>
        </div>
        <button
          onClick={() => { setEditing(null); setShowForm(true); }}
          className="flex items-center gap-2 bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-emerald-700 transition-colors"
        >
          <Plus size={16} /> Register Member
        </button>
      </div>

      {showForm && (
        <MemberForm
          initial={editing}
          onSave={handleSave}
          onCancel={() => { setShowForm(false); setEditing(null); }}
        />
      )}

      <div className="mb-4">
        <input
          placeholder="Search by name or email…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-200 rounded-lg px-3 py-2 text-sm w-72 focus:outline-none focus:ring-2 focus:ring-emerald-300"
        />
      </div>

      {loading ? (
        <p className="text-gray-400 text-sm">Loading…</p>
      ) : members.length === 0 ? (
        <p className="text-gray-400 text-sm">No members found.</p>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-500 text-left">
              <tr>
                {["Name", "Email", "Phone", "Status", "Since", "Actions"].map((h) => (
                  <th key={h} className="px-4 py-3 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {members.map((m) => (
                <tr key={m.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{m.first_name} {m.last_name}</td>
                  <td className="px-4 py-3 text-gray-600">{m.email}</td>
                  <td className="px-4 py-3 text-gray-500">{m.phone ?? "—"}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${STATUS_COLORS[m.membership_status]}`}>
                      {m.membership_status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(m.membership_date + "T12:00:00").toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => { setEditing(m); setShowForm(true); }}
                      className="text-emerald-600 hover:text-emerald-800"
                    >
                      <Pencil size={15} />
                    </button>
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

function MemberForm({
  initial,
  onSave,
  onCancel,
}: {
  initial: Member | null;
  onSave: (d: MemberCreate | MemberUpdate) => void;
  onCancel: () => void;
}) {
  const [form, setForm] = useState({
    first_name: initial?.first_name ?? "",
    last_name: initial?.last_name ?? "",
    email: initial?.email ?? "",
    phone: initial?.phone ?? "",
    address: initial?.address ?? "",
    membership_status: initial?.membership_status ?? "active",
  });

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: MemberCreate | MemberUpdate = {
      first_name: form.first_name,
      last_name: form.last_name,
      email: form.email,
      phone: form.phone || undefined,
      address: form.address || undefined,
    };
    if (initial) {
      (payload as MemberUpdate).membership_status = form.membership_status as Member["membership_status"];
    }
    onSave(payload);
  };

  return (
    <form
      onSubmit={submit}
      className="bg-white border border-emerald-200 rounded-xl p-5 mb-6 shadow-sm"
    >
      <h2 className="font-semibold mb-4">{initial ? "Edit Member" : "Register Member"}</h2>
      <div className="grid grid-cols-2 gap-3">
        {[
          { k: "first_name", label: "First Name *", required: true },
          { k: "last_name", label: "Last Name *", required: true },
          { k: "email", label: "Email *", required: true, type: "email" },
          { k: "phone", label: "Phone", required: false },
          { k: "address", label: "Address", required: false },
        ].map(({ k, label, required, type }) => (
          <div key={k}>
            <label className="text-xs text-gray-500 block mb-1">{label}</label>
            <input
              type={type ?? "text"}
              value={form[k as keyof typeof form]}
              onChange={(e) => set(k, e.target.value)}
              required={required}
              className="border border-gray-200 rounded-lg px-3 py-2 w-full text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300"
            />
          </div>
        ))}
        {initial && (
          <div>
            <label className="text-xs text-gray-500 block mb-1">Status</label>
            <select
              value={form.membership_status}
              onChange={(e) => set("membership_status", e.target.value)}
              className="border border-gray-200 rounded-lg px-3 py-2 w-full text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300"
            >
              <option value="active">Active</option>
              <option value="suspended">Suspended</option>
              <option value="expired">Expired</option>
            </select>
          </div>
        )}
      </div>
      <div className="flex gap-2 mt-4">
        <button
          type="submit"
          className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-emerald-700"
        >
          {initial ? "Update" : "Register"}
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
