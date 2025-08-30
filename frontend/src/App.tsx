import { useRef, useState, useEffect } from "react";
import "./App.scss";
import { LiveAPIProvider } from "./contexts/LiveAPIContext";
import SidePanel from "./components/side-panel/SidePanel";
import MediaMixerDisplay from "./components/media-mixer-display/MediaMixerDisplay";
import ScratchpadCapture from "./components/scratchpad-capture/ScratchpadCapture";
import SherlockED from "./components/SherlockED/SherlockED";
import ControlTray from "./components/control-tray/ControlTray";
import { LiveClientOptions, Question } from "./types";
import Scratchpad from "./components/scratchpad/Scratchpad";
import Logger from "./components/logger/Logger";

const API_KEY = process.env.REACT_APP_GEMINI_API_KEY as string;
if (typeof API_KEY !== "string") {
  throw new Error("set REACT_APP_GEMINI_API_KEY in .env");
}

const apiOptions: LiveClientOptions = {
  apiKey: API_KEY,
};

function App() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const renderCanvasRef = useRef<HTMLCanvasElement>(null);
  const [videoStream, setVideoStream] = useState<MediaStream | null>(null);
  const [mixerStream, setMixerStream] = useState<MediaStream | null>(null);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isScratchpadOpen, setScratchpadOpen] = useState(false);

  // --- State Management for SherlockED ---
  const [question, setQuestion] = useState<Question | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [currentSelection, setCurrentSelection] = useState<any>(null); // To track user's selection in real-time
  const userId = "test_student"; // Hardcoded for now

  const fetchQuestion = async () => {
    console.log("Fetching new question..."); // DEBUG LOG
    setLoading(true);
    setFeedback(null);
    setCurrentSelection(null); // Reset selection on new question
    try {
      const response = await fetch(`http://localhost:8000/next-question/${userId}`);
      if (!response.ok) throw new Error('Failed to fetch question.');
      const data: Question = await response.json();
      setQuestion(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred.");
      setQuestion(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestion();
  }, []);

  const handleAnswerSubmit = async (answer: string | number | string[]) => {
    if (!question) return;

    console.log('Submitting answer:', answer); // DEBUG LOG

    try {
      const response = await fetch('http://localhost:8000/submit-answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          question_id: question.question_id,
          answer: answer,
          response_time_seconds: 5, // Placeholder
        }),
      });

      console.log('API Response Status:', response.status); // DEBUG LOG

      if (!response.ok) {
        console.error('API Error Response:', await response.text());
        setFeedback('Error submitting answer.');
        return;
      }
      
      const result = await response.json();
      console.log('API Result:', result); // DEBUG LOG
      setFeedback(result.correct ? 'Correct!' : 'Incorrect. Try again!');
    } catch (error) {
      console.error('Failed to submit answer:', error);
      setFeedback('An error occurred.');
    }
  };

  const handleSelectionChange = (selection: any) => {
    setCurrentSelection(selection);
  };

  const handleNextQuestion = () => {
    fetchQuestion();
  };

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');
    setSocket(ws);
    return () => ws.close();
  }, []);

  return (
    <div className="App">
      <LiveAPIProvider options={apiOptions}>
        {/* --- DEBUG LOGS --- */}
        <div style={{ position: 'absolute', top: 0, left: 0, background: 'rgba(0,0,0,0.7)', color: 'white', padding: '10px', zIndex: 1000, fontSize: '12px' }}>
          <p><strong>Question Type:</strong> {question?.question_type || 'N/A'}</p>
          <p><strong>Current Selection:</strong> {JSON.stringify(currentSelection) || 'N/A'}</p>
          <p><strong>Correct Answer:</strong> {JSON.stringify(question?.correct_answer) || 'N/A'}</p>
          <p><strong>Feedback:</strong> {feedback || 'N/A'}</p>
        </div>
        {/* --- END DEBUG LOGS --- */}
        <div className="streaming-console">
          <SidePanel />
          <main>
            <div className="main-app-area">
              <div className="question-panel">
                <ScratchpadCapture socket={socket}>
                  {loading && <p>Loading question...</p>}
                  {error && <p>Error: {error}</p>}
                  {question && (
                    <SherlockED
                      question={question}
                      onAnswerSubmit={handleAnswerSubmit}
                      onSelectionChange={handleSelectionChange}
                    />
                  )}
                  {feedback && (
                    <div className="feedback-container">
                      <p className="feedback-text">{feedback}</p>
                      <button onClick={handleNextQuestion}>Next Question</button>
                    </div>
                  )}
                  {isScratchpadOpen && (
                    <div className="scratchpad-container">
                      <Scratchpad />
                    </div>
                  )}
                </ScratchpadCapture>
              </div>
              <MediaMixerDisplay socket={socket} renderCanvasRef={renderCanvasRef} />
            </div>

            <ControlTray
              socket={socket}
              renderCanvasRef={renderCanvasRef}
              videoRef={videoRef}
              supportsVideo={true}
              onVideoStreamChange={setVideoStream}
              onMixerStreamChange={setMixerStream}
              enableEditingSettings={true}
            >
              <button onClick={() => setScratchpadOpen(!isScratchpadOpen)}>
                <span className="material-symbols-outlined">
                  {isScratchpadOpen ? "close" : "edit"}
                </span>
              </button>
            </ControlTray>
          </main>
        </div>
        <Logger filter="none" />
      </LiveAPIProvider>
    </div>
  );
}

export default App;
