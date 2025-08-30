import React, { useState, useEffect } from 'react';

interface FreeResponseDisplayProps {
  content: string;
  onAnswerChange: (answer: string | null) => void;
}

const FreeResponseDisplay: React.FC<FreeResponseDisplayProps> = ({ content, onAnswerChange }) => {
  const [answer, setAnswer] = useState('');

  useEffect(() => {
    if (answer.trim()) {
      onAnswerChange(answer.trim());
    } else {
      onAnswerChange(null);
    }
  }, [answer, onAnswerChange]);

  return (
    <div className="widget-free-response">
      <p className="question-content">{content}</p>
      <input
        type="text"
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        placeholder="Type your answer here..."
      />
    </div>
  );
};

export default FreeResponseDisplay;
