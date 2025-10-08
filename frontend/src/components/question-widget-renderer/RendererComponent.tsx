import { scorePerseusItem } from "@khanacademy/perseus-score";
import { keScoreFromPerseusScore } from "./scoring";
import { KEScore } from "@khanacademy/perseus-core";
import React, { useEffect, useState, useRef } from "react";
import { ServerItemRenderer, PerseusI18nContextProvider } from "@khanacademy/perseus";
import { type PerseusItem } from "@khanacademy/perseus-core";
import { DependenciesV2 } from "../../perseus-init";
import { KeypadContext } from "@khanacademy/keypad-context";
import { mockStrings } from "./type";
import {RenderStateRoot, useRenderState, RenderState, View} from "@khanacademy/wonder-blocks-core"

const RendererComponent = () => {
    const [perseusItems, setPerseusItems] = useState<PerseusItem[]>([]);
    const [item, setItem] = useState(0);
    const [loading, setLoading] = useState(true);
    const [endOfTest, setEndOfTest] = useState(false);
    const [score, setScore] = useState<KEScore>();
    const [isAnswered, setIsAnswered] = useState(false);
    const rendererRef = useRef<React.ComponentRef<typeof ServerItemRenderer>>(null);

    useEffect(() => {
        fetch("http://localhost:8001/api/questions/20")
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

            setIsAnswered(false);
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

            // return score for the given question 
            setIsAnswered(true);
            setScore(keScore);
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
                        <div>
                            <PerseusI18nContextProvider locale="en" strings={mockStrings}>
                                    <View>
                                        <KeypadContext.Consumer >
                                            {({keypadElement}) => (<RenderStateRoot>
                                                <ServerItemRenderer
                                                    ref={rendererRef}
                                                    problemNum={0}
                                                    item={perseusItem}
                                                    dependencies={DependenciesV2}
                                                    keypadElement={keypadElement}
                                                    apiOptions={{}}
                                                    linterContext={{
                                                        contentType: "",
                                                        highlightLint: true,
                                                        paths: [],
                                                        stack: [],
                                                    }}
                                                    showSolutions="none"
                                                    hintsVisible={0}
                                                    reviewMode={
                                                        (score && score?.correct) || 
                                                        false
                                                    }/>
                                            </RenderStateRoot>)}
                                        </KeypadContext.Consumer>
                                    </View>
                            </PerseusI18nContextProvider>
                            {isAnswered && <div 
                                className="flex justify-between mt-9">
                                    <span className={score?.correct ? "text-green-400 italic" : "text-red-400 italic"}>
                                        {score?.correct ?(<p>Correct Answer!</p>):(<p>Wrong Answer.</p>)}
                                    </span>
                            </div>}
                        </div>
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