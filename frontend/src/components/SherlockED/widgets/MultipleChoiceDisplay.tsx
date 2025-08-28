import React, { useState } from 'react';

interface MultipleChoiceDisplayProps {
  content: string;
  options: string[];
  onSubmit: (answer: string) => void;
}

const MultipleChoiceDisplay: React.FC<MultipleChoiceDisplayProps> = ({ content, options, onSubmit }) => {
  const [selectedValue, setSelectedValue] = useState<string | null>(null);

  const handleSubmit = () => {
    if (selectedValue) {
      onSubmit(selectedValue);
    }
  };

  return (
    <div className="widget-multiple-choice">
      <p className="question-content">{content}</p>
      <div className="options-container">
        {options.map((option, index) => (
          <div key={index} className="option">
            <input
              type="radio"
              id={`option-${index}`}
              name="multiple-choice"
              value={option}
              onChange={(e) => setSelectedValue(e.target.value)}
              checked={selectedValue === option}
            />
            <label htmlFor={`option-${index}`}>{option}</label>
          </div>
        ))}
      </div>
      <button onClick={handleSubmit} disabled={!selectedValue}>
        Submit
      </button>
    </div>
  );
};

export default MultipleChoiceDisplay;
