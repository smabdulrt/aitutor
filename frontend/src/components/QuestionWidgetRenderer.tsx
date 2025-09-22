import React, { useRef } from "react";
import { ServerItemRenderer } from "../package/perseus/src/server-item-renderer";
import { ServerItemRendererWithDebugUI } from "../package/testing/server-item-renderer-with-debug-ui";
import { PerseusI18nContextProvider } from "../package/perseus/src/components/i18n-context";
import { DependenciesContext } from "../package/perseus/src/dependencies";
import { cypressDependenciesV2, storybookDependenciesV2 } from "../package/testing/test-dependencies";
import { mockStrings } from "../package/perseus/src/strings";
import type { PerseusItem } from "@khanacademy/perseus-core";

// Import CSS files for styling
import "../package/perseus/src/styles/perseus-renderer.css";
import "../package/perseus/src/styles/styles.css";
import "../package/perseus/src/styles/util.css";
import "../package/perseus/src/styles/widgets/dropdown.css";
import "../package/perseus/src/styles/widgets/expression.css";
import "../package/perseus/src/styles/widgets/free-response.css";
import "../package/perseus/src/styles/widgets/image.css";
import "../package/perseus/src/styles/widgets/interactive-graph.css";
import "../package/perseus/src/styles/widgets/numeric.css";
import "../package/perseus/src/styles/widgets/radio.css";
import "../package/perseus/src/styles/widgets/table.css";

interface QuestionWidgetRendererProps {
    perseusItem: PerseusItem;
    useDebugUI?: boolean;
    problemNum?: number;
    reviewMode?: boolean;
    showSolutions?: "none" | "all" | "correct";
    hintsVisible?: number;
    apiOptions?: any;
    linterContext?: any;
}

const QuestionWidgetRenderer: React.FC<QuestionWidgetRendererProps> = ({
    perseusItem,
    useDebugUI = false,
    problemNum = 0,
    reviewMode = false,
    showSolutions = "none",
    hintsVisible = 0,
    apiOptions = {},
    linterContext,
}) => {
    const rendererRef = useRef<ServerItemRenderer>(null);

    const defaultLinterContext = {
        contentType: "",
        highlightLint: true,
        paths: [],
        stack: [],
    };

    const mergedLinterContext = linterContext || defaultLinterContext;

    const dependencies = useDebugUI ? storybookDependenciesV2 : cypressDependenciesV2;

    if (useDebugUI) {
        return (
            <PerseusI18nContextProvider
                strings={mockStrings}
                locale="en"
            >
                <DependenciesContext.Provider value={dependencies}>
                    <ServerItemRendererWithDebugUI
                        title="Question Widget"
                        item={perseusItem}
                        apiOptions={apiOptions}
                        linterContext={mergedLinterContext}
                        reviewMode={reviewMode}
                        showSolutions={showSolutions}
                    />
                </DependenciesContext.Provider>
            </PerseusI18nContextProvider>
        );
    }

    return (
        <PerseusI18nContextProvider
            strings={mockStrings}
            locale="en"
        >
            <DependenciesContext.Provider value={dependencies}>
                <div style={{ padding: "20px" }}>
                    <ServerItemRenderer
                        ref={rendererRef}
                        problemNum={problemNum}
                        item={perseusItem}
                        dependencies={dependencies}
                        apiOptions={apiOptions}
                        linterContext={mergedLinterContext}
                        showSolutions={showSolutions}
                        hintsVisible={hintsVisible}
                        reviewMode={reviewMode}
                    />
                </div>
            </DependenciesContext.Provider>
        </PerseusI18nContextProvider>
    );
};

export default QuestionWidgetRenderer;