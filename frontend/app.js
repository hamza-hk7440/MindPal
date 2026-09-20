/* global React, ReactDOM, window */

const { useEffect, useRef, useState } = React;
const h = React.createElement;

const DEMO_USER_ID = "0b4f9248-2c8f-4b70-9d1f-7d64c6f7a77a";

const starterPrompt = "Explain the lesson in simple words.";

const starterQuiz = {
  code: "quick-practice-quiz",
  title: "Quick Practice Quiz",
  description: "A short quiz to help students check what they remember.",
  questions: [
    {
      id: "q1",
      prompt: "What helps you understand a lesson better?",
      choices: [
        { id: "a", label: "Reading the summary first" },
        { id: "b", label: "Ignoring the topic" },
        { id: "c", label: "Guessing randomly" },
      ],
      answer: "a",
      explanation: "A summary helps you see the main idea before details.",
    },
    {
      id: "q2",
      prompt: "What should you do after studying a few notes?",
      choices: [
        { id: "a", label: "Try a practice question" },
        { id: "b", label: "Stop reviewing forever" },
        { id: "c", label: "Forget the topic" },
      ],
      answer: "a",
      explanation: "A practice question checks if the idea really makes sense.",
    },
    {
      id: "q3",
      prompt: "What is a good way to prepare for class?",
      choices: [
        { id: "a", label: "Review your notes a little each day" },
        { id: "b", label: "Never look again" },
        { id: "c", label: "Wait until the last minute" },
      ],
      answer: "a",
      explanation: "Small reviews over time are easier to remember.",
    },
  ],
};

function normalizeApiBase(value) {
  return (value || "http://localhost:8000/api/v1").replace(/\/$/, "");
}

function buildUrl(base, path) {
  return `${normalizeApiBase(base)}${path.startsWith("/") ? path : `/${path}`}`;
}

function buildWebSocketUrl(base, path) {
  const normalizedBase = normalizeApiBase(base);
  const wsBase = normalizedBase.startsWith("https://")
    ? normalizedBase.replace("https://", "wss://")
    : normalizedBase.replace("http://", "ws://");
  return `${wsBase}${path.startsWith("/") ? path : `/${path}`}`;
}

async function requestJson(base, path, options = {}) {
  const response = await fetch(buildUrl(base, path), {
    headers: {
      Accept: "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function useLocalStorageState(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      const stored = window.localStorage.getItem(key);
      return stored === null ? initialValue : stored;
    } catch (_error) {
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(key, value);
    } catch (_error) {
      // Ignore storage limits in restricted environments.
    }
  }, [key, value]);

  return [value, setValue];
}

function Pill({ children, tone = "neutral" }) {
  return h("span", { className: `status-pill ${tone}`.trim() }, children);
}

function Field({ label, hint, children }) {
  return h(
    "div",
    { className: "field" },
    h("label", null, label),
    children,
    hint ? h("div", { className: "hint" }, hint) : null,
  );
}

function renderInlineMarkdown(text, keyPrefix) {
  return String(text)
    .split(/(\*\*[^*]+\*\*)/g)
    .filter(Boolean)
    .map((part, index) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return h("strong", { key: `${keyPrefix}-strong-${index}` }, part.slice(2, -2));
      }

      return part;
    });
}

function renderMessageContent(content) {
  const normalized = String(content || "").replace(/\r\n/g, "\n").trim();

  if (!normalized) {
    return h("div", { className: "message-content" });
  }

  const blocks = normalized.split(/\n{2,}/);

  return h(
    "div",
    { className: "message-content" },
    blocks.map((block, blockIndex) => {
      const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
      const listItems = lines
        .map((line) => line.match(/^[-*]\s+(.+)$/) || line.match(/^\d+[.)]\s+(.+)$/))
        .filter(Boolean);

      if (listItems.length === lines.length && lines.length > 1) {
        return h(
          "ul",
          { key: `block-${blockIndex}` },
          listItems.map((match, itemIndex) =>
            h("li", { key: `item-${itemIndex}` }, renderInlineMarkdown(match[1], `block-${blockIndex}-item-${itemIndex}`)),
          ),
        );
      }

      if (lines.length === 1 && /^#{1,3}\s+/.test(lines[0])) {
        return h(
          "h4",
          { key: `block-${blockIndex}` },
          renderInlineMarkdown(lines[0].replace(/^#{1,3}\s+/, ""), `block-${blockIndex}`),
        );
      }

      return h(
        "p",
        { key: `block-${blockIndex}` },
        lines.map((line, lineIndex) => [
          lineIndex > 0 ? h("br", { key: `br-${lineIndex}` }) : null,
          ...renderInlineMarkdown(line, `block-${blockIndex}-line-${lineIndex}`),
        ]),
      );
    }),
  );
}

function SectionHeader({ eyebrow, title, copy, action }) {
  return h(
    "div",
    { className: "section-header" },
    h(
      "div",
      null,
      eyebrow ? h("div", { className: "eyebrow" }, eyebrow) : null,
      h("h2", { className: "section-title" }, title),
      h("p", { className: "section-copy" }, copy),
    ),
    action || null,
  );
}

function Sidebar({ active, onChange, subjectCount, noteCount }) {
  const sections = [
    { id: "home", title: "Home", description: "Start here" },
    { id: "subjects", title: "Study Subjects", description: "Create a topic" },
    { id: "upload", title: "Upload Documents", description: "Add files for a topic" },
    { id: "chat", title: "Chat", description: "Talk about the selected topic" },
    { id: "quiz", title: "Practice Quiz", description: "Test what you know" },
  ];

  return h(
    "aside",
    { className: "sidebar" },
    h(
      "div",
      { className: "brand" },
      h("div", { className: "brand-mark" }, "MP"),
      h(
        "div",
        null,
        h("h1", { className: "brand-name" }, "MindPal"),
        h("p", { className: "brand-copy" }, "Create a study subject, add your documents, then chat with your notes."),
      ),
    ),
    h(
      "ul",
      { className: "nav-list" },
      sections.map((item) =>
        h(
          "li",
          { key: item.id },
          h(
            "button",
            {
              className: `nav-button ${active === item.id ? "active" : ""}`,
              onClick: () => onChange(item.id),
              type: "button",
            },
            h(
              "span",
              { className: "nav-label" },
              h("strong", null, item.title),
              h("span", null, item.description),
            ),
            h("span", null, ">"),
          ),
        ),
      ),
    ),
    h(
      "div",
      { className: "sidebar-panel" },
      h("h3", null, "Your workspace"),
      h("p", null, `You have ${subjectCount} study subject${subjectCount === 1 ? "" : "s"} and ${noteCount} note${noteCount === 1 ? "" : "s"}.`),
      h(
        "div",
        { className: "chip-row" },
        h(Pill, { tone: "success" }, "Simple"),
        h(Pill, { tone: "warning" }, "Student-first"),
      ),
    ),
  );
}

function Hero({ onJump }) {
  return h(
    "section",
    { className: "section" },
    h(
      "div",
      { className: "hero" },
      h("span", { className: "eyebrow" }, "Student study space"),
      h(
        "div",
        { className: "hero-grid" },
        h(
          "div",
          null,
          h("h1", null, "Study by subject, not by noise."),
          h(
            "p",
            null,
            "MindPal is built for a simple flow: make a study subject, upload the documents for that subject, and then chat with the material in one place.",
          ),
          h(
            "div",
            { className: "hero-actions" },
            h("button", { className: "primary-button", type: "button", onClick: () => onJump("subjects") }, "Create a subject"),
            h("button", { className: "secondary-button", type: "button", onClick: () => onJump("upload") }, "Upload documents"),
            h("button", { className: "ghost-button", type: "button", onClick: () => onJump("chat") }, "Start chat"),
            h("button", { className: "ghost-button", type: "button", onClick: () => onJump("quiz") }, "Practice quiz"),
          ),
        ),
        h(
          "div",
          { className: "hero-card-stack" },
          h(
            "div",
            { className: "glass-card" },
            h("h3", { style: { marginTop: 0 } }, "How it works"),
            h(
              "div",
              { className: "data-list" },
              h("div", { className: "data-card" }, h("strong", null, "1. Create a subject"), h("div", { className: "hint" }, "Example: Biology, Geometry, World History.")),
              h("div", { className: "data-card" }, h("strong", null, "2. Add documents"), h("div", { className: "hint" }, "Upload PDFs, files, or links for that subject.")),
              h("div", { className: "data-card" }, h("strong", null, "3. Chat with the subject"), h("div", { className: "hint" }, "Ask for summaries, explanations, and practice questions.")),
            ),
          ),
        ),
      ),
    ),
  );
}

function SubjectsSection({ apiBase, subjects, setSubjects, selectedSubjectId, setSelectedSubjectId }) {
  const [subjectName, setSubjectName] = useState("Biology");
  const [subjectNote, setSubjectNote] = useState("A subject for class notes and exam review.");

  async function createSubject() {
    try {
      const created = await requestJson(apiBase, "/ingestion/study-subjects/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: subjectName, user_id: DEMO_USER_ID }),
      });
      const normalized = { id: created.id, name: created.name, note: subjectNote };
      setSubjects((current) => [normalized, ...current.filter((item) => item.id !== normalized.id)]);
      setSelectedSubjectId(normalized.id);
    } catch (_error) {
      window.alert("Could not create the subject. Please check that the backend is running and try again.");
    }
  }

  return h(
    "section",
    { className: "section" },
    h(SectionHeader, {
      eyebrow: "Step 1",
      title: "Create a study subject",
      copy: "Start by making one subject for each class or topic. This keeps your notes and chat organized.",
      action: h(Pill, { tone: "success" }, `${subjects.length} saved`),
    }),
    h(
      "div",
      { className: "surface-grid" },
      h(
        "div",
        { className: "panel span-6" },
        h("h3", null, "New subject"),
        h(Field, { label: "Subject name", hint: "Example: Biology or Algebra." }, h("input", { value: subjectName, onChange: (event) => setSubjectName(event.target.value) })),
        h(Field, { label: "Small note", hint: "Optional reminder about what this subject is for." }, h("textarea", { value: subjectNote, onChange: (event) => setSubjectNote(event.target.value) })),
        h("div", { className: "action-row" }, h("button", { className: "primary-button", type: "button", onClick: createSubject }, "Save subject")),
      ),
      h(
        "div",
        { className: "panel span-6" },
        h("h3", null, "Your subjects"),
        h(
          "div",
          { className: "data-list" },
          subjects.length
            ? subjects.map((subject) =>
                h(
                  "button",
                  {
                    key: subject.id,
                    type: "button",
                    className: `data-card subject-card ${selectedSubjectId === subject.id ? "selected" : ""}`,
                    onClick: () => setSelectedSubjectId(subject.id),
                  },
                  h("strong", null, subject.name),
                  h("div", { className: "hint" }, subject.note || "Tap to open this subject."),
                ),
              )
            : h("div", { className: "hint" }, "Create your first subject to get started."),
        ),
      ),
    ),
  );
}

function UploadSection({ apiBase, subjects, selectedSubjectId, setSelectedSubjectId, notesBySubject, setNotesBySubject }) {
  const selectedSubject = subjects.find((subject) => subject.id === selectedSubjectId) || subjects[0];
  const [title, setTitle] = useState("Chapter 1 Notes");
  const [fileName, setFileName] = useState("");
  const [link, setLink] = useState("");
  const [summary, setSummary] = useState("Key ideas from the chapter.");
  const [file, setFile] = useState(null);

  async function uploadDocument() {
    if (!selectedSubject) {
      return;
    }

    const formData = new FormData();
    formData.append("subject_id", selectedSubject.id);
    formData.append("title", title);
    formData.append("doc_url", link);
    if (file) {
      formData.append("file", file);
    }

    try {
      const response = await fetch(buildUrl(apiBase, "/ingestion/resources/"), {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Upload failed");
      }

      await response.json();
      setNotesBySubject((current) => ({
        ...current,
        [selectedSubject.id]: [
          { title, summary, source: fileName || link || "Uploaded file" },
          ...(current[selectedSubject.id] || []),
        ],
      }));
    } catch (_error) {
      window.alert("Upload failed. The document was not saved, so chat cannot use it yet.");
    }
  }

  return h(
    "section",
    { className: "section" },
    h(SectionHeader, {
      eyebrow: "Step 2",
      title: "Upload the documents for that subject",
      copy: "Add the notes, slides, or files that belong to the subject you created. Keep one topic per subject.",
      action: h(Pill, { tone: selectedSubject ? "success" : "warning" }, selectedSubject ? selectedSubject.name : "No subject selected"),
    }),
    h(
      "div",
      { className: "surface-grid" },
      h(
        "div",
        { className: "panel span-6" },
        h("h3", null, "Upload document"),
        h(
          Field,
          { label: "Subject", hint: "Pick the subject this file belongs to." },
          h(
            "select",
            {
              value: selectedSubject ? selectedSubject.id : "",
              onChange: (event) => setSelectedSubjectId(event.target.value),
            },
            subjects.map((subject) => h("option", { value: subject.id, key: subject.id }, subject.name)),
          ),
        ),
        h(Field, { label: "Document title" }, h("input", { value: title, onChange: (event) => setTitle(event.target.value) })),
        h(Field, { label: "Choose a file", hint: "You can upload a PDF or document directly." }, h("input", { type: "file", onChange: (event) => { const nextFile = event.target.files && event.target.files[0] ? event.target.files[0] : null; setFile(nextFile); setFileName(nextFile ? nextFile.name : ""); } })),
        h(Field, { label: "File name or link", hint: "If you do not choose a file, you can paste a link instead." }, h("input", { value: fileName || link, onChange: (event) => { setFileName(event.target.value); setLink(event.target.value); }, placeholder: "Paste a link to a document" })),
        h(Field, { label: "Short summary" }, h("textarea", { value: summary, onChange: (event) => setSummary(event.target.value) })),
        h("div", { className: "action-row" }, h("button", { className: "primary-button", type: "button", onClick: uploadDocument }, "Save document")),
      ),
      h(
        "div",
        { className: "panel span-6" },
        h("h3", null, selectedSubject ? `${selectedSubject.name} notes` : "Saved notes"),
        h(
          "div",
          { className: "data-list" },
          selectedSubject && notesBySubject[selectedSubject.id] && notesBySubject[selectedSubject.id].length
            ? notesBySubject[selectedSubject.id].map((note, index) =>
                h(
                  "div",
                  { className: "data-card", key: `${note.title}-${index}` },
                  h("strong", null, note.title),
                  h("div", { className: "hint" }, note.summary),
                  h("div", { className: "hint" }, note.source),
                ),
              )
            : h("div", { className: "hint" }, "Upload a document for this subject and it will appear here."),
        ),
      ),
    ),
  );
}

function ChatSection({ apiBase, subjects, selectedSubjectId }) {
  const selectedSubject = subjects.find((subject) => subject.id === selectedSubjectId) || subjects[0];
  const [conversationId, setConversationId] = useState("");
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Pick a subject and start asking questions about the documents you uploaded." },
  ]);
  const [draft, setDraft] = useState(starterPrompt);
  const [status, setStatus] = useState("Choose a subject to begin.");
  const socketRef = useRef(null);

  useEffect(() => {
    setConversationId("");
    setMessages([{ role: "assistant", content: "Pick a subject and start asking questions about the documents you uploaded." }]);
    setStatus(selectedSubject ? `Ready for ${selectedSubject.name}. Press Start chat.` : "Create a subject to begin.");
  }, [selectedSubjectId]);

  useEffect(() => {
    if (!conversationId) {
      return undefined;
    }

    let cancelled = false;
    requestJson(apiBase, `/messages/${conversationId}`)
      .then((data) => {
        if (!cancelled && Array.isArray(data) && data.length) {
          setMessages(data.map((item) => ({ role: item.sender || item.sender_role || "assistant", content: item.content })));
        }
      })
      .catch(() => {
        if (!cancelled) {
          setStatus("Showing the sample chat view.");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [apiBase, conversationId]);

  useEffect(() => {
    if (!conversationId) {
      return undefined;
    }

    try {
      const socket = new WebSocket(buildWebSocketUrl(apiBase, `/messages/ws/${conversationId}`));
      socketRef.current = socket;

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.event === "status") {
            setStatus(payload.message);
            return;
          }
          if (payload.event === "token_delta") {
            setMessages((current) => {
              const next = current.slice();
              const last = next[next.length - 1];
              if (last && last.role === "assistant" && last.streaming) {
                last.content += payload.text;
                return next;
              }
              next.push({ role: "assistant", content: payload.text, streaming: true });
              return next;
            });
            return;
          }
          if (payload.event === "generation_finished") {
            setMessages((current) => current.map((item) => (item.streaming ? { ...item, streaming: false } : item)));
            setStatus("Answer ready.");
            return;
          }
          if (payload.event === "error") {
            setMessages((current) => [
              ...current,
              {
                role: "assistant",
                content: `**Chat error**\n\n${payload.message || "The tutor could not generate a response right now."}`,
              },
            ]);
            setStatus("Chat error.");
          }
        } catch (_error) {
          // Ignore malformed socket messages.
        }
      };

      socket.onerror = () => setStatus("Chat connection is unavailable right now. You can still type locally.");

      return () => {
        socket.close();
        socketRef.current = null;
      };
    } catch (_error) {
      return undefined;
    }
  }, [apiBase, conversationId]);

  async function startConversation() {
    if (!selectedSubject) {
      setStatus("Create a subject first.");
      return;
    }

    try {
      const response = await requestJson(apiBase, "/conversations/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject_id: selectedSubject.id }),
      });
      setConversationId(response.id);
      setStatus(`Chat started for ${selectedSubject.name}.`);
    } catch (_error) {
      setConversationId("");
      setStatus("Could not start chat. Please select a real saved subject first.");
    }
  }

  async function sendMessage() {
    if (!draft.trim()) {
      return;
    }

    setMessages((current) => [...current, { role: "user", content: draft }]);

    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ content: draft }));
      setDraft(starterPrompt);
      return;
    }

    setMessages((current) => [...current, { role: "assistant", content: "**Chat not started**\n\nPress Start chat before sending a message." }]);
    setDraft(starterPrompt);
  }

  return h(
    "section",
    { className: "section" },
    h(SectionHeader, {
      eyebrow: "Step 3",
      title: "Chat inside your subject",
      copy: "Choose the subject, open chat, and ask questions about the documents you uploaded for that topic.",
      action: h(Pill, { tone: selectedSubject ? "success" : "warning" }, selectedSubject ? selectedSubject.name : "No subject"),
    }),
    h(
      "div",
      { className: "surface-grid" },
      h(
        "div",
        { className: "panel span-6" },
        h("h3", null, "Open chat"),
        h(
          Field,
          { label: "Selected subject", hint: "Chat always follows the subject you choose." },
          h(
            "input",
            {
              value: selectedSubject ? selectedSubject.name : "",
              readOnly: true,
            },
          ),
        ),
        h("div", { className: "action-row" }, h("button", { className: "primary-button", type: "button", onClick: startConversation }, "Start chat")),
        h("div", { className: "hint", style: { marginTop: "12px" } }, status),
      ),
      h(
        "div",
        { className: "panel span-6" },
        h("h3", null, "Ask something"),
        h(Field, { label: "Your message", hint: "Examples: summarize this subject, explain the lesson, make practice questions." }, h("textarea", { value: draft, onChange: (event) => setDraft(event.target.value) })),
        h("div", { className: "action-row" }, h("button", { className: "primary-button", type: "button", onClick: sendMessage }, "Send message")),
      ),
      h(
        "div",
        { className: "panel span-12" },
        h("h3", null, "Conversation"),
        h(
          "div",
          { className: "chat-stream" },
          messages.map((message, index) =>
            h(
              "div",
              { className: `bubble ${message.role === "user" ? "user" : "assistant"}`, key: `${index}-${message.content.slice(0, 12)}` },
              h("div", { className: "bubble-meta" }, h("span", null, message.role === "user" ? "You" : "Tutor")),
              renderMessageContent(message.content),
            ),
          ),
        ),
      ),
    ),
  );
}

function QuizSection({ apiBase, subjects, selectedSubjectId }) {
  const selectedSubject = subjects.find((subject) => subject.id === selectedSubjectId) || subjects[0];
  const [quiz, setQuiz] = useState(starterQuiz);
  const [answers, setAnswers] = useState(() => {
    const initial = {};
    starterQuiz.questions.forEach((question) => {
      initial[question.id] = question.answer;
    });
    return initial;
  });
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("Choose a subject, then try a short quiz.");

  useEffect(() => {
    let cancelled = false;

    requestJson(apiBase, "/assessment/quiz/quizzes")
      .then((data) => {
        if (cancelled || !Array.isArray(data) || !data.length) {
          return null;
        }
        return requestJson(apiBase, `/assessment/quiz/quizzes/${data[0].code}`);
      })
      .then((data) => {
        if (cancelled || !data || !Array.isArray(data.questions) || !data.questions.length) {
          return;
        }

        setQuiz({
          code: data.code || starterQuiz.code,
          title: "Quick Practice Quiz",
          description: "A short quiz to help students check what they remember.",
          questions: data.questions.map((question, index) => ({
            id: question.id || `q${index + 1}`,
            prompt: question.prompt || question.question || `Question ${index + 1}`,
            choices: Array.isArray(question.choices)
              ? question.choices.map((choice, choiceIndex) => ({
                  id: choice.id || String.fromCharCode(97 + choiceIndex),
                  label: choice.label || choice.text || String(choice),
                }))
              : starterQuiz.questions[index % starterQuiz.questions.length].choices,
            answer: question.answer || question.correct_answer || starterQuiz.questions[index % starterQuiz.questions.length].answer,
            explanation: question.explanation || "Review the lesson and try again.",
          })),
        });

        const nextAnswers = {};
        data.questions.forEach((question, index) => {
          nextAnswers[question.id || `q${index + 1}`] = question.answer || question.correct_answer || "a";
        });
        setAnswers(nextAnswers);
        setStatus("Loaded the quiz from the server.");
      })
      .catch(() => {
        if (!cancelled) {
          setQuiz(starterQuiz);
          setStatus("Using the sample quiz.");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [apiBase]);

  async function submitQuiz() {
    try {
      const payload = await requestJson(apiBase, `/assessment/quiz/quizzes/${quiz.code}/attempts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers }),
      });
      setResult(payload);
      setStatus("Quiz scored.");
    } catch (_error) {
      const score = quiz.questions.filter((question) => answers[question.id] === question.answer).length;
      setResult({ quiz_code: quiz.code, score, total: quiz.questions.length, passed: score === quiz.questions.length, feedback: [] });
      setStatus("Quiz scored using the sample mode.");
    }
  }

  return h(
    "section",
    { className: "section" },
    h(SectionHeader, {
      eyebrow: "Step 4",
      title: "Practice quiz",
      copy: selectedSubject
        ? `Check what you remember for ${selectedSubject.name}.`
        : "Check what you remember with a short practice quiz.",
      action: h(Pill, { tone: "success" }, selectedSubject ? selectedSubject.name : "Practice"),
    }),
    h(
      "div",
      { className: "surface-grid" },
      h(
        "div",
        { className: "panel span-7" },
        h("h3", null, quiz.title),
        h("p", null, quiz.description),
        quiz.questions.map((question, index) =>
          h(
            "div",
            { className: "data-card", key: question.id || index, style: { marginTop: "12px" } },
            h("strong", null, question.prompt),
            h(
              "div",
              { className: "field", style: { marginTop: "10px" } },
              h(
                "select",
                {
                  value: answers[question.id] || "",
                  onChange: (event) => setAnswers((current) => ({ ...current, [question.id]: event.target.value })),
                },
                question.choices.map((choice) => h("option", { value: choice.id, key: choice.id }, choice.label)),
              ),
            ),
          ),
        ),
        h("div", { className: "action-row" }, h("button", { className: "primary-button", type: "button", onClick: submitQuiz }, "Check answers")),
        h("div", { className: "hint", style: { marginTop: "12px" } }, status),
      ),
      h(
        "div",
        { className: "panel span-5" },
        h("h3", null, "Your result"),
        result
          ? h(
              "div",
              { className: "score-grid" },
              h("div", { className: "score-box" }, h("strong", null, `${result.score}/${result.total}`), h("span", null, "score")),
              h("div", { className: "score-box" }, h("strong", null, result.passed ? "Great job" : "Keep trying"), h("span", null, "result")),
              h("div", { className: "score-box" }, h("strong", null, quiz.title), h("span", null, "quiz")),
              h("div", { className: "score-box" }, h("strong", null, selectedSubject ? selectedSubject.name : "Any subject"), h("span", null, "subject")),
            )
          : h("div", { className: "hint" }, "Finish the quiz and press the button to see your score."),
      ),
    ),
  );
}

function App() {
  const [apiBase, setApiBase] = useLocalStorageState("mindpal-api-base", window.MINDPAL_API_BASE || "http://localhost:8000/api/v1");
  const [active, setActive] = useState("home");
  const [subjects, setSubjects] = useState([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState("");
  const [notesBySubject, setNotesBySubject] = useState({});

  useEffect(() => {
    window.MINDPAL_API_BASE = normalizeApiBase(apiBase);
  }, [apiBase]);

  useEffect(() => {
    let cancelled = false;

    requestJson(apiBase, `/ingestion/study-subjects/?user_id=${DEMO_USER_ID}`)
      .then((data) => {
        if (cancelled) {
          return;
        }

        const normalized = Array.isArray(data)
          ? data.map((item) => ({ id: item.id, name: item.name, note: "" }))
          : [];

        setSubjects(normalized);
        setSelectedSubjectId((current) => (normalized.some((subject) => subject.id === current) ? current : normalized[0]?.id || ""));
      })
      .catch(() => {
        if (cancelled) {
          return;
        }

        setSubjects([]);
        setSelectedSubjectId("");
      });

    return () => {
      cancelled = true;
    };
  }, [apiBase]);

  useEffect(() => {
    if (!selectedSubjectId || !subjects.length) {
      return undefined;
    }

    let cancelled = false;

    requestJson(apiBase, `/ingestion/resources/?study_subject_id=${selectedSubjectId}`)
      .then((data) => {
        if (cancelled) {
          return;
        }

        if (Array.isArray(data) && data.length) {
          setNotesBySubject((current) => ({
            ...current,
            [selectedSubjectId]: data.map((item) => ({
              title: item.title,
              summary: item.content || "",
              source: item.doc_url || item.doc_type || "Saved document",
            })),
          }));
        }
      })
      .catch(() => {
        if (cancelled) {
          return;
        }

        setNotesBySubject((current) => ({
          ...current,
          [selectedSubjectId]: current[selectedSubjectId] || [],
        }));
      });

    return () => {
      cancelled = true;
    };
  }, [apiBase, selectedSubjectId, subjects.length]);

  const subjectCount = subjects.length;
  const noteCount = Object.values(notesBySubject).reduce((total, items) => total + items.length, 0);
  const selectedSubject = subjects.find((subject) => subject.id === selectedSubjectId) || subjects[0] || null;

  const content =
    active === "subjects"
      ? h(SubjectsSection, { apiBase, subjects, setSubjects, selectedSubjectId, setSelectedSubjectId })
      : active === "upload"
        ? h(UploadSection, { apiBase, subjects, selectedSubjectId, setSelectedSubjectId, notesBySubject, setNotesBySubject })
        : active === "chat"
          ? h(ChatSection, { apiBase, subjects, selectedSubjectId })
          : active === "quiz"
            ? h(QuizSection, { apiBase, subjects, selectedSubjectId })
          : h(Hero, { onJump: setActive });

  return h(
    "div",
    { className: "app-shell" },
    h(Sidebar, { active, onChange: setActive, subjectCount, noteCount }),
    h(
      "main",
      { className: "main" },
      h(
        "div",
        { className: "section", style: { marginBottom: 0 } },
        h("div", { className: "chip-row" }, h(Pill, { tone: "success" }, "Student-focused"), h(Pill, { tone: "warning" }, selectedSubject ? `Current subject: ${selectedSubject.name}` : "No subject chosen")),
      ),
      content,
      h(
        "div",
        { className: "footer" },
        "Create a subject, add the right documents, and then chat about that exact subject.",
      ),
    ),
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(h(App));
