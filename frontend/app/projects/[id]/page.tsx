"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { projects, ProjectDetail, ProjectNote } from "@/lib/api";

type TimelineItem =
  | { type: "note"; date: string; data: ProjectNote }
  | { type: "journal"; date: string; data: ProjectDetail["journal_entries"][number] }
  | { type: "publication"; date: string; data: ProjectDetail["publications"][number] }
  | { type: "deadline"; date: string; data: ProjectDetail["deadlines"][number] };

const BORDER_COLORS: Record<TimelineItem["type"], string> = {
  note: "border-l-blue-500",
  journal: "border-l-violet-500",
  publication: "border-l-green-500",
  deadline: "border-l-orange-500",
};

const TYPE_LABELS: Record<TimelineItem["type"], string> = {
  note: "Note",
  journal: "Journal",
  publication: "Publication",
  deadline: "Deadline",
};

const LABEL_COLORS: Record<TimelineItem["type"], string> = {
  note: "bg-blue-50 text-blue-700",
  journal: "bg-violet-50 text-violet-700",
  publication: "bg-green-50 text-green-700",
  deadline: "bg-orange-50 text-orange-700",
};

function buildTimeline(detail: ProjectDetail): TimelineItem[] {
  const items: TimelineItem[] = [];
  for (const n of detail.project_notes) {
    items.push({ type: "note", date: n.created_at, data: n });
  }
  for (const j of detail.journal_entries) {
    items.push({ type: "journal", date: j.entry_date, data: j });
  }
  for (const p of detail.publications) {
    items.push({ type: "publication", date: p.updated_at, data: p });
  }
  for (const d of detail.deadlines) {
    items.push({ type: "deadline", date: d.due_date, data: d });
  }
  items.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  return items;
}

export default function ProjectDetailPage() {
  const params = useParams();
  const projectId = Number(params.id);

  const [detail, setDetail] = useState<ProjectDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [noteText, setNoteText] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = () => {
    projects.detail(projectId).then(setDetail).finally(() => setLoading(false));
  };

  useEffect(load, [projectId]);

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteText.trim()) return;
    setSubmitting(true);
    await projects.notes.create(projectId, { content: noteText.trim() });
    setNoteText("");
    setSubmitting(false);
    load();
  };

  const handleDeleteNote = async (noteId: number) => {
    if (!confirm("Delete this note?")) return;
    await projects.notes.delete(noteId);
    load();
  };

  if (loading) return <p className="text-slate-500">Loading...</p>;
  if (!detail) return <p className="text-red-500">Project not found.</p>;

  const timeline = buildTimeline(detail);

  return (
    <>
      {/* Back link */}
      <Link href="/projects" className="text-sm text-slate-500 hover:text-slate-700 mb-4 inline-block">&larr; Back to Projects</Link>

      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">{detail.title}</h1>
          {detail.description && <p className="text-slate-500 mt-1">{detail.description}</p>}
        </div>
        <span className={`text-xs px-2 py-1 rounded-full ${
          detail.status === "active" ? "bg-green-50 text-green-700" :
          detail.status === "completed" ? "bg-blue-50 text-blue-700" :
          "bg-slate-100 text-slate-600"
        }`}>
          {detail.status.replace("_", " ")}
        </span>
      </div>

      {/* Metadata */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {detail.collaborators && (
          <div className="bg-white rounded-lg border border-slate-200 p-3">
            <p className="text-xs text-slate-400">Collaborators</p>
            <p className="text-sm font-medium mt-0.5">{detail.collaborators}</p>
          </div>
        )}
        {detail.start_date && (
          <div className="bg-white rounded-lg border border-slate-200 p-3">
            <p className="text-xs text-slate-400">Start Date</p>
            <p className="text-sm font-medium mt-0.5">{detail.start_date}</p>
          </div>
        )}
        {detail.target_end_date && (
          <div className="bg-white rounded-lg border border-slate-200 p-3">
            <p className="text-xs text-slate-400">Target End</p>
            <p className="text-sm font-medium mt-0.5">{detail.target_end_date}</p>
          </div>
        )}
        <div className="bg-white rounded-lg border border-slate-200 p-3">
          <p className="text-xs text-slate-400">Activity</p>
          <p className="text-sm font-medium mt-0.5">
            {detail.project_notes.length} notes &middot; {detail.journal_entries.length} journal &middot; {detail.publications.length} pubs &middot; {detail.deadlines.length} deadlines
          </p>
        </div>
      </div>

      {/* Add Note Form */}
      <form onSubmit={handleAddNote} className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 mb-6">
        <label className="block text-sm font-medium mb-2">Add a note</label>
        <textarea
          value={noteText}
          onChange={(e) => setNoteText(e.target.value)}
          rows={3}
          className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm mb-2"
          placeholder="Meeting notes, observations, ideas..."
        />
        <button
          type="submit"
          disabled={submitting || !noteText.trim()}
          className="bg-blue-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? "Saving..." : "Add Note"}
        </button>
      </form>

      {/* Timeline */}
      <h2 className="text-lg font-semibold mb-3">Timeline</h2>
      {timeline.length === 0 ? (
        <p className="text-slate-400 text-sm">No activity yet. Add a note or tag a journal entry to this project.</p>
      ) : (
        <div className="space-y-3">
          {timeline.map((item, idx) => (
            <div
              key={`${item.type}-${idx}`}
              className={`bg-white rounded-lg border border-slate-200 border-l-4 ${BORDER_COLORS[item.type]} p-4`}
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${LABEL_COLORS[item.type]}`}>
                    {TYPE_LABELS[item.type]}
                  </span>
                  <span className="text-xs text-slate-400">
                    {new Date(item.date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                  </span>
                </div>
                {item.type === "note" && (
                  <button
                    onClick={() => handleDeleteNote((item.data as ProjectNote).id)}
                    className="text-xs text-red-500 hover:text-red-700"
                  >
                    Delete
                  </button>
                )}
              </div>

              {item.type === "note" && (
                <p className="text-sm text-slate-700 whitespace-pre-wrap">{(item.data as ProjectNote).content}</p>
              )}

              {item.type === "journal" && (
                <div>
                  {(item.data as ProjectDetail["journal_entries"][number]).title && (
                    <p className="text-sm font-medium">{(item.data as ProjectDetail["journal_entries"][number]).title}</p>
                  )}
                  <p className="text-sm text-slate-700 whitespace-pre-wrap">
                    {(item.data as ProjectDetail["journal_entries"][number]).body}
                  </p>
                  {(item.data as ProjectDetail["journal_entries"][number]).mood && (
                    <span className="inline-block mt-1 text-xs bg-violet-50 text-violet-700 px-2 py-0.5 rounded-full">
                      {(item.data as ProjectDetail["journal_entries"][number]).mood}
                    </span>
                  )}
                </div>
              )}

              {item.type === "publication" && (
                <div>
                  <p className="text-sm font-medium">{(item.data as ProjectDetail["publications"][number]).title}</p>
                  {(item.data as ProjectDetail["publications"][number]).venue && (
                    <p className="text-xs text-slate-500">{(item.data as ProjectDetail["publications"][number]).venue}</p>
                  )}
                  <span className="inline-block mt-1 text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full">
                    {(item.data as ProjectDetail["publications"][number]).status.replace("_", " ")}
                  </span>
                </div>
              )}

              {item.type === "deadline" && (
                <div>
                  <p className="text-sm font-medium">{(item.data as ProjectDetail["deadlines"][number]).title}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs bg-orange-50 text-orange-700 px-2 py-0.5 rounded-full">
                      {(item.data as ProjectDetail["deadlines"][number]).kind}
                    </span>
                    <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                      {(item.data as ProjectDetail["deadlines"][number]).status}
                    </span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </>
  );
}
