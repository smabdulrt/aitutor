import React, { useState, useEffect } from 'react';

interface Choice {
  id: string;
  content: string;
}

interface MultipleChoiceDisplayProps {
  content: string;
  choices: Choice[];
  onAnswerChange: (selectedChoiceId: string | null) => void;
}

const MultipleChoiceDisplay: React.FC<MultipleChoiceDisplayProps> = ({ content, choices, onAnswerChange }) => {
  const [selectedChoice, setSelectedChoice] = useState<string | null>(null);

  useEffect(() => {
    onAnswerChange(selectedChoice);
  }, [selectedChoice, onAnswerChange]);

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
    </div>
  );
};

export default MultipleChoiceDisplay;
