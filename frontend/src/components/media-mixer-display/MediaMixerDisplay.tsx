import React, { useEffect, useState, RefObject } from 'react';
import cn from 'classnames';
import { RiSidebarFoldLine, RiSidebarUnfoldLine } from "react-icons/ri";
import { useMediaMixer } from '../../hooks/use-media-mixer';
import './media-mixer-display.scss';

interface MediaMixerDisplayProps {
  socket: WebSocket | null;
  renderCanvasRef: RefObject<HTMLCanvasElement>;
}

const MediaMixerDisplay: React.FC<MediaMixerDisplayProps> = ({ socket, renderCanvasRef }) => {
  const [imageData, setImageData] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { toggleCamera, toggleScreen } = useMediaMixer({ socket });

  useEffect(() => {
    if (!socket) return;

    const image = new Image();
    image.onload = () => {
      const canvas = renderCanvasRef.current;
      if (canvas) {
        const ctx = canvas.getContext('2d');
        if (ctx) {
          canvas.width = image.width;
          canvas.height = image.height;
          ctx.drawImage(image, 0, 0);
        }
      }
    };

    socket.onopen = () => {
      console.log('Connected to MediaMixer WebSocket');
      setIsConnected(true);
      setError(null);

      // Send initial commands to match the behavior of the HTML file
      toggleCamera(true);
      toggleScreen(true);
    };

    socket.onmessage = (event) => {
      const frame = event.data;
      const imageUrl = `data:image/jpeg;base64,${frame}`;
      setImageData(imageUrl);
      image.src = imageUrl;
    };

    socket.onerror = (err) => {
      console.error('WebSocket error:', err);
      setError('Failed to connect to MediaMixer. Is it running?');
      setIsConnected(false);
    };

    socket.onclose = () => {
      console.log('Disconnected from MediaMixer WebSocket');
      setIsConnected(false);
    };
  }, [socket, renderCanvasRef, toggleCamera, toggleScreen]);

  return (
    <div className={cn("media-mixer-display", { "collapsed": isCollapsed })}>
      <header className="top">
        <button onClick={() => setIsCollapsed(!isCollapsed)} className="collapse-button">
          {isCollapsed ? (
            <RiSidebarUnfoldLine color="#b4b8bb" />
          ) : (
            <RiSidebarFoldLine color="#b4b8bb" />
          )}
        </button>
        <h2>Media Mixer Display</h2>
      </header>
      <div className="media-mixer-content">
        {error && <div className="error-message">{error}</div>}
        {!isConnected && !error && <div>Connecting to MediaMixer...</div>}
        {isConnected && imageData && (
          <img src={imageData} alt="MediaMixer Stream" style={{ width: '100%', height: 'auto' }} />
        )}
      </div>
    </div>
  );
};

export default MediaMixerDisplay;
