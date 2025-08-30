import React, { useState, useEffect } from 'react';

interface CountingBoxesDisplayProps {
  content: string;
  onSubmit: (answers: string[]) => void;
  onSelectionChange: (answers: string[]) => void;
}

const CountingBoxesDisplay: React.FC<CountingBoxesDisplayProps> = ({ content, onSubmit, onSelectionChange }) => {
  const [answers, setAnswers] = useState<string[]>(Array(5).fill(''));

  // Propagate changes up to the parent component
  useEffect(() => {
    onSelectionChange(answers);
  }, [answers, onSelectionChange]);

  const handleChange = (index: number, value: string) => {
    const newAnswers = [...answers];
    newAnswers[index] = value.replace(/[^0-9]/g, '').slice(0, 1);
    setAnswers(newAnswers);
  };

  const handleSubmit = () => {
    onSubmit(answers);
  };

  const isSubmitDisabled = answers.some(answer => answer === '');

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
      <button onClick={handleSubmit} disabled={isSubmitDisabled}>
        Submit
      </button>
    </div>
  );
};

export default CountingBoxesDisplay;
