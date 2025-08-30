import React, { useState, useEffect } from 'react';

interface NumericInputDisplayProps {
  content: string;
  onAnswerChange: (answer: number | null) => void;
}

const NumericInputDisplay: React.FC<NumericInputDisplayProps> = ({ content, onAnswerChange }) => {
  const [answer, setAnswer] = useState('');

  useEffect(() => {
    const num = parseFloat(answer);
    if (!isNaN(num)) {
      onAnswerChange(num);
    } else {
      onAnswerChange(null);
    }
  }, [answer, onAnswerChange]);

  return (
    <div className="widget-numeric-input">
      <p className="question-content">{content}</p>
      <input
        type="number"
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        placeholder="Enter a number..."
      />
    </div>
  );
};

export default NumericInputDisplay;
