import React, { useState } from 'react';

interface FreeResponseDisplayProps {
  content: string;
  onSubmit: (answer: string) => void;
}

const FreeResponseDisplay: React.FC<FreeResponseDisplayProps> = ({ content, onSubmit }) => {
  const [answer, setAnswer] = useState('');

  const handleSubmit = () => {
    if (answer.trim()) {
      onSubmit(answer.trim());
    }
  };

  return (
    <div className="widget-free-response">
      <p className="question-content">{content}</p>
      <input
        type="text"
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        placeholder="Type your answer here..."
      />
      <button onClick={handleSubmit} disabled={!answer.trim()}>
        Submit
      </button>
    </div>
  );
};

export default FreeResponseDisplay;
