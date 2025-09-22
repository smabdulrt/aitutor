import React, { useEffect, useState, useRef } from "react";
import { I18nContextType } from "@khanacademy/perseus/src/components/i18n-context";
import { ServerItemRenderer, PerseusI18nContextProvider } from "@khanacademy/perseus";
import { type PerseusItem } from "@khanacademy/perseus-core";
import { ExamContext } from "../../contexts/ExamContext";
import { DependenciesV2 } from "../../perseus-init";
import { string } from "./perseus-string";

const RendererComponent = () => {
    const [perseusItems, setPerseusItems] = useState<PerseusItem[]>([]);
    const [item, setItem] = useState(0);
    const [loading, setLoading] = useState(true);
    const { dispatch } = React.useContext(ExamContext);

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
        <PerseusI18nContextProvider
            strings={string}
        >

            <div style={{ padding: "20px" }}>
                <button
                    onClick={() => {
                        const index = (item === perseusItems.length - 1) ? 0 : (item + 1);
                        console.log(`Item: ${index}`)
                        setItem(index)}
                    }
                    className="absolute top-18 bg-black rounded text-white p-2 right-8">
                        Next
                </button>
                {!loading && perseusItems.length >= 1 ? (
                    <ServerItemRenderer
                        problemNum={0}
                        item={perseusItem}
                        dependencies={DependenciesV2}
                        apiOptions={(() => {
                            const options = {};
                            console.log("[DEBUG] RendererComponent apiOptions:", options);
                            return options;
                        })()}
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
        </PerseusI18nContextProvider>
    );
};

export default RendererComponent;
