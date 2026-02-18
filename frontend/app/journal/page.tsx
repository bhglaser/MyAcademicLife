"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { journal, JournalEntry, projects as projectsApi, Project } from "@/lib/api";

const MOOD_OPTIONS = ["great", "good", "okay", "stressed", "tired", "focused", "anxious"];

export default function JournalPage() {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", body: "", mood: "", tags: "", project_id: "" });
  const [projectsList, setProjectsList] = useState<Project[]>([]);

  const load = () => {
    journal.list().then(setEntries).finally(() => setLoading(false));
  };

  useEffect(() => {
    projectsApi.list().then(setProjectsList);
  }, []);

  useEffect(load, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await journal.create({
      ...form,
      mood: form.mood || null,
      tags: form.tags || null,
      title: form.title || null,
      project_id: form.project_id ? Number(form.project_id) : null,
    });
    setForm({ title: "", body: "", mood: "", tags: "", project_id: "" });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this entry?")) return;
    await journal.delete(id);
    load();
  };

  if (loading) return <p className="text-slate-500">Loading...</p>;

  return (
    <>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Journal</h1>
        <button onClick={() => setShowForm(true)} className="bg-violet-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-violet-700">
          + New Entry
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Title (optional)</label>
            <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="How was your day?" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">What&apos;s on your mind?</label>
            <textarea required value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} rows={5} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Mood</label>
              <select value={form.mood} onChange={(e) => setForm({ ...form, mood: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                <option value="">-- select --</option>
                {MOOD_OPTIONS.map((m) => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Project (optional)</label>
              <select value={form.project_id} onChange={(e) => setForm({ ...form, project_id: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                <option value="">-- none --</option>
                {projectsList.map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Tags</label>
              <input value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="comma separated" />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" className="bg-violet-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-violet-700">Save</button>
            <button type="button" onClick={() => setShowForm(false)} className="text-sm px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-50">Cancel</button>
          </div>
        </form>
      )}

      {entries.length === 0 ? (
        <p className="text-slate-400">No journal entries yet. Start reflecting!</p>
      ) : (
        <div className="space-y-4">
          {entries.map((entry) => (
            <article key={entry.id} className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="text-xs text-slate-400">{new Date(entry.entry_date).toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" })}</p>
                  {entry.title && <h3 className="font-semibold mt-0.5">{entry.title}</h3>}
                </div>
                <div className="flex items-center gap-2">
                  {entry.mood && (
                    <span className="text-xs bg-violet-50 text-violet-700 px-2 py-1 rounded-full">{entry.mood}</span>
                  )}
                  <button onClick={() => handleDelete(entry.id)} className="text-xs text-red-500 hover:text-red-700">Delete</button>
                </div>
              </div>
              <p className="text-sm text-slate-700 whitespace-pre-wrap">{entry.body}</p>
              {entry.project_title && (
                <Link href={`/projects/${entry.project_id}`} className="inline-block mt-2 text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full hover:bg-blue-100">
                  {entry.project_title}
                </Link>
              )}
              {entry.tags && (
                <div className="mt-3 flex gap-1 flex-wrap">
                  {entry.tags.split(",").map((tag) => (
                    <span key={tag.trim()} className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded">{tag.trim()}</span>
                  ))}
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </>
  );
}
