import React, { useState } from 'react';

interface Choice {
  id: string;
  content: string;
}

interface MultipleChoiceDisplayProps {
  content: string;
  choices: Choice[];
  onSubmit: (selectedChoiceId: string) => void;
}

const MultipleChoiceDisplay: React.FC<MultipleChoiceDisplayProps> = ({ content, choices, onSubmit }) => {
  const [selectedChoice, setSelectedChoice] = useState<string | null>(null);

  const handleSubmit = () => {
    if (selectedChoice) {
      onSubmit(selectedChoice);
    }
  };

  return (
    <div className="widget-multiple-choice">
      <p className="question-content">{content}</p>
      <div className="choices">
        {choices.map((choice) => (
          <div key={choice.id} className="choice">
            <input
              type="radio"
              id={choice.id}
              name="multiple-choice"
              value={choice.id}
              checked={selectedChoice === choice.id}
              onChange={() => setSelectedChoice(choice.id)}
            />
            <label htmlFor={choice.id}>{choice.content}</label>
          </div>
        ))}
      </div>
      <button onClick={handleSubmit} disabled={!selectedChoice}>
        Submit
      </button>
    </div>
  );
};

export default MultipleChoiceDisplay;
