"use client";

import { useEffect, useState } from "react";
import { goals, Goal, Milestone } from "@/lib/api";

const TIMEFRAME_OPTIONS = ["weekly", "monthly", "semester", "yearly", "multi_year"];
const STATUS_OPTIONS = ["active", "achieved", "deferred", "dropped"];

export default function GoalsPage() {
  const [items, setItems] = useState<Goal[]>([]);
  const [milestones, setMilestones] = useState<Record<number, Milestone[]>>({});
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [expandedGoal, setExpandedGoal] = useState<number | null>(null);
  const [form, setForm] = useState({ title: "", description: "", timeframe: "semester", target_date: "" });
  const [msForm, setMsForm] = useState({ title: "", target_date: "" });
  const [showMsForm, setShowMsForm] = useState<number | null>(null);

  const load = () => {
    goals.list().then(setItems).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const loadMilestones = async (goalId: number) => {
    const ms = await goals.milestones.list(goalId);
    setMilestones((prev) => ({ ...prev, [goalId]: ms }));
  };

  const toggleExpand = (goalId: number) => {
    if (expandedGoal === goalId) {
      setExpandedGoal(null);
    } else {
      setExpandedGoal(goalId);
      if (!milestones[goalId]) loadMilestones(goalId);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await goals.create({ ...form, target_date: form.target_date || null });
    setForm({ title: "", description: "", timeframe: "semester", target_date: "" });
    setShowForm(false);
    load();
  };

  const handleMsSubmit = async (e: React.FormEvent, goalId: number) => {
    e.preventDefault();
    await goals.milestones.create(goalId, { ...msForm, target_date: msForm.target_date || null });
    setMsForm({ title: "", target_date: "" });
    setShowMsForm(null);
    loadMilestones(goalId);
  };

  const toggleMilestone = async (ms: Milestone) => {
    await goals.milestones.update(ms.id, { is_complete: !ms.is_complete });
    loadMilestones(ms.goal_id);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this goal?")) return;
    await goals.delete(id);
    load();
  };

  if (loading) return <p className="text-slate-500">Loading...</p>;

  return (
    <>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Goals</h1>
        <button onClick={() => setShowForm(true)} className="bg-emerald-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-emerald-700">
          + New Goal
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
            <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Timeframe</label>
              <select value={form.timeframe} onChange={(e) => setForm({ ...form, timeframe: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm">
                {TIMEFRAME_OPTIONS.map((t) => <option key={t} value={t}>{t.replace("_", " ")}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Target Date</label>
              <input type="date" value={form.target_date} onChange={(e) => setForm({ ...form, target_date: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" className="bg-emerald-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-emerald-700">Create</button>
            <button type="button" onClick={() => setShowForm(false)} className="text-sm px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-50">Cancel</button>
          </div>
        </form>
      )}

      {items.length === 0 ? (
        <p className="text-slate-400">No goals yet. Set your first goal!</p>
      ) : (
        <div className="space-y-3">
          {items.map((g) => (
            <div key={g.id} className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
              <div className="flex items-start justify-between">
                <div className="cursor-pointer flex-1" onClick={() => toggleExpand(g.id)}>
                  <h3 className="font-semibold">{g.title}</h3>
                  {g.description && <p className="text-sm text-slate-500 mt-1">{g.description}</p>}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs bg-emerald-50 text-emerald-700 px-2 py-1 rounded-full">{g.timeframe.replace("_", " ")}</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    g.status === "active" ? "bg-green-50 text-green-700" :
                    g.status === "achieved" ? "bg-blue-50 text-blue-700" :
                    "bg-slate-100 text-slate-600"
                  }`}>{g.status}</span>
                  <button onClick={() => handleDelete(g.id)} className="text-xs text-red-500 hover:text-red-700">Delete</button>
                </div>
              </div>

              {expandedGoal === g.id && (
                <div className="mt-4 pl-4 border-l-2 border-emerald-200">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-slate-700">Milestones</h4>
                    <button onClick={() => setShowMsForm(g.id)} className="text-xs text-emerald-600 hover:underline">+ Add</button>
                  </div>

                  {showMsForm === g.id && (
                    <form onSubmit={(e) => handleMsSubmit(e, g.id)} className="flex gap-2 mb-3">
                      <input required placeholder="Milestone title" value={msForm.title} onChange={(e) => setMsForm({ ...msForm, title: e.target.value })} className="flex-1 border border-slate-300 rounded-lg px-3 py-1.5 text-sm" />
                      <input type="date" value={msForm.target_date} onChange={(e) => setMsForm({ ...msForm, target_date: e.target.value })} className="border border-slate-300 rounded-lg px-3 py-1.5 text-sm" />
                      <button type="submit" className="bg-emerald-600 text-white text-xs px-3 py-1.5 rounded-lg">Add</button>
                    </form>
                  )}

                  {(milestones[g.id] || []).length === 0 ? (
                    <p className="text-xs text-slate-400">No milestones yet.</p>
                  ) : (
                    <ul className="space-y-2">
                      {(milestones[g.id] || []).map((ms) => (
                        <li key={ms.id} className="flex items-center gap-3">
                          <button
                            onClick={() => toggleMilestone(ms)}
                            className={`w-4 h-4 rounded border-2 flex-shrink-0 flex items-center justify-center ${
                              ms.is_complete ? "bg-emerald-500 border-emerald-500 text-white" : "border-slate-300"
                            }`}
                          >
                            {ms.is_complete && (
                              <svg className="w-2.5 h-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                              </svg>
                            )}
                          </button>
                          <span className={`text-sm ${ms.is_complete ? "line-through text-slate-400" : ""}`}>{ms.title}</span>
                          {ms.target_date && <span className="text-xs text-slate-400">{ms.target_date}</span>}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </>
  );
}
