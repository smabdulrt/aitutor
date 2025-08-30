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
  onAnswerChange: (answer: string | number | string[] | null) => void;
}

const SherlockED: React.FC<SherlockEDProps> = ({ question, onAnswerChange }) => {
  const getWidgetInfo = () => {
    if (!question) return { component: null, name: 'None' };

    switch (question.question_type) {
      case 'static-text':
        // Static text is just for display. The button is handled in App.tsx.
        return { component: <StaticTextDisplay content={question.content} />, name: 'Static Text Display' };
      case 'multiple-choice':
        const choices = (question.options || []).map((option, index) => ({
          id: `${question.question_id}-choice-${index}`,
          content: option,
        }));
        return { component: <MultipleChoiceDisplay content={question.content} choices={choices} onAnswerChange={onAnswerChange} />, name: 'Multiple Choice Display' };
      case 'free-response':
        return { component: <FreeResponseDisplay content={question.content} onAnswerChange={onAnswerChange} />, name: 'Free Response Display' };
      case 'numeric-input':
        return { component: <NumericInputDisplay content={question.content} onAnswerChange={onAnswerChange} />, name: 'Numeric Input Display' };
      case 'counting-boxes':
        return { component: <CountingBoxesDisplay content={question.content} onAnswerChange={onAnswerChange} />, name: 'Counting Boxes Display' };
      default:
        return { component: <div>Unsupported question type</div>, name: 'Unsupported' };
    }
  };

  const widgetInfo = getWidgetInfo();

  return (
    <div className="sherlock-ed">
      <div className="widget-debug-info" style={{ color: 'grey', fontSize: '0.8em', marginBottom: '10px' }}>
        SherlockED: {widgetInfo.name}
      </div>
      <div className="question-container">
        {widgetInfo.component}
      </div>
    </div>
  );
};

export default SherlockED;
