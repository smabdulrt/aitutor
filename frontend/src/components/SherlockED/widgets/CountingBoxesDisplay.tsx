import React, { useState } from 'react';

interface CountingBoxesDisplayProps {
  content: string;
  onSubmit: (answers: string[]) => void;
}

const CountingBoxesDisplay: React.FC<CountingBoxesDisplayProps> = ({ content, onSubmit }) => {
  const [answers, setAnswers] = useState<string[]>(Array(5).fill(''));

  const handleChange = (index: number, value: string) => {
    const newAnswers = [...answers];
    // Allow only single numeric digits
    newAnswers[index] = value.replace(/[^0-9]/g, '').slice(0, 1);
    setAnswers(newAnswers);
  };

  const handleSubmit = () => {
    // Only submit if all boxes are filled
    if (answers.every(answer => answer !== '')) {
      onSubmit(answers);
    }
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
