import React, { createContext, useContext, useReducer } from 'react';
import  type { Exam, UserAnswer, ExamContextType, ExamAction } from './types';

const initialState = {
    examData: null,
    userAnswers: {},
    score: null,
    isGraded: false,
}

export const ExamContext = createContext<ExamContextType>({ state:{} as Exam,dispatch:() => undefined});

// utils/gradingLogic.js
export const calculateScore = (userAnswers, answerKey, gradingScheme) => {
  let correctCount = 0;
  Object.keys(userAnswers).forEach((questionId) => {
    if (userAnswers[questionId] === answerKey[questionId]) {
      correctCount++;
    }
  });

  // Apply grading scheme (e.g., percentage, weighted questions, etc.)
  return (correctCount / Object.keys(answerKey).length) * 100;
};


const examReducer = (state, action) => {
  switch (action.type) {
    case 'SET_EXAM':
      return { ...state, examData: action.payload };
    case 'RECORD_ANSWER':
      return {
        ...state,
        userAnswers: {
          ...state.userAnswers,
          [action.payload.questionId]: action.payload.answer,
        },
      };
    case 'GRADE_EXAM':
      const { answerKey, gradingScheme } = action.payload;
      const calculatedScore = calculateScore(state.userAnswers, answerKey, gradingScheme);
      return { ...state, score: calculatedScore, isGraded: true };
    case 'RESET_EXAM':
      return initialState;
    default:
      return state;
  }
};

export const ExamProvider = ({ children }) => {
  const [state, dispatch] = useReducer(examReducer, initialState);

  return (
    <ExamContext.Provider value={{ state, dispatch }}>
      {children}
    </ExamContext.Provider>
  );
};
