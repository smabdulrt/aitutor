import React, { useState, useEffect } from 'react';
import './sherlock-ed.scss';
import StaticTextDisplay from './widgets/StaticTextDisplay';
import MultipleChoiceDisplay from './widgets/MultipleChoiceDisplay';
import FreeResponseDisplay from './widgets/FreeResponseDisplay';
import NumericInputDisplay from './widgets/NumericInputDisplay';

// Define the structure of a question
interface Question {
  question_id: string;
  skill_ids: string[];
  content: string;
  question_type: 'static-text' | 'multiple-choice' | 'free-response' | 'numeric-input';
  options?: string[];
  difficulty: number;
}

type AnswerStatus = 'unanswered' | 'correct' | 'incorrect';

const SherlockED: React.FC = () => {
  const [question, setQuestion] = useState<Question | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [answerStatus, setAnswerStatus] = useState<AnswerStatus>('unanswered');
  const userId = "test_student"; // Hardcoded for now

  const fetchQuestion = async () => {
    try {
      setLoading(true);
      setAnswerStatus('unanswered');
      const response = await fetch(`http://localhost:8000/next-question/${userId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch the next question. The student may have mastered all skills.');
      }
      const data: Question = await response.json();
      setQuestion(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred.");
      setQuestion(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestion();
  }, [userId]);

  const handleAnswerSubmit = async (answer: string) => {
    if (!question) return;

    const startTime = Date.now();
    const response = await fetch('http://localhost:8000/submit-answer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: userId,
            question_id: question.question_id,
            answer: answer,
            response_time_seconds: (Date.now() - startTime) / 1000,
        }),
    });

    const result = await response.json();
    setAnswerStatus(result.correct ? 'correct' : 'incorrect');
  };

  const renderWidget = () => {
    if (!question) return null;

    switch (question.question_type) {
      case 'static-text':
        return <StaticTextDisplay content={question.content} />;
      case 'multiple-choice':
        return <MultipleChoiceDisplay content={question.content} options={question.options || []} onSubmit={handleAnswerSubmit} />;
      case 'free-response':
        return <FreeResponseDisplay content={question.content} onSubmit={handleAnswerSubmit} />;
      case 'numeric-input':
        return <NumericInputDisplay content={question.content} onSubmit={handleAnswerSubmit} />;
      default:
        return <div>Unsupported question type</div>;
    }
  };

  if (loading) {
    return <div className="sherlock-ed">Loading question...</div>;
  }

  if (error) {
    return <div className="sherlock-ed error">Error: {error}</div>;
  }

  return (
    <div className={`sherlock-ed status-${answerStatus}`}>
      <div className="question-container">
        {renderWidget()}
      </div>
      {answerStatus !== 'unanswered' && (
        <div className="feedback-container">
          <p className="feedback-text">{answerStatus === 'correct' ? 'Correct!' : 'Incorrect. Try the next one!'}</p>
          <button onClick={fetchQuestion}>Next Question</button>
        </div>
      )}
    </div>
  );
};

export default SherlockED;
