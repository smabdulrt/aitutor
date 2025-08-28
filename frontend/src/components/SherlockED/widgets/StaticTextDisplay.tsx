import React from 'react';

interface StaticTextDisplayProps {
  content: string;
}

const StaticTextDisplay: React.FC<StaticTextDisplayProps> = ({ content }) => {
  return (
    <div className="widget-static-text">
      <p>{content}</p>
    </div>
  );
};

export default StaticTextDisplay;
