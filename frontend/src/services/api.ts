import type {
  Recommendation,
  TopicChunk,
  TopicProgress,
  WeakTopic,
} from "../types";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  const payload = (await response.json()) as T & { error?: string };
  if (!response.ok) {
    throw new Error(payload.error || "The Claude Lab backend returned an error.");
  }
  return payload;
}

export function getProgress(): Promise<{ progress: Record<string, TopicProgress> }> {
  return request("/api/progress");
}

export function getRecommendation(): Promise<{
  available: boolean;
  weak_topics: WeakTopic[];
  recommendation: Recommendation | null;
}> {
  return request("/api/recommendation");
}

export function getTopic(topic: string): Promise<{
  topic: string;
  found: boolean;
  content: TopicChunk[];
}> {
  return request(`/api/topic/${encodeURIComponent(topic)}`);
}

export function recordPractice(topic: string, correct: number, total: number) {
  return request<{ message: string }>("/api/practice", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, correct, total }),
  });
}
