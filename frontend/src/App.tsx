import { useRef, useState, useEffect } from "react";
import "./App.scss";
import { LiveAPIProvider } from "./contexts/LiveAPIContext";
import SidePanel from "./components/side-panel/SidePanel";
import MediaMixerDisplay from "./components/media-mixer-display/MediaMixerDisplay";
import ScratchpadCapture from "./components/scratchpad-capture/ScratchpadCapture";
import QuestionDisplay from "./components/question-display/QuestionDisplay";
import ControlTray from "./components/control-tray/ControlTray";
import { LiveClientOptions } from "./types";
import Scratchpad from "./components/scratchpad/Scratchpad";

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY as string;
if (typeof API_KEY !== "string") {
  throw new Error("set VITE_GEMINI_API_KEY in .env");
}

// Get WebSocket URLs from environment or use defaults for local dev
const MEDIAMIXER_COMMAND_WS = import.meta.env.VITE_MEDIAMIXER_COMMAND_WS || 'ws://localhost:8080/command';
const MEDIAMIXER_VIDEO_WS = import.meta.env.VITE_MEDIAMIXER_VIDEO_WS || 'ws://localhost:8080/video';

const apiOptions: LiveClientOptions = {
  apiKey: API_KEY,
};

function App() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const renderCanvasRef = useRef<HTMLCanvasElement>(null);
  const [videoStream, setVideoStream] = useState<MediaStream | null>(null);
  const [mixerStream, setMixerStream] = useState<MediaStream | null>(null);
  const mixerVideoRef = useRef<HTMLVideoElement>(null);
  const [commandSocket, setCommandSocket] = useState<WebSocket | null>(null);
  const [videoSocket, setVideoSocket] = useState<WebSocket | null>(null);
  const [isScratchpadOpen, setScratchpadOpen] = useState(false);

  useEffect(() => {
    console.log('Connecting to MediaMixer...');
    console.log('Command WS:', MEDIAMIXER_COMMAND_WS);
    console.log('Video WS:', MEDIAMIXER_VIDEO_WS);

    // Command WebSocket for sending frames/commands TO MediaMixer
    const commandWs = new WebSocket(MEDIAMIXER_COMMAND_WS);
    commandWs.onopen = () => console.log('Command WebSocket connected');
    commandWs.onerror = (error) => console.error('Command WebSocket error:', error);
    setCommandSocket(commandWs);

    // Video WebSocket for receiving video FROM MediaMixer
    const videoWs = new WebSocket(MEDIAMIXER_VIDEO_WS);
    videoWs.onopen = () => console.log('Video WebSocket connected');
    videoWs.onerror = (error) => console.error('Video WebSocket error:', error);
    setVideoSocket(videoWs);

    return () => {
      commandWs.close();
      videoWs.close();
    };
  }, []);

  useEffect(() => {
    if (mixerVideoRef.current && mixerStream) {
      mixerVideoRef.current.srcObject = mixerStream;
    }
  }, [mixerStream]);

  return (
    <div className="App">
      <LiveAPIProvider options={apiOptions}>
        <div className="streaming-console">
          <SidePanel />
          <main>
            <div className="main-app-area">
              <div className="question-panel">
                <ScratchpadCapture socket={commandSocket}>
                  <QuestionDisplay />
                  {isScratchpadOpen && (
                    <div className="scratchpad-container">
                      <Scratchpad />
                    </div>
                  )}
                </ScratchpadCapture>
              </div>
              <MediaMixerDisplay socket={videoSocket} renderCanvasRef={renderCanvasRef} />
            </div>

            <ControlTray
              socket={commandSocket}
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
      </LiveAPIProvider>
    </div>
  );
}

export default App;