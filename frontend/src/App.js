import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useEffect, useMemo, useState } from "react";
import { getProgress, getRecommendation, getTopic, recordPractice, } from "./services/api";
import "./styles.css";
const questions = [
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
    const [screen, setScreen] = useState("dashboard");
    const [progress, setProgress] = useState({});
    const [recommendation, setRecommendation] = useState(null);
    const [weakTopics, setWeakTopics] = useState([]);
    const [topicContent, setTopicContent] = useState([]);
    const [topic, setTopic] = useState("");
    const [questionIndex, setQuestionIndex] = useState(0);
    const [selected, setSelected] = useState(null);
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
        }
        catch (loadError) {
            setError(loadError instanceof Error ? loadError.message : "Unable to connect to Claude Lab backend.");
        }
        finally {
            setLoading(false);
        }
    };
    useEffect(() => {
        void loadDashboard();
    }, []);
    const startLearning = async () => {
        if (!recommendation?.topic)
            return;
        setBusy("Loading study material...");
        setError("");
        try {
            const response = await getTopic(recommendation.topic);
            setTopic(recommendation.topic);
            setTopicContent(response.content);
            setScreen("topic");
        }
        catch (loadError) {
            setError(loadError instanceof Error ? loadError.message : "Unable to load study material.");
        }
        finally {
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
        if (selected === null)
            return;
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
        }
        catch (saveError) {
            setError(saveError instanceof Error ? saveError.message : "Practice result could not be recorded.");
        }
        finally {
            setBusy("");
        }
    };
    const scorePercent = Math.round((lastScore.correct / lastScore.total) * 100);
    const currentQuestion = questions[questionIndex];
    const totalQuestions = Object.values(progress).reduce((sum, item) => sum + item.total, 0);
    const topicCount = Object.keys(progress).length;
    const progressCards = useMemo(() => Object.entries(progress).sort(([, left], [, right]) => left.accuracy - right.accuracy), [progress]);
    return (_jsxs("main", { className: "app-shell", children: [_jsxs("header", { className: "topbar", children: [_jsxs("div", { className: "brand", children: [_jsx("span", { className: "brand-mark", children: "CL" }), _jsxs("div", { children: [_jsx("strong", { children: "Claude Lab" }), _jsx("span", { children: "Student Lab" })] })] }), _jsx("span", { className: "status-dot", children: "Adaptive learning workspace" })] }), _jsxs("section", { className: "hero", children: [_jsx("p", { className: "eyebrow", children: "STUDENT LAB / LEARNING CONSOLE" }), _jsx("h1", { children: "Build understanding, one focused session at a time." }), _jsx("p", { className: "hero-copy", children: "Study from your course material, practice what needs attention, and let your progress shape the next recommendation." })] }), error && _jsxs("div", { className: "alert error", children: [_jsx("strong", { children: "Something went wrong." }), " ", error] }), busy && _jsx("div", { className: "alert info", children: busy }), screen === "dashboard" && (_jsxs("section", { className: "content-grid", children: [_jsxs("div", { className: "main-column", children: [_jsxs("div", { className: "section-heading", children: [_jsxs("div", { children: [_jsx("p", { className: "eyebrow", children: "OVERVIEW" }), _jsx("h2", { children: "Your progress" })] }), _jsx("button", { className: "text-button", onClick: () => void loadDashboard(), children: "Refresh data" })] }), loading ? _jsx("div", { className: "panel empty", children: "Loading progress..." }) : topicCount === 0 ? _jsxs("div", { className: "panel empty", children: [_jsx("h3", { children: "No practice history yet." }), _jsx("p", { children: "Complete your first practice session to receive adaptive recommendations." })] }) : _jsx("div", { className: "progress-list", children: progressCards.map(([name, item]) => _jsxs("div", { className: "panel progress-row", children: [_jsxs("div", { children: [_jsx("h3", { children: name }), _jsxs("p", { children: [item.attempts, " attempt", item.attempts === 1 ? "" : "s", " \u00B7 ", item.correct, "/", item.total, " correct"] })] }), _jsxs("div", { className: "accuracy", children: [_jsxs("strong", { children: [item.accuracy, "%"] }), _jsx("span", { children: "accuracy" })] })] }, name)) }), _jsxs("div", { className: "metrics", children: [_jsxs("div", { className: "metric", children: [_jsx("span", { children: "Topics practiced" }), _jsx("strong", { children: topicCount })] }), _jsxs("div", { className: "metric", children: [_jsx("span", { children: "Total questions" }), _jsx("strong", { children: totalQuestions })] }), _jsxs("div", { className: "metric", children: [_jsx("span", { children: "Focus areas" }), _jsx("strong", { children: weakTopics.length })] })] })] }), _jsxs("aside", { className: "panel recommendation", children: [_jsx("p", { className: "eyebrow", children: "NEXT BEST STEP" }), _jsx("h2", { children: "Learning recommendation" }), loading ? _jsx("p", { className: "muted", children: "Loading recommendation..." }) : recommendation ? _jsxs(_Fragment, { children: [_jsxs("div", { className: "recommend-topic", children: [recommendation.topic, _jsx("span", { children: recommendation.strategy.level })] }), _jsx("p", { className: "reason", children: recommendation.reason }), _jsxs("div", { className: "detail-grid", children: [_jsxs("div", { children: [_jsx("span", { children: "Current accuracy" }), _jsxs("strong", { children: [recommendation.accuracy, "%"] })] }), _jsxs("div", { children: [_jsx("span", { children: "Difficulty" }), _jsx("strong", { children: recommendation.strategy.difficulty })] }), _jsxs("div", { children: [_jsx("span", { children: "Questions" }), _jsx("strong", { children: recommendation.strategy.questions })] })] }), _jsxs("p", { className: "focus", children: [_jsx("strong", { children: "Focus:" }), " ", recommendation.strategy.focus] }), _jsxs("button", { className: "primary-button", onClick: () => void startLearning(), children: ["Start learning ", _jsx("span", { children: "\u2192" })] })] }) : _jsxs("div", { className: "empty compact", children: [_jsx("h3", { children: "Practice to unlock recommendations." }), _jsx("p", { children: "Your next topic will be selected from your recorded results." })] })] })] })), screen === "topic" && _jsxs("section", { className: "panel reading", children: [_jsx("button", { className: "back-button", onClick: () => setScreen("dashboard"), children: "\u2190 Back to dashboard" }), _jsx("p", { className: "eyebrow", children: "STUDY MATERIAL" }), _jsx("h2", { children: topic }), _jsx("p", { className: "muted", children: "Retrieved from your Claude Lab knowledge base. Use this review before starting practice." }), topicContent.length === 0 ? _jsx("div", { className: "empty", children: _jsx("p", { children: "No study material found for this topic." }) }) : _jsx("div", { className: "source-list", children: topicContent.map((chunk) => _jsxs("article", { className: "source-card", children: [_jsxs("div", { className: "source-label", children: [chunk.source, " \u00B7 Chunk ", chunk.chunk] }), _jsx("p", { children: chunk.text })] }, `${chunk.source}-${chunk.chunk}`)) }), _jsxs("button", { className: "primary-button", onClick: startPractice, children: ["Start practice ", _jsx("span", { children: "\u2192" })] })] }), screen === "quiz" && _jsxs("section", { className: "panel quiz", children: [_jsxs("div", { className: "quiz-top", children: [_jsx("button", { className: "back-button", onClick: () => setScreen("topic"), children: "\u2190 Study material" }), _jsxs("span", { children: ["Question ", questionIndex + 1, " of ", questions.length] })] }), _jsx("div", { className: "progress-bar", children: _jsx("span", { style: { width: `${((questionIndex + 1) / questions.length) * 100}%` } }) }), _jsxs("p", { className: "eyebrow", children: ["PRACTICE / ", topic] }), _jsx("h2", { children: currentQuestion.prompt }), _jsx("div", { className: "options", children: currentQuestion.options.map((option, index) => _jsxs("button", { className: `option ${selected === index ? "selected" : ""}`, onClick: () => setSelected(index), children: [_jsx("span", { children: String.fromCharCode(65 + index) }), option] }, option)) }), _jsxs("button", { className: "primary-button", disabled: selected === null, onClick: answerQuestion, children: [questionIndex === questions.length - 1 ? "See result" : "Next question", " ", _jsx("span", { children: "\u2192" })] })] }), screen === "result" && _jsxs("section", { className: "panel result", children: [_jsx("p", { className: "eyebrow", children: "PRACTICE COMPLETE" }), _jsxs("h2", { children: ["Nice work on ", topic, "."] }), _jsxs("div", { className: "score-ring", children: [_jsxs("strong", { children: [scorePercent, "%"] }), _jsxs("span", { children: [lastScore.correct, " of ", lastScore.total, " correct"] })] }), recorded ? _jsxs(_Fragment, { children: [_jsx("div", { className: "success-box", children: "Result recorded successfully. Your dashboard and recommendation are up to date." }), _jsxs("button", { className: "primary-button", onClick: () => setScreen("dashboard"), children: ["View updated dashboard ", _jsx("span", { children: "\u2192" })] })] }) : _jsxs(_Fragment, { children: [_jsx("p", { className: "muted", children: "Record this session to update your adaptive learning path." }), _jsxs("button", { className: "primary-button", onClick: () => void saveResult(), children: ["Record practice result ", _jsx("span", { children: "\u2192" })] })] })] }), _jsxs("footer", { children: ["Claude Lab \u00B7 Student Lab ", _jsx("span", { children: "Backend-powered adaptive learning" })] })] }));
}
export default App;
