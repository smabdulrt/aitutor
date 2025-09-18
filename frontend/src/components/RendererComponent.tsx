import React, { useEffect, useState, useRef } from "react";
import { ServerItemRenderer } from "../package/perseus/src/server-item-renderer";
import { storybookDependenciesV2 } from "../package/perseus/testing/test-dependencies";
import type { PerseusItem } from "@khanacademy/perseus-core";
import { PerseusI18nProvider } from "../contexts/perseusI18nContext";
import { ExamContext } from "../contexts/ExamContext";
import { scorePerseusItem } from "@khanacademy/perseus-score";
import { keScoreFromPerseusScore } from "../package/perseus/src/util/scoring"; 

const RendererComponent = () => {
    const [perseusItems, setPerseusItems] = useState<PerseusItem[]>([]);
    const [item, setItem] = useState(0);
    const [loading, setLoading] = useState(true);
    const { dispatch } = React.useContext(ExamContext);
    const rendererRef = useRef<ServerItemRenderer>(null);

    useEffect(() => {
        fetch("http://localhost:8001/api/questions")
            .then((response) => response.json())
            .then((data) => {
                console.log("API response:", data);
                setPerseusItems(data);
                setLoading(false);
            })
            .catch((err) => {
                console.error("Failed to fetch questions:", err);
                setLoading(false);
            });
    }, []);

    const handleSubmit = () => {
        if (rendererRef.current) {
            const userInput = rendererRef.current.getUserInput();
            const question = perseusItem.question;
            const score = scorePerseusItem(question, userInput, "en");
            
            // Continue to include an empty guess for the now defunct answer area.
            const maxCompatGuess = [rendererRef.current.getUserInputLegacy(), []];
            const keScore = keScoreFromPerseusScore(score, maxCompatGuess, rendererRef.current.getSerializedState().question);

            // Record the answer 
            dispatch({
                type: 'RECORD_ANSWER',
                payload: {
                    questionId: `question-${item}`,
                    answer: userInput
                }
            });

            // Optionally, grade the exam if this is the last question
            // For now, just log the score
            console.log("Score:", keScore);
        }
    };

    const perseusItem = perseusItems[item] || {};

    return (
        <PerseusI18nProvider
            strings={{
                chooseNumAnswers: ({ numCorrect }: { numCorrect: string }) => 
                    `Select ${numCorrect} correct answer${numCorrect !== "1" ? "s" : ""}`,
                chooseAllAnswers: "Select all correct answers",
                chooseOneAnswer: "Select one answer",
            }}
        >
            <div style={{ padding: "20px" }}>
                {loading && <p>Loading questions...</p>}
                {!loading && perseusItems.length >= 1 &&
                    <ServerItemRenderer
                        // ref={rendererRef}
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
                    />}
                
                {/* <button
                    onClick={handleSubmit}
                    className="absolute bg-blue-500 rounded text-white p-2 bottom-8 right-40">
                    Submit
                </button> */}
                <button
                    onClick={() => {
                        const index = (item === perseusItems.length - 1) ? 0 : (item + 1);
                        console.log(`Item: ${index}`)
                        setItem(index)}
                    }
                    className="absolute bg-black rounded text-white p-2 bottom-8
                    right-8">
                        Next
                </button>
            </div>
        </PerseusI18nProvider>
    );
};

export default RendererComponent;
