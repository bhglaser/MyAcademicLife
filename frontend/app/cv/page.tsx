"use client";

import { useEffect, useState } from "react";
import { cv, CVSection, CVEntry } from "@/lib/api";

export default function CVPage() {
  const [sections, setSections] = useState<CVSection[]>([]);
  const [entries, setEntries] = useState<CVEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [showSectionForm, setShowSectionForm] = useState(false);
  const [showEntryForm, setShowEntryForm] = useState(false);
  const [sectionForm, setSectionForm] = useState({ name: "", display_order: 0 });
  const [entryForm, setEntryForm] = useState({
    section: "", title: "", organization: "", location: "",
    start_date: "", end_date: "", description: "", display_order: 0,
  });

  const load = () => {
    Promise.all([cv.sections.list(), cv.entries.list()])
      .then(([s, e]) => { setSections(s); setEntries(e); })
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleSectionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await cv.sections.create(sectionForm);
    setSectionForm({ name: "", display_order: 0 });
    setShowSectionForm(false);
    load();
  };

  const handleEntrySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await cv.entries.create({
      ...entryForm,
      start_date: entryForm.start_date || null,
      end_date: entryForm.end_date || null,
      organization: entryForm.organization || null,
      location: entryForm.location || null,
      description: entryForm.description || null,
    });
    setEntryForm({ section: "", title: "", organization: "", location: "", start_date: "", end_date: "", description: "", display_order: 0 });
    setShowEntryForm(false);
    load();
  };

  const handleDeleteEntry = async (id: number) => {
    if (!confirm("Delete this CV entry?")) return;
    await cv.entries.delete(id);
    load();
  };

  const entriesBySection = entries.reduce<Record<string, CVEntry[]>>((acc, e) => {
    (acc[e.section] ||= []).push(e);
    return acc;
  }, {});

  if (loading) return <p className="text-slate-500">Loading...</p>;

  return (
    <>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Curriculum Vitae</h1>
        <div className="flex gap-2">
          <button onClick={() => setShowSectionForm(true)} className="text-sm px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-50">
            + Section
          </button>
          <button onClick={() => setShowEntryForm(true)} className="bg-slate-900 text-white text-sm px-4 py-2 rounded-lg hover:bg-slate-800">
            + Entry
          </button>
        </div>
      </div>

      {showSectionForm && (
        <form onSubmit={handleSectionSubmit} className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6 space-y-4">
          <h3 className="font-medium">New Section</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Name</label>
              <input required value={sectionForm.name} onChange={(e) => setSectionForm({ ...sectionForm, name: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" placeholder="e.g. Education, Awards" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Display Order</label>
              <input type="number" value={sectionForm.display_order} onChange={(e) => setSectionForm({ ...sectionForm, display_order: parseInt(e.target.value) || 0 })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" className="bg-slate-900 text-white text-sm px-4 py-2 rounded-lg">Create</button>
            <button type="button" onClick={() => setShowSectionForm(false)} className="text-sm px-4 py-2 rounded-lg border border-slate-300">Cancel</button>
          </div>
        </form>
      )}

      {showEntryForm && (
        <form onSubmit={handleEntrySubmit} className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6 space-y-4">
          <h3 className="font-medium">New CV Entry</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Section</label>
              <select required value={entryForm.section} onChange={(e) => setEntryForm({ ...entryForm, section: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                <option value="">-- select --</option>
                {sections.map((s) => <option key={s.name} value={s.name}>{s.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Title</label>
              <input required value={entryForm.title} onChange={(e) => setEntryForm({ ...entryForm, title: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Organization</label>
              <input value={entryForm.organization} onChange={(e) => setEntryForm({ ...entryForm, organization: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Location</label>
              <input value={entryForm.location} onChange={(e) => setEntryForm({ ...entryForm, location: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Start Date</label>
              <input type="date" value={entryForm.start_date} onChange={(e) => setEntryForm({ ...entryForm, start_date: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">End Date</label>
              <input type="date" value={entryForm.end_date} onChange={(e) => setEntryForm({ ...entryForm, end_date: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea value={entryForm.description} onChange={(e) => setEntryForm({ ...entryForm, description: e.target.value })} rows={3} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div className="flex gap-2">
            <button type="submit" className="bg-slate-900 text-white text-sm px-4 py-2 rounded-lg">Create</button>
            <button type="button" onClick={() => setShowEntryForm(false)} className="text-sm px-4 py-2 rounded-lg border border-slate-300">Cancel</button>
          </div>
        </form>
      )}

      {sections.length === 0 ? (
        <p className="text-slate-400">No CV sections yet. Add sections like &quot;Education&quot;, &quot;Experience&quot;, &quot;Publications&quot;, &quot;Awards&quot;.</p>
      ) : (
        <div className="space-y-6">
          {sections.map((sec) => (
            <section key={sec.name} className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
              <h2 className="text-lg font-semibold mb-3 text-slate-800">{sec.name}</h2>
              {(entriesBySection[sec.name] || []).length === 0 ? (
                <p className="text-sm text-slate-400">No entries in this section.</p>
              ) : (
                <div className="space-y-4">
                  {(entriesBySection[sec.name] || []).map((entry) => (
                    <div key={entry.id} className="flex items-start justify-between border-b border-slate-100 pb-3 last:border-0 last:pb-0">
                      <div>
                        <p className="font-medium text-sm">{entry.title}</p>
                        <p className="text-sm text-slate-500">
                          {[entry.organization, entry.location].filter(Boolean).join(" — ")}
                          {entry.start_date && (
                            <span className="ml-2 text-xs text-slate-400">
                              ({new Date(entry.start_date).getFullYear()}–{entry.end_date ? new Date(entry.end_date).getFullYear() : "Present"})
                            </span>
                          )}
                        </p>
                        {entry.description && <p className="text-xs text-slate-400 mt-1">{entry.description}</p>}
                      </div>
                      <button onClick={() => handleDeleteEntry(entry.id)} className="text-xs text-red-500 hover:text-red-700 flex-shrink-0">Delete</button>
                    </div>
                  ))}
                </div>
              )}
            </section>
          ))}
        </div>
      )}
    </>
  );
}
