import React from "react";
import QuestionWidgetRenderer from "./QuestionWidgetRenderer";
import type { PerseusItem } from "@khanacademy/perseus-core";
import { useState, useEffect, useRef } from "react";

const samplePerseusItem: PerseusItem = {
    question: {
        content: "What is 2 + 2?",
        images: {},
        widgets: {
            "radio 1": {
                type: "radio",
                alignment: "default",
                static: false,
                graded: true,
                options: {
                    choices: [
                        {
                            content: "3",
                            correct: false,
                            id: "first-1"
                        },
                        {
                            content: "4",
                            correct: true,
                            id: "second-2"
                        },
                        {
                            content: "5",
                            correct: false,
                            id: "third-3"
                        },
                    ],
                    randomize: false,
                    multipleSelect: false,
                    // displayCount: null,
                    hasNoneOfTheAbove: false,
                    // onePerLine: false,
                    deselectEnabled: false,
                },
                version: {
                    major: 1,
                    minor: 0,
                },
            },
        },
    },
    answerArea: null,
    // itemDataVersion: {
    //     major: 0,
    //     minor: 1,
    // },
    hints: [],
    // _multi: null,
};

const QuestionWidgetRendererTest: React.FC = () => {
    const [perseusItems, setPerseusItems] = useState<PerseusItem[]>([]);
        const [item, setItem] = useState(0);
        const [loading, setLoading] = useState(true);
        // const { dispatch } = React.useContext(ExamContext)
        // const rendererRef = useRef<ServerItemRenderer>(null);
    
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
        <div>
            <button
                    onClick={() => {
                        const index = (item === perseusItems.length - 1) ? 0 : (item + 1);
                        console.log(`Item: ${index}`)
                        setItem(index)}
                    }
                    className="absolute top-19 right-8 bg-black rounded 
                        text-white p-2">Next</button>
            <h1>Question Widget Renderer Test</h1>
            { loading === false ? 
            (
                <QuestionWidgetRenderer
                perseusItem={perseusItem}
                useDebugUI={false}
            />) : (
                <div>Loading... </div>
            )}
        </div>
    );
};

export default QuestionWidgetRendererTest;