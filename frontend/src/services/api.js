async function request(url, options) {
    const response = await fetch(url, options);
    const payload = (await response.json());
    if (!response.ok) {
        throw new Error(payload.error || "The Claude Lab backend returned an error.");
    }
    return payload;
}
export function getProgress() {
    return request("/api/progress");
}
export function getRecommendation() {
    return request("/api/recommendation");
}
export function getTopic(topic) {
    return request(`/api/topic/${encodeURIComponent(topic)}`);
}
export function recordPractice(topic, correct, total) {
    return request("/api/practice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, correct, total }),
    });
}
