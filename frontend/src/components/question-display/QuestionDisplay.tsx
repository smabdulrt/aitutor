import React from 'react';
import SherlockED from '../SherlockED/SherlockED';
import './question-display.scss';
import { Question } from '../../types';

interface QuestionDisplayProps {
  question: Question | null;
  error: string | null;
  loading: boolean;
  onAnswerChange: (answer: any) => void;
}

// This component is now a simple "presenter". It receives all its data via props.
const QuestionDisplay: React.FC<QuestionDisplayProps> = ({ question, error, loading, onAnswerChange }) => {
  if (loading) {
    return <div className="question-display">Loading question...</div>;
  }

  if (error) {
    return <div className="question-display error">Error: {error}</div>;
  }

  if (!question) {
    return <div className="question-display">No question available.</div>;
  }

  // It passes the data down to SherlockED, which will render the correct interactive widget.
  return (
    <div className="question-display">
      <SherlockED question={question} onAnswerChange={onAnswerChange} />
    </div>
  );
};

export default QuestionDisplay;
