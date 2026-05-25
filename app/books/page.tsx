"use client";
import { useEffect, useState, useCallback } from "react";
import { bookApi } from "@/lib/api";
import type { Book, BookCreate, BookUpdate } from "@/lib/types";
import toast from "react-hot-toast";
import { Plus, Pencil, BookOpen } from "lucide-react";

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Book | null>(null);
  const [authorFilter, setAuthorFilter] = useState("");
  const [genreFilter, setGenreFilter] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await bookApi.list({
        author: authorFilter || undefined,
        genre: genreFilter || undefined,
      });
      setBooks(data.books);
      setTotal(data.total);
    } catch {
      toast.error("Failed to load books");
    } finally {
      setLoading(false);
    }
  }, [authorFilter, genreFilter]);

  useEffect(() => {
    load();
  }, [load]);

  const handleSave = async (form: BookCreate | BookUpdate) => {
    try {
      if (editing) {
        await bookApi.update(editing.id, form as BookUpdate);
        toast.success("Book updated");
      } else {
        await bookApi.create(form as BookCreate);
        toast.success("Book created");
      }
      setShowForm(false);
      setEditing(null);
      load();
    } catch (e: unknown) {
      const msg =
        (e as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "An error occurred";
      toast.error(msg);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <BookOpen size={22} className="text-indigo-600" /> Books
          </h1>
          <p className="text-gray-500 text-sm mt-1">{total} total records</p>
        </div>
        <button
          onClick={() => { setEditing(null); setShowForm(true); }}
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
        >
          <Plus size={16} /> Add Book
        </button>
      </div>

      <div className="flex gap-3 mb-4">
        <input
          placeholder="Filter by author…"
          value={authorFilter}
          onChange={(e) => setAuthorFilter(e.target.value)}
          className="border border-gray-200 rounded-lg px-3 py-2 text-sm w-48 focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
        <input
          placeholder="Filter by genre…"
          value={genreFilter}
          onChange={(e) => setGenreFilter(e.target.value)}
          className="border border-gray-200 rounded-lg px-3 py-2 text-sm w-48 focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
      </div>

      {showForm && (
        <BookForm
          initial={editing}
          onSave={handleSave}
          onCancel={() => { setShowForm(false); setEditing(null); }}
        />
      )}

      {loading ? (
        <p className="text-gray-400 text-sm">Loading…</p>
      ) : books.length === 0 ? (
        <p className="text-gray-400 text-sm">No books found.</p>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-500 text-left">
              <tr>
                {["Title", "Author", "Genre", "Year", "Copies", "Available", "Actions"].map((h) => (
                  <th key={h} className="px-4 py-3 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {books.map((b) => (
                <tr key={b.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{b.title}</td>
                  <td className="px-4 py-3 text-gray-600">{b.author}</td>
                  <td className="px-4 py-3 text-gray-500">{b.genre ?? "—"}</td>
                  <td className="px-4 py-3 text-gray-500">{b.published_year ?? "—"}</td>
                  <td className="px-4 py-3">{b.total_copies}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${b.available_copies > 0 ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                      {b.available_copies}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => { setEditing(b); setShowForm(true); }}
                      className="text-indigo-600 hover:text-indigo-800"
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

function BookForm({
  initial,
  onSave,
  onCancel,
}: {
  initial: Book | null;
  onSave: (d: BookCreate | BookUpdate) => void;
  onCancel: () => void;
}) {
  const [form, setForm] = useState({
    isbn: initial?.isbn ?? "",
    title: initial?.title ?? "",
    author: initial?.author ?? "",
    genre: initial?.genre ?? "",
    published_year: initial?.published_year?.toString() ?? "",
    total_copies: initial?.total_copies?.toString() ?? "1",
  });

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      isbn: form.isbn || undefined,
      title: form.title,
      author: form.author,
      genre: form.genre || undefined,
      published_year: form.published_year ? parseInt(form.published_year) : undefined,
      total_copies: parseInt(form.total_copies) || 1,
    });
  };

  return (
    <form
      onSubmit={submit}
      className="bg-white border border-indigo-200 rounded-xl p-5 mb-6 shadow-sm"
    >
      <h2 className="font-semibold mb-4">{initial ? "Edit Book" : "New Book"}</h2>
      <div className="grid grid-cols-2 gap-3">
        {[
          { k: "title", label: "Title *", required: true },
          { k: "author", label: "Author *", required: true },
          { k: "isbn", label: "ISBN", required: false },
          { k: "genre", label: "Genre", required: false },
          { k: "published_year", label: "Year", required: false },
          { k: "total_copies", label: "Total Copies *", required: true },
        ].map(({ k, label, required }) => (
          <div key={k}>
            <label className="text-xs text-gray-500 block mb-1">{label}</label>
            <input
              value={form[k as keyof typeof form]}
              onChange={(e) => set(k, e.target.value)}
              required={required}
              className="border border-gray-200 rounded-lg px-3 py-2 w-full text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
          </div>
        ))}
      </div>
      <div className="flex gap-2 mt-4">
        <button
          type="submit"
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700"
        >
          {initial ? "Update" : "Create"}
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
