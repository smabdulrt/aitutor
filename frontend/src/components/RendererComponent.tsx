import React, { useEffect, useState, useRef } from "react";
import {ServerItemRenderer} from "../package/perseus/src/server-item-renderer";
import type { PerseusItem } from "@khanacademy/perseus-core";
import { storybookDependenciesV2 } from "../package/perseus/testing/test-dependencies";
import { PerseusI18nProvider } from "../contexts/perseusI18nContext";
import { scorePerseusItem } from "@khanacademy/perseus-score";
import { keScoreFromPerseusScore } from "../package/perseus/src/util/scoring";
import { RenderStateRoot } from "@khanacademy/wonder-blocks-core";
import { PerseusI18nContextProvider } from "../package/perseus/src/components/i18n-context";
import { mockStrings } from "../package/perseus/src/strings";

const RendererComponent = () => {
    const [perseusItems, setPerseusItems] = useState<PerseusItem[]>([]);
    const [item, setItem] = useState(0);
    const [loading, setLoading] = useState(true);
    const [endOfTest, setEndOfTest] = useState(false);
    const rendererRef = useRef<ServerItemRenderer>(null);

    useEffect(() => {
        fetch("http://localhost:8001/api/questions/16")
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

    const handleNext = () => {
        setItem((prev) => {
            const index = prev + 1;

            if (index >= perseusItems.length) {
                setEndOfTest(true);
                return prev; // stay at last valid index
            }

            if (index === perseusItems.length - 1) {
                setEndOfTest(true);
            }

            return index;
        });
    };


    const handleSubmit = () => {
        if (rendererRef.current) {
            const userInput = rendererRef.current.getUserInput();
            const question = perseusItem.question;
            const score = scorePerseusItem(question, userInput, "en");

            // Continue to include an empty guess for the now defunct answer area.
            const maxCompatGuess = [rendererRef.current.getUserInputLegacy(), []];
            const keScore = keScoreFromPerseusScore(score, maxCompatGuess, rendererRef.current.getSerializedState().question);

            // Optionally, grade the exam if this is the last question
            // For now, just log the score
            console.log("Score:", keScore);
        }
    };

    const perseusItem = perseusItems[item] || {};

    return (
            <div className="framework-perseus">
                <div style={{ padding: "20px" }}>
                    <button
                        onClick={handleNext}
                        className="absolute top-19 right-8 bg-black rounded 
                            text-white p-2">Next</button>
                            
                    {endOfTest ? (
                        <p>You've successfully completed your test!</p>
                    ): (
                        perseusItems.length > 0 ? (
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
                        ) : (
                            <p>Loading...</p>
                        )
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
