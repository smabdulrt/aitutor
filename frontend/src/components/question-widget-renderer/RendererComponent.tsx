import React, { useEffect, useState, useRef, useCallback } from "react";
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
    const [perseusItems, setPerseusItems] = useState<PerseusItem[]>([]);
    const [currentQuestion, setCurrentQuestion] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [score, setScore] = useState<KEScore>();
    const [isAnswered, setIsAnswered] = useState(false);
    const rendererRef = useRef<ServerItemRenderer>(null);
    const userId = "1"; // TODO: Get from auth context

    // Fetch next question from DASH API
    const fetchNextQuestion = useCallback(async () => {
        try {
            setLoading(true);
            const response = await fetch(`http://localhost:8000/next-question/${userId}`);

            if (!response.ok) {
                throw new Error('No recommended question found or API error.');
            }

            const dashQuestion = await response.json();
            console.log("DASH API response:", dashQuestion);

            // For now, we need to convert DASH question to Perseus format
            // TODO: Update this when Perseus questions are integrated with DASH
            // For MVP, we'll fetch Perseus format from the existing API
            const perseusResponse = await fetch(`http://localhost:8001/api/questions/${dashQuestion.question_id}`);

            if (perseusResponse.ok) {
                const perseusData = await perseusResponse.json();
                setCurrentQuestion(perseusData[0]); // Assuming first item
            } else {
                // Fallback: show DASH question as text (temporary)
                console.warn("Could not fetch Perseus version, showing basic question");
                setCurrentQuestion({
                    question: {
                        content: dashQuestion.content,
                        widgets: {}
                    }
                });
            }

            setIsAnswered(false);
            setLoading(false);

        } catch (err) {
            console.error("Failed to fetch next question:", err);
            setLoading(false);
        }
    }, [userId]);

    // Fetch first question on mount
    useEffect(() => {
        fetchNextQuestion();
    }, [fetchNextQuestion]);

    const handleNext = () => {
        // Fetch next question from DASH API
        fetchNextQuestion();
    };

    const handleSubmit = () => {
        if (rendererRef.current && currentQuestion) {
            const userInput = rendererRef.current.getUserInput();
            const question = currentQuestion.question;
            const score = scorePerseusItem(question, userInput, "en");

            // Continue to include an empty guess for the now defunct answer area.
            const maxCompatGuess = [rendererRef.current.getUserInputLegacy(), []];
            const keScore = keScoreFromPerseusScore(score, maxCompatGuess, rendererRef.current.getSerializedState().question);

            // TODO: Send score back to DASH API
            // await fetch(`http://localhost:8000/record-answer`, {
            //     method: 'POST',
            //     body: JSON.stringify({
            //         user_id: userId,
            //         question_id: currentQuestion.id,
            //         is_correct: keScore.correct,
            //         response_time: ...
            //     })
            // });

            setIsAnswered(true);
            setScore(keScore);
            console.log("Score:", keScore);
        }
    };

    return (
        <div className="framework-perseus">
            <div style={{ padding: "20px" }}>
                <button
                    onClick={handleNext}
                    disabled={loading}
                    className="absolute top-19 right-8 bg-black rounded
                        text-white p-2 disabled:opacity-50">
                    {loading ? "Loading..." : "Next"}
                </button>

                {loading ? (
                    <p>Loading next question...</p>
                ) : currentQuestion ? (
                    <div>
                        <PerseusI18nContextProvider locale="en" strings={mockStrings}>
                            <RenderStateRoot>
                                <ServerItemRenderer
                                    ref={rendererRef}
                                    problemNum={0}
                                    item={currentQuestion}
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
                    <p>No questions available.</p>
                )}
                <button
                    className="bg-blue-500 absolute rounded text-white p-2 right-8 mt-8"
                    onClick={handleSubmit}
                    disabled={loading || !currentQuestion}>
                    Submit
                </button>
            </div>
        </div>
    );
};

export default RendererComponent;
