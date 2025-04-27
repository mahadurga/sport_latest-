/**
 * Speech synthesis helper for cricket commentary
 */
class CommentarySpeechSynthesizer {
    constructor() {
        this.synth = window.speechSynthesis;
        this.voices = [];
        this.utterance = null;
        this.commentaryText = '';
        this.isPlaying = false;
        this.sentences = [];
        this.currentSentenceIndex = 0;
        
        // Initialize voices
        this.loadVoices();
        
        // Handle voice loading
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = () => {
                this.loadVoices();
            };
        }

        // Ensure speech synthesis stops when page unloads
        window.addEventListener('unload', () => {
            if (this.synth.speaking) {
                this.synth.cancel();
            }
        });
    }
    
    loadVoices() {
        this.voices = this.synth.getVoices();
        
        if (this.voices.length > 0) {
            // Get all English voices
            let englishVoices = this.voices.filter(voice => 
                voice.lang.includes('en') || voice.lang.includes('ta'));
                
            if (englishVoices.length === 0) {
                englishVoices = [this.voices[0]]; // Fallback to first available voice
            }
            
            // Create small audio test to verify voice works
            const testUtterance = new SpeechSynthesisUtterance('test');
            testUtterance.volume = 0;
            testUtterance.voice = englishVoices[0];
            
            try {
                this.synth.speak(testUtterance);
                console.log("Voice check successful");
            } catch (e) {
                console.warn("Voice test failed, using default voice");
            }
        }
    }
    
    setCommentary(text) {
        this.commentaryText = text;
        this.sentences = this.splitIntoSentences(text);
        this.currentSentenceIndex = 0;
        console.log(`Commentary set with ${this.sentences.length} sentences`);
    }
    
    splitIntoSentences(text) {
        // Split text into sentences for better speech synthesis
        return text.split(/(?<=[.!?])\s+/);
    }
    
    play() {
        if (this.isPlaying) return;
        
        if (this.isPaused) {
            this.resume();
            return;
        }
        
        if (!this.commentaryText) {
            console.warn("No commentary text set");
            return;
        }
        
        this.isPlaying = true;
        this.speakNextSentence();
    }
    
    speakNextSentence() {
        if (this.currentSentenceIndex >= this.sentences.length) {
            this.isPlaying = false;
            this.currentSentenceIndex = 0;
            if (typeof this.onCommentaryEnd === 'function') {
                this.onCommentaryEnd();
            }
            return;
        }
        
        try {
            const sentence = this.sentences[this.currentSentenceIndex];
            if (!sentence || sentence.trim() === '') {
                this.currentSentenceIndex++;
                this.speakNextSentence();
                return;
            }

            this.utterance = new SpeechSynthesisUtterance(sentence);
            
            // Select appropriate voice
            const availableVoices = this.voices.filter(v => v.lang.includes('en') || v.lang.includes('ta'));
            if (availableVoices.length > 0) {
                this.utterance.voice = availableVoices[0];
            }
            
            this.utterance.rate = 0.9;
            this.utterance.pitch = 1.0;
            this.utterance.volume = 1.0;
            
            this.utterance.onend = () => {
                this.currentSentenceIndex++;
                setTimeout(() => this.speakNextSentence(), 100);
            };

            this.utterance.onerror = (event) => {
                console.warn("Speech synthesis error:", event);
                this.currentSentenceIndex++;
                setTimeout(() => this.speakNextSentence(), 100);
            };
            
            this.synth.speak(this.utterance);
        } catch (error) {
            console.error("Speech synthesis error:", error);
            this.currentSentenceIndex++;
            setTimeout(() => this.speakNextSentence(), 100);
        }
        
        this.utterance.onerror = (event) => {
            console.error("Speech synthesis error:", event);
            this.isPlaying = false;
        };
        
        // Highlight current sentence
        this.onSentenceChange(sentence, this.currentSentenceIndex);
        
        // Speak the sentence
        this.synth.speak(this.utterance);
    }
    
    pause() {
        if (!this.isPlaying) return;
        
        this.synth.pause();
        this.isPaused = true;
        this.isPlaying = false;
    }
    
    resume() {
        if (!this.isPaused) return;
        
        this.synth.resume();
        this.isPaused = false;
        this.isPlaying = true;
    }
    
    stop() {
        this.synth.cancel();
        this.isPaused = false;
        this.isPlaying = false;
        this.currentSentenceIndex = 0;
    }
    
    // Callback functions to be overridden
    onSentenceChange(sentence, index) {
        // Override this function to highlight current sentence
    }
    
    onCommentaryEnd() {
        // Override this function for end of commentary behavior
    }
}

// Initialize the player when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Get the commentary text
    const commentaryElement = document.getElementById('commentary-text');
    const commentaryText = commentaryElement ? commentaryElement.textContent.trim() : '';
    
    // Initialize the speech synthesizer if we have commentary
    if (commentaryText) {
        const speechSynthesizer = new CommentarySpeechSynthesizer();
        speechSynthesizer.setCommentary(commentaryText);
        
        // Override callbacks
        speechSynthesizer.onSentenceChange = function(sentence, index) {
            // Create a highlighted version of the text
            const sentences = speechSynthesizer.sentences;
            const highlightedText = sentences.map((s, i) => 
                i === index ? `<span class="highlight-sentence">${s}</span>` : s
            ).join(' ');
            
            // Update the UI with highlighted text
            if (commentaryElement) {
                commentaryElement.innerHTML = highlightedText;
            }
        };
        
        speechSynthesizer.onCommentaryEnd = function() {
            const playButton = document.getElementById('play-commentary');
            if (playButton) {
                playButton.innerHTML = '<i class="bi bi-play-fill"></i> Play Commentary';
                playButton.classList.remove('btn-danger');
                playButton.classList.add('btn-success');
            }
            
            // Reset the commentary text display
            if (commentaryElement) {
                commentaryElement.innerHTML = commentaryText;
            }
        };
        
        // Set up the play button
        const playButton = document.getElementById('play-commentary');
        if (playButton) {
            playButton.addEventListener('click', function() {
                if (speechSynthesizer.isPlaying || speechSynthesizer.isPaused) {
                    speechSynthesizer.stop();
                    playButton.innerHTML = '<i class="bi bi-play-fill"></i> Play Commentary';
                    playButton.classList.remove('btn-danger');
                    playButton.classList.add('btn-success');
                } else {
                    speechSynthesizer.play();
                    playButton.innerHTML = '<i class="bi bi-stop-fill"></i> Stop Commentary';
                    playButton.classList.remove('btn-success');
                    playButton.classList.add('btn-danger');
                }
            });
        }
    }
    
    // Set up the events button to scroll to events section
    const eventsButton = document.getElementById('events-button');
    if (eventsButton) {
        eventsButton.addEventListener('click', function() {
            const eventsSection = document.getElementById('cricket-events');
            if (eventsSection) {
                eventsSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    
    // Populate the events list
    fetch('/api/events')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && data.events) {
                displayEvents(data.events);
            }
        })
        .catch(error => {
            console.error('Error fetching events:', error);
            const eventsContainer = document.getElementById('cricket-events');
            if (eventsContainer) {
                eventsContainer.innerHTML = '<div class="alert alert-warning">Could not load events. Please try again later.</div>';
            }
        });
        
    function displayEvents(events) {
        const eventsContainer = document.getElementById('cricket-events');
        if (!eventsContainer) return;
        
        // Clear loading spinner
        eventsContainer.innerHTML = '';
        
        if (events.length === 0) {
            eventsContainer.innerHTML = '<p class="text-center">No events detected in this video.</p>';
            return;
        }
        
        // Group events by type
        const eventsByType = {};
        events.forEach(event => {
            const type = event.type;
            if (!eventsByType[type]) {
                eventsByType[type] = [];
            }
            eventsByType[type].push(event);
        });
        
        // Create event list
        const eventList = document.createElement('div');
        eventList.className = 'list-group';
        
        for (const type in eventsByType) {
            const typeEvents = eventsByType[type];
            
            // Create type header
            const typeHeader = document.createElement('div');
            typeHeader.className = 'list-group-item list-group-item-dark';
            typeHeader.innerHTML = `<strong>${capitalizeFirstLetter(type)} Events (${typeEvents.length})</strong>`;
            eventList.appendChild(typeHeader);
            
            // Add individual events
            typeEvents.forEach(event => {
                const listItem = document.createElement('div');
                listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                
                // Event description
                const description = document.createElement('div');
                description.innerHTML = `
                    <div><strong>${event.subtype ? capitalizeFirstLetter(event.subtype) : ''}</strong></div>
                    <small class="text-muted">at ${formatTime(event.timestamp)}</small>
                `;
                
                // Jump to event button
                const jumpButton = document.createElement('button');
                jumpButton.className = 'btn btn-sm btn-outline-primary';
                jumpButton.innerHTML = '<i class="bi bi-play-fill"></i>';
                jumpButton.addEventListener('click', () => {
                    const video = document.getElementById('results-video');
                    if (video) {
                        video.currentTime = event.timestamp;
                        video.play().catch(e => console.error("Error playing video:", e));
                    }
                });
                
                listItem.appendChild(description);
                listItem.appendChild(jumpButton);
                eventList.appendChild(listItem);
            });
        }
        
        eventsContainer.appendChild(eventList);
    }
    
    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
    
    function formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        
        const minutes = Math.floor(seconds / 60);
        seconds = Math.floor(seconds % 60);
        return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    }
});