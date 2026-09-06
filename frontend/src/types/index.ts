export interface TopicProgress {
  attempts: number;
  correct: number;
  total: number;
  accuracy: number;
}

export interface RecommendationStrategy {
  level: string;
  questions: number;
  difficulty: string;
  focus: string;
}

export interface Recommendation {
  topic: string;
  accuracy: number;
  reason: string;
  strategy: RecommendationStrategy;
}

export interface WeakTopic {
  topic: string;
  accuracy: number;
  attempts: number;
  correct: number;
  total: number;
}

export interface TopicChunk {
  source: string;
  chunk: number;
  score: number;
  text: string;
}
