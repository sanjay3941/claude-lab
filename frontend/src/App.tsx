import { useEffect, useMemo, useState } from "react";
import {
  getProgress,
  getRecommendation,
  getTopic,
  recordPractice,
} from "./services/api";
import type { Recommendation, TopicChunk, TopicProgress } from "./types";
import "./styles.css";

type Screen = "dashboard" | "topic" | "quiz" | "result";

interface Question {
  prompt: string;
  options: string[];
  answer: number;
}

const questions: Question[] = [
  {
    prompt: "Which condition requires a resource to be held while waiting for another?",
    options: ["Mutual exclusion", "Hold and wait", "Preemption", "Circular wait"],
    answer: 1,
  },
  {
    prompt: "What does a semaphore primarily help coordinate?",
    options: ["Process synchronization", "Disk formatting", "Memory paging", "File compression"],
    answer: 0,
  },
  {
    prompt: "Which scheduling algorithm uses a fixed time slice?",
    options: ["First-come, first-served", "Round robin", "Shortest job first", "Priority only"],
    answer: 1,
  },
  {
    prompt: "Virtual memory allows a system to use disk space as an extension of what?",
    options: ["The CPU", "The network", "Main memory", "The file system"],
    answer: 2,
  },
  {
    prompt: "What is a context switch?",
    options: [
      "Changing a file extension",
      "Saving one process state and loading another",
      "Moving a page to disk",
      "Restarting the operating system",
    ],
    answer: 1,
  },
];

function App() {
  const [screen, setScreen] = useState<Screen>("dashboard");
  const [progress, setProgress] = useState<Record<string, TopicProgress>>({});
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [weakTopics, setWeakTopics] = useState<string[]>([]);
  const [topicContent, setTopicContent] = useState<TopicChunk[]>([]);
  const [topic, setTopic] = useState("");
  const [questionIndex, setQuestionIndex] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [correct, setCorrect] = useState(0);
  const [lastScore, setLastScore] = useState({ correct: 0, total: questions.length });
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [recorded, setRecorded] = useState(false);

  const loadDashboard = async () => {
    setLoading(true);
    setError("");
    try {
      const [progressResponse, recommendationResponse] = await Promise.all([
        getProgress(),
        getRecommendation(),
      ]);
      setProgress(progressResponse.progress);
      setRecommendation(recommendationResponse.recommendation);
      setWeakTopics(recommendationResponse.weak_topics.map((item) => item.topic));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to connect to Claude Lab backend.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadDashboard();
  }, []);

  const startLearning = async () => {
    if (!recommendation?.topic) return;
    setBusy("Loading study material...");
    setError("");
    try {
      const response = await getTopic(recommendation.topic);
      setTopic(recommendation.topic);
      setTopicContent(response.content);
      setScreen("topic");
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load study material.");
    } finally {
      setBusy("");
    }
  };

  const startPractice = () => {
    setQuestionIndex(0);
    setSelected(null);
    setCorrect(0);
    setRecorded(false);
    setScreen("quiz");
  };

  const answerQuestion = () => {
    if (selected === null) return;
    const nextCorrect = correct + (selected === questions[questionIndex].answer ? 1 : 0);
    if (questionIndex === questions.length - 1) {
      setCorrect(nextCorrect);
      setLastScore({ correct: nextCorrect, total: questions.length });
      setScreen("result");
      return;
    }
    setCorrect(nextCorrect);
    setQuestionIndex((current) => current + 1);
    setSelected(null);
  };

  const saveResult = async () => {
    setBusy("Recording result...");
    setError("");
    try {
      await recordPractice(topic, lastScore.correct, lastScore.total);
      setRecorded(true);
      await loadDashboard();
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Practice result could not be recorded.");
    } finally {
      setBusy("");
    }
  };

  const scorePercent = Math.round((lastScore.correct / lastScore.total) * 100);
  const currentQuestion = questions[questionIndex];
  const totalQuestions = Object.values(progress).reduce((sum, item) => sum + item.total, 0);
  const topicCount = Object.keys(progress).length;
  const progressCards = useMemo(
    () => Object.entries(progress).sort(([, left], [, right]) => left.accuracy - right.accuracy),
    [progress],
  );

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark">CL</span><div><strong>Claude Lab</strong><span>Student Lab</span></div></div>
        <span className="status-dot">Adaptive learning workspace</span>
      </header>
      <section className="hero">
        <p className="eyebrow">STUDENT LAB / LEARNING CONSOLE</p>
        <h1>Build understanding, one focused session at a time.</h1>
        <p className="hero-copy">Study from your course material, practice what needs attention, and let your progress shape the next recommendation.</p>
      </section>
      {error && <div className="alert error"><strong>Something went wrong.</strong> {error}</div>}
      {busy && <div className="alert info">{busy}</div>}
      {screen === "dashboard" && (
        <section className="content-grid">
          <div className="main-column">
            <div className="section-heading"><div><p className="eyebrow">OVERVIEW</p><h2>Your progress</h2></div><button className="text-button" onClick={() => void loadDashboard()}>Refresh data</button></div>
            {loading ? <div className="panel empty">Loading progress...</div> : topicCount === 0 ? <div className="panel empty"><h3>No practice history yet.</h3><p>Complete your first practice session to receive adaptive recommendations.</p></div> : <div className="progress-list">{progressCards.map(([name, item]) => <div className="panel progress-row" key={name}><div><h3>{name}</h3><p>{item.attempts} attempt{item.attempts === 1 ? "" : "s"} · {item.correct}/{item.total} correct</p></div><div className="accuracy"><strong>{item.accuracy}%</strong><span>accuracy</span></div></div>)}</div>}
            <div className="metrics"><div className="metric"><span>Topics practiced</span><strong>{topicCount}</strong></div><div className="metric"><span>Total questions</span><strong>{totalQuestions}</strong></div><div className="metric"><span>Focus areas</span><strong>{weakTopics.length}</strong></div></div>
          </div>
          <aside className="panel recommendation"><p className="eyebrow">NEXT BEST STEP</p><h2>Learning recommendation</h2>{loading ? <p className="muted">Loading recommendation...</p> : recommendation ? <><div className="recommend-topic">{recommendation.topic}<span>{recommendation.strategy.level}</span></div><p className="reason">{recommendation.reason}</p><div className="detail-grid"><div><span>Current accuracy</span><strong>{recommendation.accuracy}%</strong></div><div><span>Difficulty</span><strong>{recommendation.strategy.difficulty}</strong></div><div><span>Questions</span><strong>{recommendation.strategy.questions}</strong></div></div><p className="focus"><strong>Focus:</strong> {recommendation.strategy.focus}</p><button className="primary-button" onClick={() => void startLearning()}>Start learning <span>→</span></button></> : <div className="empty compact"><h3>Practice to unlock recommendations.</h3><p>Your next topic will be selected from your recorded results.</p></div>}</aside>
        </section>
      )}
      {screen === "topic" && <section className="panel reading"><button className="back-button" onClick={() => setScreen("dashboard")}>← Back to dashboard</button><p className="eyebrow">STUDY MATERIAL</p><h2>{topic}</h2><p className="muted">Retrieved from your Claude Lab knowledge base. Use this review before starting practice.</p>{topicContent.length === 0 ? <div className="empty"><p>No study material found for this topic.</p></div> : <div className="source-list">{topicContent.map((chunk) => <article className="source-card" key={`${chunk.source}-${chunk.chunk}`}><div className="source-label">{chunk.source} · Chunk {chunk.chunk}</div><p>{chunk.text}</p></article>)}</div>}<button className="primary-button" onClick={startPractice}>Start practice <span>→</span></button></section>}
      {screen === "quiz" && <section className="panel quiz"><div className="quiz-top"><button className="back-button" onClick={() => setScreen("topic")}>← Study material</button><span>Question {questionIndex + 1} of {questions.length}</span></div><div className="progress-bar"><span style={{ width: `${((questionIndex + 1) / questions.length) * 100}%` }} /></div><p className="eyebrow">PRACTICE / {topic}</p><h2>{currentQuestion.prompt}</h2><div className="options">{currentQuestion.options.map((option, index) => <button className={`option ${selected === index ? "selected" : ""}`} key={option} onClick={() => setSelected(index)}><span>{String.fromCharCode(65 + index)}</span>{option}</button>)}</div><button className="primary-button" disabled={selected === null} onClick={answerQuestion}>{questionIndex === questions.length - 1 ? "See result" : "Next question"} <span>→</span></button></section>}
      {screen === "result" && <section className="panel result"><p className="eyebrow">PRACTICE COMPLETE</p><h2>Nice work on {topic}.</h2><div className="score-ring"><strong>{scorePercent}%</strong><span>{lastScore.correct} of {lastScore.total} correct</span></div>{recorded ? <><div className="success-box">Result recorded successfully. Your dashboard and recommendation are up to date.</div><button className="primary-button" onClick={() => setScreen("dashboard")}>View updated dashboard <span>→</span></button></> : <><p className="muted">Record this session to update your adaptive learning path.</p><button className="primary-button" onClick={() => void saveResult()}>Record practice result <span>→</span></button></>}</section>}
      <footer>Claude Lab · Student Lab <span>Backend-powered adaptive learning</span></footer>
    </main>
  );
}

export default App;
