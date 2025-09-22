import React, { useEffect, useState, useRef } from "react";
import {ServerItemRenderer} from "../package/perseus/src/server-item-renderer";
import type { PerseusItem } from "@khanacademy/perseus-core";
import { storybookDependenciesV2 } from "../package/perseus/testing/test-dependencies";
import { PerseusI18nProvider } from "../contexts/perseusI18nContext"; 

const RendererComponent = () => {
    const [perseusItems, setPerseusItems] = useState<PerseusItem[]>([]);
    const [item, setItem] = useState(0);
    const [loading, setLoading] = useState(true);
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


    const perseusItem = perseusItems[item] || {};

    return (
        <PerseusI18nProvider
            strings={{
                chooseNumAnswers: ({numCorrect}) => 
                    `Select ${numCorrect} correct answer${numCorrect !== "1" ? "s" : ""}`,
                chooseAllAnswers: "Select all correct answers",
                chooseOneAnswer: "Select one answer",
            }}
        >

            <div className="framework-perseus">
                <div style={{ padding: "20px" }}>
                    <button
                        onClick={() => {
                            const index = (item === perseusItems.length - 1) ? 0 : (item + 1);
                            console.log(`Item: ${index}`)
                            setItem(index)}
                        }
                        className="absolute top-19 right-8 bg-black rounded 
                            text-white p-2">Next</button>
                            
                    {perseusItems.length > 0 ? (
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
                        ) : (
                            <p>Loading...</p>
                        )}
                </div>
            </div>

        </PerseusI18nProvider>
        
    );
};

export default RendererComponent;
