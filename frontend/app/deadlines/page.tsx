"use client";

import { useEffect, useState } from "react";
import { deadlines, Deadline } from "@/lib/api";

const KIND_OPTIONS = ["conference", "journal", "grant", "coursework", "administrative", "other"];
const STATUS_OPTIONS = ["upcoming", "submitted", "missed", "cancelled"];

export default function DeadlinesPage() {
  const [items, setItems] = useState<Deadline[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState({ title: "", kind: "conference", due_date: "", description: "", status: "upcoming" });

  const load = () => {
    deadlines.list().then(setItems).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (editingId) {
      await deadlines.update(editingId, form);
    } else {
      await deadlines.create(form);
    }
    resetForm();
    load();
  };

  const resetForm = () => {
    setForm({ title: "", kind: "conference", due_date: "", description: "", status: "upcoming" });
    setShowForm(false);
    setEditingId(null);
  };

  const startEdit = (d: Deadline) => {
    setForm({
      title: d.title,
      kind: d.kind,
      due_date: d.due_date.slice(0, 16),
      description: d.description || "",
      status: d.status,
    });
    setEditingId(d.id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this deadline?")) return;
    await deadlines.delete(id);
    load();
  };

  const daysUntil = (dateStr: string) => {
    const days = Math.ceil((new Date(dateStr).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    if (days < 0) return "overdue";
    if (days === 0) return "today";
    if (days === 1) return "tomorrow";
    return `${days} days`;
  };

  if (loading) return <p className="text-slate-500">Loading...</p>;

  return (
    <>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Deadlines</h1>
        <button onClick={() => { resetForm(); setShowForm(true); }} className="bg-red-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-red-700">
          + New Deadline
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Title</label>
            <input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Type</label>
              <select value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                {KIND_OPTIONS.map((k) => <option key={k} value={k}>{k}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Due Date</label>
              <input required type="datetime-local" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div className="flex gap-2">
            <button type="submit" className="bg-red-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-red-700">
              {editingId ? "Update" : "Create"}
            </button>
            <button type="button" onClick={resetForm} className="text-sm px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-50">Cancel</button>
          </div>
        </form>
      )}

      {items.length === 0 ? (
        <p className="text-slate-400">No deadlines yet.</p>
      ) : (
        <div className="space-y-3">
          {items.map((d) => (
            <div key={d.id} className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 flex items-center justify-between">
              <div>
                <h3 className="font-semibold">{d.title}</h3>
                <p className="text-sm text-slate-500 mt-0.5">
                  {d.kind} &middot; {new Date(d.due_date).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", year: "numeric" })}
                </p>
                {d.description && <p className="text-xs text-slate-400 mt-1">{d.description}</p>}
              </div>
              <div className="flex items-center gap-3">
                <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                  d.status === "upcoming" ? "bg-amber-50 text-amber-700" :
                  d.status === "submitted" ? "bg-green-50 text-green-700" :
                  d.status === "missed" ? "bg-red-50 text-red-700" :
                  "bg-slate-100 text-slate-600"
                }`}>
                  {d.status === "upcoming" ? daysUntil(d.due_date) : d.status}
                </span>
                <button onClick={() => startEdit(d)} className="text-xs text-slate-500 hover:text-slate-700">Edit</button>
                <button onClick={() => handleDelete(d.id)} className="text-xs text-red-500 hover:text-red-700">Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
