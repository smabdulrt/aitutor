import React, { useState, useEffect } from 'react';
import './question-display.scss';
import RendererComponent from "../RendererComponent";

const QuestionDisplay: React.FC = () => {
  
  return (
    <div className="question-display">
      <h2 className="question-title">Here's your next question:</h2>
      <RendererComponent />
    </div>
  );
};

export default QuestionDisplay;
