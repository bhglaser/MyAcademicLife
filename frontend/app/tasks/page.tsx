"use client";

import { useEffect, useState } from "react";
import { tasks, Task } from "@/lib/api";

const PRIORITY_OPTIONS = ["low", "medium", "high", "urgent"];
const STATUS_OPTIONS = ["todo", "in_progress", "blocked", "done"];

const PRIORITY_COLORS: Record<string, string> = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-blue-50 text-blue-700",
  high: "bg-amber-50 text-amber-700",
  urgent: "bg-red-50 text-red-700",
};

export default function TasksPage() {
  const [items, setItems] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [filter, setFilter] = useState<string>("");
  const [form, setForm] = useState({ title: "", description: "", priority: "medium", status: "todo", due_date: "" });

  const load = () => {
    tasks.list(filter ? { status: filter } : undefined).then(setItems).finally(() => setLoading(false));
  };

  useEffect(load, [filter]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = { ...form, due_date: form.due_date || null };
    if (editingId) {
      await tasks.update(editingId, payload);
    } else {
      await tasks.create(payload);
    }
    resetForm();
    load();
  };

  const resetForm = () => {
    setForm({ title: "", description: "", priority: "medium", status: "todo", due_date: "" });
    setShowForm(false);
    setEditingId(null);
  };

  const startEdit = (t: Task) => {
    setForm({
      title: t.title,
      description: t.description || "",
      priority: t.priority,
      status: t.status,
      due_date: t.due_date || "",
    });
    setEditingId(t.id);
    setShowForm(true);
  };

  const quickComplete = async (t: Task) => {
    await tasks.update(t.id, { status: "done" });
    load();
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this task?")) return;
    await tasks.delete(id);
    load();
  };

  if (loading) return <p className="text-slate-500">Loading...</p>;

  return (
    <>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Tasks</h1>
        <button onClick={() => { resetForm(); setShowForm(true); }} className="bg-amber-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-amber-700">
          + New Task
        </button>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 mb-5">
        {["", ...STATUS_OPTIONS].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`text-xs px-3 py-1.5 rounded-full border ${
              filter === s ? "bg-slate-900 text-white border-slate-900" : "border-slate-300 text-slate-600 hover:bg-slate-100"
            }`}
          >
            {s || "All"}
          </button>
        ))}
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Title</label>
            <input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Priority</label>
              <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                {PRIORITY_OPTIONS.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s.replace("_", " ")}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Due Date</label>
              <input type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" className="bg-amber-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-amber-700">
              {editingId ? "Update" : "Create"}
            </button>
            <button type="button" onClick={resetForm} className="text-sm px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-50">Cancel</button>
          </div>
        </form>
      )}

      {items.length === 0 ? (
        <p className="text-slate-400">{filter ? `No ${filter.replace("_", " ")} tasks.` : "No tasks yet."}</p>
      ) : (
        <div className="space-y-2">
          {items.map((t) => (
            <div key={t.id} className={`bg-white rounded-xl shadow-sm border border-slate-200 p-4 flex items-center gap-4 ${t.status === "done" ? "opacity-60" : ""}`}>
              <button
                onClick={() => t.status !== "done" && quickComplete(t)}
                className={`w-5 h-5 rounded border-2 flex-shrink-0 flex items-center justify-center ${
                  t.status === "done" ? "bg-green-500 border-green-500 text-white" : "border-slate-300 hover:border-green-400"
                }`}
              >
                {t.status === "done" && (
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </button>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${t.status === "done" ? "line-through" : ""}`}>{t.title}</p>
                {t.description && <p className="text-xs text-slate-400 truncate">{t.description}</p>}
              </div>
              <span className={`text-xs px-2 py-1 rounded-full ${PRIORITY_COLORS[t.priority] || ""}`}>{t.priority}</span>
              {t.due_date && <span className="text-xs text-slate-500">{new Date(t.due_date).toLocaleDateString()}</span>}
              <button onClick={() => startEdit(t)} className="text-xs text-slate-500 hover:text-slate-700">Edit</button>
              <button onClick={() => handleDelete(t.id)} className="text-xs text-red-500 hover:text-red-700">Delete</button>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
