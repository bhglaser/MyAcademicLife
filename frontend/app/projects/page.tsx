"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { projects, Project } from "@/lib/api";

const STATUS_OPTIONS = ["active", "on_hold", "completed", "archived"];

export default function ProjectsPage() {
  const [items, setItems] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState({ title: "", description: "", status: "active", collaborators: "" });

  const load = () => {
    projects.list().then(setItems).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (editingId) {
      await projects.update(editingId, form);
    } else {
      await projects.create(form);
    }
    resetForm();
    load();
  };

  const resetForm = () => {
    setForm({ title: "", description: "", status: "active", collaborators: "" });
    setShowForm(false);
    setEditingId(null);
  };

  const startEdit = (p: Project) => {
    setForm({
      title: p.title,
      description: p.description || "",
      status: p.status,
      collaborators: p.collaborators || "",
    });
    setEditingId(p.id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this project?")) return;
    await projects.delete(id);
    load();
  };

  if (loading) return <p className="text-slate-500">Loading...</p>;

  return (
    <>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Research Projects</h1>
        <button onClick={() => { resetForm(); setShowForm(true); }} className="bg-blue-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-blue-700">
          + New Project
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Title</label>
            <input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={3} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s.replace("_", " ")}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Collaborators</label>
              <input value={form.collaborators} onChange={(e) => setForm({ ...form, collaborators: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="comma separated" />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" className="bg-blue-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-blue-700">
              {editingId ? "Update" : "Create"}
            </button>
            <button type="button" onClick={resetForm} className="text-sm px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-50">Cancel</button>
          </div>
        </form>
      )}

      {items.length === 0 ? (
        <p className="text-slate-400">No projects yet. Create one to get started.</p>
      ) : (
        <div className="space-y-3">
          {items.map((p) => (
            <div key={p.id} className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
              <div className="flex items-start justify-between">
                <div>
                  <Link href={`/projects/${p.id}`} className="font-semibold hover:text-blue-600">{p.title}</Link>
                  {p.description && <p className="text-sm text-slate-500 mt-1">{p.description}</p>}
                  {p.collaborators && <p className="text-xs text-slate-400 mt-2">Collaborators: {p.collaborators}</p>}
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    p.status === "active" ? "bg-green-50 text-green-700" :
                    p.status === "completed" ? "bg-blue-50 text-blue-700" :
                    "bg-slate-100 text-slate-600"
                  }`}>
                    {p.status.replace("_", " ")}
                  </span>
                  <button onClick={() => startEdit(p)} className="text-xs text-slate-500 hover:text-slate-700">Edit</button>
                  <button onClick={() => handleDelete(p.id)} className="text-xs text-red-500 hover:text-red-700">Delete</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
