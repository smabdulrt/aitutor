import React, { useState, useEffect } from 'react';

interface CountingBoxesDisplayProps {
  content: string;
  onAnswerChange: (answers: string[] | null) => void;
}

const CountingBoxesDisplay: React.FC<CountingBoxesDisplayProps> = ({ content, onAnswerChange }) => {
  const [answers, setAnswers] = useState<string[]>(Array(5).fill(''));

  useEffect(() => {
    // If at least one box is filled, send the answer up. Otherwise, send null.
    if (answers.some(answer => answer !== '')) {
      onAnswerChange(answers);
    } else {
      onAnswerChange(null);
    }
  }, [answers, onAnswerChange]);

  const handleChange = (index: number, value: string) => {
    const newAnswers = [...answers];
    newAnswers[index] = value.replace(/[^0-9]/g, '').slice(0, 1);
    setAnswers(newAnswers);
  };

  return (
    <div className="widget-counting-boxes">
      <p className="question-content">{content}</p>
      <div className="boxes-container">
        {answers.map((answer, index) => (
          <input
            key={index}
            type="text"
            value={answer}
            onChange={(e) => handleChange(index, e.target.value)}
            className="counting-box"
            maxLength={1}
            style={{ width: '3em', textAlign: 'center', marginRight: '0.5em' }}
          />
        ))}
      </div>
      {/* The submit button is now managed by the parent App component */}
    </div>
  );
};

export default CountingBoxesDisplay;
