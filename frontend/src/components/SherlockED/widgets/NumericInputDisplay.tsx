import React, { useState } from 'react';

interface NumericInputDisplayProps {
  content: string;
  onSubmit: (answer: string) => void;
}

const NumericInputDisplay: React.FC<NumericInputDisplayProps> = ({ content, onSubmit }) => {
  const [answer, setAnswer] = useState('');

  const handleSubmit = () => {
    if (answer.trim()) {
      onSubmit(answer.trim());
    }
  };

  return (
    <div className="widget-numeric-input">
      <p className="question-content">{content}</p>
      <input
        type="number"
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        placeholder="Enter a number..."
      />
      <button onClick={handleSubmit} disabled={!answer.trim()}>
        Submit
      </button>
    </div>
  );
};

export default NumericInputDisplay;
