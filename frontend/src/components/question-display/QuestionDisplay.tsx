import React from 'react';
import SherlockED from '../SherlockED/SherlockED';
import './question-display.scss';
import { Question } from '../../types';

interface QuestionDisplayProps {
  question: Question | null;
  error: string | null;
  loading: boolean;
  onAnswerSubmit: (answer: string | number) => void;
}

// This component is now a simple "presenter". It receives all its data via props.
const QuestionDisplay: React.FC<QuestionDisplayProps> = (props: any) => {
  if (props.loading) {
    return <div className="question-display">Loading question...</div>;
  }

  if (props.error) {
    return <div className="question-display error">Error: {props.error}</div>;
  }

  if (!props.question) {
    return <div className="question-display">No question available.</div>;
  }

  // It passes the data down to SherlockED, which will render the correct interactive widget.
  return (
    <div className="question-display">
      <SherlockED question={props.question} onAnswerSubmit={props.onAnswerSubmit} />
    </div>
  );
};

export default QuestionDisplay;
