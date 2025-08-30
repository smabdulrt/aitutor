import React from 'react';
import './sherlock-ed.scss';
import StaticTextDisplay from './widgets/StaticTextDisplay';
import MultipleChoiceDisplay from './widgets/MultipleChoiceDisplay';
import FreeResponseDisplay from './widgets/FreeResponseDisplay';
import NumericInputDisplay from './widgets/NumericInputDisplay';
import CountingBoxesDisplay from './widgets/CountingBoxesDisplay'; // Import the new widget
import { Question } from '../../types';

interface SherlockEDProps {
  question: Question;
  onAnswerSubmit: (answer: string | number | string[]) => void; // Add string[] for the new type
}

const SherlockED: React.FC<SherlockEDProps> = ({ question, onAnswerSubmit }) => {
  const handleAnswerSubmit = (answer: string | number | string[]) => {
    onAnswerSubmit(answer);
  };

  const renderWidget = () => {
    if (!question) return null;

    switch (question.question_type) {
      case 'static-text':
        return <StaticTextDisplay content={question.content} onSubmit={handleAnswerSubmit} />;
      case 'multiple-choice':
        const choices = (question.options || []).map((option, index) => ({
          id: `${question.question_id}-choice-${index}`,
          content: option,
        }));
        return <MultipleChoiceDisplay content={question.content} choices={choices} onSubmit={handleAnswerSubmit} />;
      case 'free-response':
        return <FreeResponseDisplay content={question.content} onSubmit={handleAnswerSubmit} />;
      case 'numeric-input':
        return <NumericInputDisplay content={question.content} onSubmit={handleAnswerSubmit} />;
      case 'counting-boxes':
        return <CountingBoxesDisplay content={question.content} onSubmit={handleAnswerSubmit} />;
      default:
        return <div>Unsupported question type</div>;
    }
  };

  return (
    <div className="sherlock-ed">
      <div className="question-container">
        {renderWidget()}
      </div>
    </div>
  );
};

export default SherlockED;
