import React from 'react';

interface StaticTextDisplayProps {
  content: string;
  onSubmit: (answer: string) => void; // We'll use onSubmit to signal continuation
}

const StaticTextDisplay: React.FC<StaticTextDisplayProps> = ({ content, onSubmit }) => {
  const handleContinue = () => {
    // We can pass a standard string like "acknowledged" to the submit handler
    // to trigger the feedback and "Next Question" button.
    onSubmit("acknowledged");
  };

  return (
    <div className="widget-static-text">
      <p className="question-content">{content}</p>
      <button onClick={handleContinue}>Continue</button>
    </div>
  );
};

export default StaticTextDisplay;
