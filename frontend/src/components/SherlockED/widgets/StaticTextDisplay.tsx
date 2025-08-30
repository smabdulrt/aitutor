import React from 'react';

interface StaticTextDisplayProps {
  content: string;
}

const StaticTextDisplay: React.FC<StaticTextDisplayProps> = ({ content }) => {
  return (
    <div className="widget-static-text">
      <p className="question-content">{content}</p>
      {/* The "Continue" button is now managed by the parent App component */}
    </div>
  );
};

export default StaticTextDisplay;
