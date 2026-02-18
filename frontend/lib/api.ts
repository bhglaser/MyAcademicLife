const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// -- Research Projects -------------------------------------------------------

export interface Project {
  id: number;
  title: string;
  description: string | null;
  status: string;
  start_date: string | null;
  target_end_date: string | null;
  collaborators: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectNote {
  id: number;
  content: string;
  project_id: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectDetail extends Project {
  project_notes: ProjectNote[];
  journal_entries: JournalEntry[];
  publications: Publication[];
  deadlines: Deadline[];
}

export const projects = {
  list: (status?: string) =>
    request<Project[]>(`/api/projects/${status ? `?status=${status}` : ""}`),
  get: (id: number) => request<Project>(`/api/projects/${id}`),
  detail: (id: number) => request<ProjectDetail>(`/api/projects/${id}/detail`),
  create: (data: Partial<Project>) =>
    request<Project>("/api/projects/", { method: "POST", body: JSON.stringify(data) }),
  update: (id: number, data: Partial<Project>) =>
    request<Project>(`/api/projects/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (id: number) =>
    request<void>(`/api/projects/${id}`, { method: "DELETE" }),
  notes: {
    list: (projectId: number) =>
      request<ProjectNote[]>(`/api/projects/${projectId}/notes`),
    create: (projectId: number, data: { content: string }) =>
      request<ProjectNote>(`/api/projects/${projectId}/notes`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (noteId: number, data: { content?: string }) =>
      request<ProjectNote>(`/api/projects/notes/${noteId}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    delete: (noteId: number) =>
      request<void>(`/api/projects/notes/${noteId}`, { method: "DELETE" }),
  },
};

// -- Deadlines ---------------------------------------------------------------

export interface Deadline {
  id: number;
  title: string;
  description: string | null;
  kind: string;
  status: string;
  due_date: string;
  reminder_days_before: number;
  url: string | null;
  notes: string | null;
  project_id: number | null;
  created_at: string;
  updated_at: string;
}

export const deadlines = {
  list: (params?: { status?: string; upcoming_only?: boolean }) => {
    const sp = new URLSearchParams();
    if (params?.status) sp.set("status", params.status);
    if (params?.upcoming_only) sp.set("upcoming_only", "true");
    const qs = sp.toString();
    return request<Deadline[]>(`/api/deadlines/${qs ? `?${qs}` : ""}`);
  },
  create: (data: Partial<Deadline>) =>
    request<Deadline>("/api/deadlines/", { method: "POST", body: JSON.stringify(data) }),
  update: (id: number, data: Partial<Deadline>) =>
    request<Deadline>(`/api/deadlines/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (id: number) =>
    request<void>(`/api/deadlines/${id}`, { method: "DELETE" }),
};

// -- Tasks -------------------------------------------------------------------

export interface Task {
  id: number;
  title: string;
  description: string | null;
  priority: string;
  status: string;
  due_date: string | null;
  estimated_hours: number | null;
  actual_hours: number | null;
  is_recurring: boolean;
  category_id: number | null;
  parent_id: number | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface TaskCategory {
  id: number;
  name: string;
  color: string | null;
  description: string | null;
}

export const tasks = {
  list: (params?: { status?: string; priority?: string }) => {
    const sp = new URLSearchParams();
    if (params?.status) sp.set("status", params.status);
    if (params?.priority) sp.set("priority", params.priority);
    const qs = sp.toString();
    return request<Task[]>(`/api/tasks/${qs ? `?${qs}` : ""}`);
  },
  create: (data: Partial<Task>) =>
    request<Task>("/api/tasks/", { method: "POST", body: JSON.stringify(data) }),
  update: (id: number, data: Partial<Task>) =>
    request<Task>(`/api/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (id: number) =>
    request<void>(`/api/tasks/${id}`, { method: "DELETE" }),
  categories: {
    list: () => request<TaskCategory[]>("/api/tasks/categories"),
    create: (data: Partial<TaskCategory>) =>
      request<TaskCategory>("/api/tasks/categories", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },
};

// -- Goals -------------------------------------------------------------------

export interface Goal {
  id: number;
  title: string;
  description: string | null;
  timeframe: string;
  status: string;
  target_date: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Milestone {
  id: number;
  title: string;
  description: string | null;
  is_complete: boolean;
  target_date: string | null;
  completed_date: string | null;
  goal_id: number;
  created_at: string;
  updated_at: string;
}

export const goals = {
  list: (params?: { status?: string; timeframe?: string }) => {
    const sp = new URLSearchParams();
    if (params?.status) sp.set("status", params.status);
    if (params?.timeframe) sp.set("timeframe", params.timeframe);
    const qs = sp.toString();
    return request<Goal[]>(`/api/goals/${qs ? `?${qs}` : ""}`);
  },
  create: (data: Partial<Goal>) =>
    request<Goal>("/api/goals/", { method: "POST", body: JSON.stringify(data) }),
  update: (id: number, data: Partial<Goal>) =>
    request<Goal>(`/api/goals/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (id: number) =>
    request<void>(`/api/goals/${id}`, { method: "DELETE" }),
  milestones: {
    list: (goalId: number) => request<Milestone[]>(`/api/goals/${goalId}/milestones`),
    create: (goalId: number, data: Partial<Milestone>) =>
      request<Milestone>(`/api/goals/${goalId}/milestones`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (msId: number, data: Partial<Milestone>) =>
      request<Milestone>(`/api/goals/milestones/${msId}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
  },
};

// -- Journal -----------------------------------------------------------------

export interface JournalEntry {
  id: number;
  entry_date: string;
  title: string | null;
  body: string;
  mood: string | null;
  tags: string | null;
  project_id: number | null;
  project_title: string | null;
  created_at: string;
  updated_at: string;
}

export const journal = {
  list: (params?: { mood?: string; project_id?: number }) => {
    const sp = new URLSearchParams();
    if (params?.mood) sp.set("mood", params.mood);
    if (params?.project_id) sp.set("project_id", String(params.project_id));
    const qs = sp.toString();
    return request<JournalEntry[]>(`/api/journal/${qs ? `?${qs}` : ""}`);
  },
  create: (data: Partial<JournalEntry>) =>
    request<JournalEntry>("/api/journal/", { method: "POST", body: JSON.stringify(data) }),
  update: (id: number, data: Partial<JournalEntry>) =>
    request<JournalEntry>(`/api/journal/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (id: number) =>
    request<void>(`/api/journal/${id}`, { method: "DELETE" }),
};

// -- CV ----------------------------------------------------------------------

export interface CVSection {
  id: number;
  name: string;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface CVEntry {
  id: number;
  section: string;
  title: string;
  organization: string | null;
  location: string | null;
  start_date: string | null;
  end_date: string | null;
  description: string | null;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export const cv = {
  sections: {
    list: () => request<CVSection[]>("/api/cv/sections"),
    create: (data: Partial<CVSection>) =>
      request<CVSection>("/api/cv/sections", { method: "POST", body: JSON.stringify(data) }),
  },
  entries: {
    list: (section?: string) =>
      request<CVEntry[]>(`/api/cv/entries${section ? `?section=${section}` : ""}`),
    create: (data: Partial<CVEntry>) =>
      request<CVEntry>("/api/cv/entries", { method: "POST", body: JSON.stringify(data) }),
    update: (id: number, data: Partial<CVEntry>) =>
      request<CVEntry>(`/api/cv/entries/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    delete: (id: number) =>
      request<void>(`/api/cv/entries/${id}`, { method: "DELETE" }),
  },
};

// -- Chat --------------------------------------------------------------------

export interface ToolAction {
  tool: string;
  input: Record<string, unknown>;
  result: Record<string, unknown>;
}

export interface ChatMessageRead {
  id: number;
  role: "user" | "assistant";
  content: string;
  tool_actions: ToolAction[] | null;
  created_at: string;
}

export interface ChatResponse {
  reply: string;
  tool_actions: ToolAction[] | null;
  user_message_id: number;
  assistant_message_id: number;
}

export const chat = {
  send: (message: string) =>
    request<ChatResponse>("/api/chat/", { method: "POST", body: JSON.stringify({ message }) }),
  history: (limit = 100) =>
    request<ChatMessageRead[]>(`/api/chat/history?limit=${limit}`),
  clearHistory: () =>
    request<void>("/api/chat/history", { method: "DELETE" }),
};

// -- Publications ------------------------------------------------------------

export interface Publication {
  id: number;
  title: string;
  authors: string | null;
  venue: string | null;
  status: string;
  abstract: string | null;
  doi: string | null;
  url: string | null;
  submitted_date: string | null;
  accepted_date: string | null;
  published_date: string | null;
  notes: string | null;
  project_id: number | null;
  created_at: string;
  updated_at: string;
}

export const publications = {
  list: (params?: { status?: string; project_id?: number }) => {
    const sp = new URLSearchParams();
    if (params?.status) sp.set("status", params.status);
    if (params?.project_id) sp.set("project_id", String(params.project_id));
    const qs = sp.toString();
    return request<Publication[]>(`/api/publications/${qs ? `?${qs}` : ""}`);
  },
  create: (data: Partial<Publication>) =>
    request<Publication>("/api/publications/", { method: "POST", body: JSON.stringify(data) }),
  update: (id: number, data: Partial<Publication>) =>
    request<Publication>(`/api/publications/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    request<void>(`/api/publications/${id}`, { method: "DELETE" }),
};
