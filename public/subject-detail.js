function getQueryParam(param) {
    const params = new URLSearchParams(window.location.search);
    return params.get(param);
}

const subjectContent = {
    Mathematics: {
        topics: ['Algebra', 'Geometry', 'Trigonometry', 'Calculus', 'Statistics'],
        note: 'Review class notes and practice previous exam questions. Focus on formula derivations and example problems.',
        tips: ['Practice every day', 'Work through sample papers', 'Study with a friend', 'Understand the formula meaning'],
        images: ['Graph of functions', 'Geometry diagrams', 'Equation examples']
    },
    English: {
        topics: ['Comprehension', 'Grammar', 'Writing', 'Literature', 'Vocabulary'],
        note: 'Read widely and practice writing short essays. Use past papers to help structure answers clearly.',
        tips: ['Read every day', 'Write summaries', 'Practice grammar exercises', 'Learn key literary devices'],
        images: ['Reading passages', 'Essay plan', 'Grammar chart']
    },
    Biology: {
        topics: ['Cell Biology', 'Genetics', 'Ecology', 'Human Anatomy', 'Evolution'],
        note: 'Draw diagrams and label them accurately. Understand processes step-by-step instead of memorizing alone.',
        tips: ['Use colour diagrams', 'Explain processes aloud', 'Compare systems', 'Practice with past paper diagrams'],
        images: ['Cell diagram', 'Food chain', 'Human body systems']
    },
    Chemistry: {
        topics: ['Atoms and Molecules', 'Chemical Equations', 'Acids and Bases', 'Organic Chemistry', 'Stoichiometry'],
        note: 'Balance equations carefully and practice naming compounds. Pay attention to trends in the periodic table.',
        tips: ['Memorise common ions', 'Practice balancing equations', 'Understand reaction types', 'Work through numerical problems'],
        images: ['Molecular structures', 'Reaction diagrams', 'Periodic table examples']
    },
    Physics: {
        topics: ['Mechanics', 'Waves', 'Electricity', 'Optics', 'Energy'],
        note: 'Practice solving problems from first principles and use correct units. Focus on understanding formula derivations.',
        tips: ['Draw diagrams', 'Write down given values', 'Practice calculations', 'Use formulas consistently'],
        images: ['Free body diagrams', 'Circuit examples', 'Wave graphs']
    }
};

function renderSubject() {
    const subject = getQueryParam('subject') || 'Mathematics';
    const className = getQueryParam('class') || '';
    const data = subjectContent[subject] || subjectContent['Mathematics'];

    document.getElementById('subjectTitle').textContent = subject;
    document.getElementById('subjectSubtitle').textContent = `Selected subject: ${subject}`;

    document.getElementById('subjectTopics').innerHTML = `
        <h3>Topics</h3>
        <ul>${data.topics.map(topic => `<li>${topic}</li>`).join('')}</ul>
    `;

    document.getElementById('subjectResources').innerHTML = `
        <h3>Resources</h3>
        <p><strong>Notes:</strong> ${data.note}</p>
        <p><strong>Flashcards:</strong></p>
        <ul>${data.topics.map(topic => `<li>${topic} flashcards available</li>`).join('')}</ul>
        <p><strong>Images and charts:</strong> ${data.images.join(', ')}</p>
        <p><strong>Learning tips:</strong></p>
        <ul>${data.tips.map(tip => `<li>${tip}</li>`).join('')}</ul>
        <div id="subjectNotes">
            <h3>Downloadable Notes</h3>
            <p>Loading notes...</p>
        </div>
    `;

    loadSubjectNotes(subject, className);
}

async function loadSubjectNotes(subject, className = '') {
    const notesContainer = document.getElementById('subjectNotes');
    if (!notesContainer) return;

    try {
        const endpoint = className
            ? `/api/notes/class/${encodeURIComponent(className)}/${encodeURIComponent(subject)}`
            : `/api/notes/${encodeURIComponent(subject)}`;
        const res = await fetch(endpoint);
        const data = await res.json();

        if (!data.success) {
            notesContainer.innerHTML = `<p>No notes available for ${subject} yet.</p>`;
            return;
        }

        if (!data.notes || data.notes.length === 0) {
            notesContainer.innerHTML = `<p>No notes available for ${subject} yet.</p>`;
            return;
        }

        const basePath = className
            ? `/notes/${encodeURIComponent(className)}/${encodeURIComponent(subject)}`
            : `/api/notes/${encodeURIComponent(subject)}`;

        notesContainer.innerHTML = `
            <ul>
                ${data.notes.map(note => `<li><a href="${basePath}/${encodeURIComponent(note.file)}" target="_blank">${note.displayName}</a></li>`).join('')}
            </ul>
        `;
    } catch (error) {
        console.error('Error loading subject notes:', error);
        notesContainer.innerHTML = `<p>Failed to load notes for ${subject}.</p>`;
    }
}

window.addEventListener('load', renderSubject);
