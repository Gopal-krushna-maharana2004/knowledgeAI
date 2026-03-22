document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-assessment-btn');
    const modal = document.getElementById('config-modal');
    const closeBtn = document.getElementById('close-modal');

    if (startBtn) {
        startBtn.onclick = () => modal.style.display = 'flex';
    }
    if (closeBtn) {
        closeBtn.onclick = () => modal.style.display = 'none';
    }

    // Voice Recognition
    const micBtn = document.getElementById('mic-btn');
    const chatInput = document.getElementById('chat-input-field');

    if (micBtn && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        micBtn.onclick = () => {
            if (micBtn.classList.contains('recording')) {
                recognition.stop();
            } else {
                recognition.start();
                micBtn.classList.add('recording');
            }
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            micBtn.classList.remove('recording');
        };

        recognition.onend = () => {
            micBtn.classList.remove('recording');
        };
    }
});

// Chat Logic
const chatBox = document.getElementById('chat-box');
const chatInput = document.getElementById('chat-input-field');
const sendBtn = document.getElementById('send-btn');

if (sendBtn) {
    sendBtn.onclick = () => {
        const text = chatInput.value.trim();
        if (text) {
            appendMessage('user', text);
            chatInput.value = '';
            // Handle bot response logic here
            handleBotInteraction(text);
        }
    };
}

function appendMessage(sender, text) {
    if (!chatBox) return;
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender} fade-in`;
    msgDiv.innerText = text;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function fetchScrapingInfo(topic) {
    try {
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic })
        });
        const data = await response.json();
        return data.summary;
    } catch (e) {
        return "Failed to fetch topic information.";
    }
}

// Initialized by chat.html
window.startAssessmentSession = async (topic, numQ) => {
    appendMessage('bot', `Gathering information about ${topic}...`);
    const summary = await fetchScrapingInfo(topic);
    appendMessage('bot', "Here's what I found:");
    appendMessage('bot', summary);
    
    appendMessage('bot', `Fetching ${numQ} questions for your assessment...`);
    const questionsResponse = await fetch('/api/get_questions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, num_questions: numQ })
    });
    const qData = await questionsResponse.json();
    
    // Start Quiz State
    window.quizState = {
        topic: topic,
        total: parseInt(numQ),
        current: 0,
        score: 0,
        questions: qData.questions || []
    };
    
    if (window.quizState.questions.length === 0) {
        appendMessage('bot', "Sorry, I couldn't find any questions for this topic.");
        return;
    }

    appendMessage('bot', `Great! Let's start the ${window.quizState.questions.length} question assessment.`);
    setTimeout(() => askNextQuestion(), 1500);
};

function askNextQuestion() {
    const state = window.quizState;
    if (state.current < state.questions.length) {
        const questionObj = state.questions[state.current];
        appendMessage('bot', `Question ${state.current + 1}: ${questionObj.q}`);
    } else {
        finishQuiz();
    }
}

async function handleBotInteraction(userText) {
    const state = window.quizState;
    if (!state) return;

    const currentQuestion = state.questions[state.current];
    
    appendMessage('bot', "Validating your answer...");
    
    try {
        const response = await fetch('/api/validate_answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: currentQuestion.q,
                user_answer: userText,
                expected_answer: currentQuestion.a
            })
        });
        
        const data = await response.json();
        
        if (data.is_correct) {
            state.score++;
            appendMessage('bot', data.feedback || "Correct! Excellent work.");
        } else {
            appendMessage('bot', data.feedback || `Not quite. The correct answer was: ${currentQuestion.a}`);
        }
    } catch (e) {
        console.error("Validation failed", e);
        // Fallback to basic match
        const correctAnswer = currentQuestion.a.toLowerCase();
        const userAnswer = userText.toLowerCase();
        if (userAnswer.includes(correctAnswer) || correctAnswer.includes(userAnswer)) {
            state.score++;
            appendMessage('bot', "Correct! (Fallback validation)");
        } else {
            appendMessage('bot', `Incorrect. The correct answer was: ${currentQuestion.a}`);
        }
    }

    state.current++;
    setTimeout(() => askNextQuestion(), 1500);
}

async function finishQuiz() {
    const state = window.quizState;
    appendMessage('bot', `Assessment Complete! Your knowledge score: ${state.score} / ${state.total}`);
    
    // Save to history
    try {
        await fetch('/api/save_history', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                subject: "Mixed", // Could be passed from template
                topic: state.topic,
                score: state.score,
                total_questions: state.total
            })
        });
        appendMessage('bot', "History saved. You can view it in your dashboard.");
    } catch (e) {
        console.error("Failed to save history", e);
    }
}
