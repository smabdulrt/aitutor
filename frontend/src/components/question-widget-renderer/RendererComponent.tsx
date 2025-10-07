import React, { useEffect, useState, useRef } from "react";
import {ServerItemRenderer} from "../../package/perseus/src/server-item-renderer";
import type { PerseusItem } from "@khanacademy/perseus-core";
import { storybookDependenciesV2 } from "../../package/perseus/testing/test-dependencies";
import { scorePerseusItem } from "@khanacademy/perseus-score";
import { keScoreFromPerseusScore } from "../../package/perseus/src/util/scoring";
import { RenderStateRoot } from "@khanacademy/wonder-blocks-core";
import { PerseusI18nContextProvider } from "../../package/perseus/src/components/i18n-context";
import { mockStrings } from "../../package/perseus/src/strings";
import { KEScore } from "@khanacademy/perseus-core";

const RendererComponent = () => {
    const [perseusItem, setPerseusItem] = useState<PerseusItem | null>(null);
    const [loading, setLoading] = useState(true);
    const [endOfTest, setEndOfTest] = useState(false);
    const [score, setScore] = useState<KEScore>();
    const [isAnswered, setIsAnswered] = useState(false);
    const [userId] = useState("student_demo"); // You can make this dynamic later
    const [currentQuestionData, setCurrentQuestionData] = useState<any>(null);
    const [questionStartTime, setQuestionStartTime] = useState<number>(0);
    const rendererRef = useRef<ServerItemRenderer>(null);

    // Create user on mount
    useEffect(() => {
        const createUser = async () => {
            try {
                const response = await fetch('http://localhost:8000/users/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: userId,
                        age: 8,
                        grade_level: 'GRADE_3'
                    })
                });
                const data = await response.json();
                console.log('User created:', data);
            } catch (err) {
                console.log('User might already exist:', err);
            }
        };
        createUser();
    }, [userId]);

    const fetchNextQuestion = async () => {
        setLoading(true);
        try {
            const response = await fetch(`http://localhost:8000/next-question/${userId}`);
            if (!response.ok) {
                if (response.status === 404) {
                    setEndOfTest(true);
                    setLoading(false);
                    return;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log("DASH API response:", data);

            // Store question data for later submission
            setCurrentQuestionData(data);

            // Parse the content field which contains the Perseus question JSON
            let questionContent;
            try {
                questionContent = typeof data.content === 'string'
                    ? JSON.parse(data.content)
                    : data.content;
            } catch (e) {
                console.error('Failed to parse question content:', e);
                questionContent = { content: data.content || '', widgets: {}, images: {} };
            }

            // Convert to Perseus PerseusItem format
            const perseusQuestion: PerseusItem = {
                question: questionContent,
                answerArea: {},
                itemDataVersion: { major: 0, minor: 1 },
                hints: data.hints || []
            };

            setPerseusItem(perseusQuestion);
            setIsAnswered(false);
            setQuestionStartTime(Date.now());
            setLoading(false);
        } catch (err) {
            console.error("Failed to fetch next question:", err);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchNextQuestion();
    }, []);

    const handleNext = () => {
        // Fetch the next question from DASH API
        fetchNextQuestion();
    };

    const handleSubmit = async () => {
        if (rendererRef.current && perseusItem && currentQuestionData) {
            const userInput = rendererRef.current.getUserInput();
            const question = perseusItem.question;
            const perseusScore = scorePerseusItem(question, userInput, "en");

            // Continue to include an empty guess for the now defunct answer area.
            const maxCompatGuess = [rendererRef.current.getUserInputLegacy(), []];
            const keScore = keScoreFromPerseusScore(perseusScore, maxCompatGuess, rendererRef.current.getSerializedState().question);

            // Calculate response time
            const responseTime = (Date.now() - questionStartTime) / 1000; // Convert to seconds

            // Display score locally
            setIsAnswered(true);
            setScore(keScore);
            console.log("Score:", keScore);
            console.log("Response time:", responseTime, "seconds");

            // Send score to DASH API to update student model with breadcrumb cascade
            try {
                const submitResponse = await fetch('http://localhost:8000/submit-answer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: userId,
                        question_id: currentQuestionData.question_id,
                        skill_ids: currentQuestionData.skill_ids || [],
                        is_correct: keScore.correct,
                        response_time: responseTime
                    })
                });

                if (submitResponse.ok) {
                    const result = await submitResponse.json();
                    console.log('✅ Answer submitted to DASH:', result);
                    console.log(`   Affected ${result.affected_skills_count} skills via cascade`);
                    console.log(`   Current streak: ${result.current_streak}`);
                } else {
                    console.error('Failed to submit answer:', submitResponse.statusText);
                }
            } catch (err) {
                console.error('Error submitting answer to DASH:', err);
            }
        }
    };

    // Helper function to get full skill_id breadcrumb
    const getBreadcrumb = () => {
        if (!currentQuestionData?.skill_ids?.[0]) return "N/A";
        // Return the full skill_id (e.g., "math_8_1.1.1.1")
        return currentQuestionData.skill_ids[0];
    };

    return (
            <div className="framework-perseus">
                <div style={{ padding: "20px" }}>
                    <button
                        onClick={handleNext}
                        className="absolute top-19 right-8 bg-black rounded
                            text-white p-2">Next</button>

                    {loading ? (
                        <p>Loading question...</p>
                    ) : endOfTest ? (
                        <p>You've successfully completed your test!</p>
                    ) : perseusItem ? (
                        <div>
                            {/* Display breadcrumb and question ID */}
                            {currentQuestionData && (
                                <div style={{
                                    backgroundColor: '#f0f4f8',
                                    padding: '10px 15px',
                                    borderRadius: '8px',
                                    marginBottom: '20px',
                                    fontFamily: 'monospace',
                                    fontSize: '14px',
                                    border: '1px solid #d1d5db'
                                }}>
                                    <div style={{ display: 'flex', gap: '20px' }}>
                                        <span>
                                            <strong>📍 Breadcrumb:</strong> {getBreadcrumb()}
                                        </span>
                                        <span>
                                            <strong>🔑 Question ID:</strong> {currentQuestionData.question_id}
                                        </span>
                                    </div>
                                </div>
                            )}
                            <PerseusI18nContextProvider locale="en" strings={mockStrings}>
                                <RenderStateRoot>
                                    <ServerItemRenderer
                                        ref={rendererRef}
                                        problemNum={0}
                                        item={perseusItem}
                                        dependencies={storybookDependenciesV2}
                                        apiOptions={{}}
                                        linterContext={{
                                            contentType: "",
                                            highlightLint: true,
                                            paths: [],
                                            stack: [],
                                        }}
                                        showSolutions="none"
                                        hintsVisible={0}
                                        reviewMode={false}
                                        />
                                </RenderStateRoot>
                            </PerseusI18nContextProvider>
                            {isAnswered && <div 
                                className="flex justify-between mt-9">
                                    <span className={score?.correct ? "text-green-400 italic" : "text-red-400 italic"}>
                                        {score?.correct ?(<p>Correct Answer!</p>):(<p>Wrong Answer.</p>)}
                                    </span>
                            </div>}
                        </div>
                    ) : (
                        <p>No question available</p>
                    )}
                    <button 
                        className="bg-blue-500 absolute rounded text-white p-2 right-8 mt-8"
                        onClick={handleSubmit}>
                        Submit
                    </button>
                </div>
            </div>
    );
};

export default RendererComponent;
