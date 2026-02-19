"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { projects, Project, deadlines, Deadline, tasks, Task, goals, Goal } from "@/lib/api";

export default function Dashboard() {
  const [recentProjects, setProjects] = useState<Project[]>([]);
  const [upcomingDeadlines, setDeadlines] = useState<Deadline[]>([]);
  const [openTasks, setTasks] = useState<Task[]>([]);
  const [activeGoals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      projects.list("active").catch(() => []),
      deadlines.list({ upcoming_only: true }).catch(() => []),
      tasks.list({ status: "todo" }).catch(() => []),
      goals.list({ status: "active" }).catch(() => []),
    ]).then(([p, d, t, g]) => {
      setProjects(p);
      setDeadlines(d);
      setTasks(t);
      setGoals(g);
      setLoading(false);
    });
  }, []);

  if (loading) return <p className="text-slate-500">Loading...</p>;

  return (
    <>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Active Projects" value={recentProjects.length} href="/projects" color="bg-blue-500" />
        <StatCard label="Upcoming Deadlines" value={upcomingDeadlines.length} href="/deadlines" color="bg-red-500" />
        <StatCard label="Open Tasks" value={openTasks.length} href="/tasks" color="bg-amber-500" />
        <StatCard label="Active Goals" value={activeGoals.length} href="/goals" color="bg-emerald-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming deadlines */}
        <section className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-lg">Upcoming Deadlines</h2>
            <Link href="/deadlines" className="text-sm text-blue-600 hover:underline">View all</Link>
          </div>
          {upcomingDeadlines.length === 0 ? (
            <p className="text-slate-400 text-sm">No upcoming deadlines</p>
          ) : (
            <ul className="space-y-3">
              {upcomingDeadlines.slice(0, 5).map((d) => (
                <li key={d.id} className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{d.title}</p>
                    <p className="text-xs text-slate-500">{d.kind}</p>
                  </div>
                  <span className="text-xs bg-red-50 text-red-700 px-2 py-1 rounded-full">
                    {new Date(d.due_date).toLocaleDateString()}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Open tasks */}
        <section className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-lg">Open Tasks</h2>
            <Link href="/tasks" className="text-sm text-blue-600 hover:underline">View all</Link>
          </div>
          {openTasks.length === 0 ? (
            <p className="text-slate-400 text-sm">All clear!</p>
          ) : (
            <ul className="space-y-3">
              {openTasks.slice(0, 5).map((t) => (
                <li key={t.id} className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{t.title}</p>
                    <p className="text-xs text-slate-500">{t.priority} priority</p>
                  </div>
                  {t.due_date && (
                    <span className="text-xs text-slate-500">
                      {new Date(t.due_date).toLocaleDateString()}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Active projects */}
        <section className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-lg">Active Projects</h2>
            <Link href="/projects" className="text-sm text-blue-600 hover:underline">View all</Link>
          </div>
          {recentProjects.length === 0 ? (
            <p className="text-slate-400 text-sm">No active projects</p>
          ) : (
            <ul className="space-y-3">
              {recentProjects.slice(0, 5).map((p) => (
                <li key={p.id}>
                  <p className="text-sm font-medium">{p.title}</p>
                  {p.description && <p className="text-xs text-slate-500 truncate">{p.description}</p>}
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Active goals */}
        <section className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-lg">Active Goals</h2>
            <Link href="/goals" className="text-sm text-blue-600 hover:underline">View all</Link>
          </div>
          {activeGoals.length === 0 ? (
            <p className="text-slate-400 text-sm">No active goals</p>
          ) : (
            <ul className="space-y-3">
              {activeGoals.slice(0, 5).map((g) => (
                <li key={g.id} className="flex items-center justify-between">
                  <p className="text-sm font-medium">{g.title}</p>
                  <span className="text-xs bg-emerald-50 text-emerald-700 px-2 py-1 rounded-full">
                    {g.timeframe}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      {/* Quick link to assistant */}
      <div className="mt-8">
        <Link
          href="/chat"
          className="inline-flex items-center gap-2 bg-slate-900 text-white px-5 py-3 rounded-lg hover:bg-slate-800 transition-colors text-sm font-medium"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          Ask your assistant
        </Link>
      </div>
    </>
  );
}

function StatCard({ label, value, href, color }: { label: string; value: number; href: string; color: string }) {
  return (
    <Link href={href} className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 hover:shadow-md transition-shadow">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg ${color} flex items-center justify-center text-white text-lg font-bold`}>
          {value}
        </div>
        <p className="text-sm text-slate-600 font-medium">{label}</p>
      </div>
    </Link>
  );
}
