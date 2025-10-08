import * as React from "react";
import { registerAllWidgetsForTesting, Dependencies } from "@khanacademy/perseus";
import { PerseusDependencies, PerseusDependenciesV2 } from "@khanacademy/perseus";
import {TestMathjax} from "./test-mathjax";

// We do nothing in this implementation, but it is easy to spy on the .Log of
// the PerseusDependencies in tests and then assert on the calls.
const LogForTesting = {
    log: () => {},
    error: () => {},
};

interface JIPTDependency {
    useJIPT: boolean;
}

interface GraphieMovablesJiptLabelsDependency {
    addLabel: (label: string, useMath: boolean) => void;
}

interface SvgImageJiptLabelsDependency {
    addLabel: (label: string, useMath: boolean) => void;
}

interface RendererTranslationComponentsDependency {
    addComponent: (renderer: unknown) => number;
    removeComponentAtIndex: (index: number) => void;
}

interface TeXDependencyProps {
    children: React.ReactNode;
}

type TeXDependency = React.FC<TeXDependencyProps>;

type StaticUrlFn = (str?: string | null) => string;

interface VideoData {
    id: string;
    contentId: string;
    youtubeId: string;
    title: string;
    __typename: string;
}

type UseVideoStatus =
    | { status: "success"; data: { video: VideoData } }
    | { status: "loading" };

type UseVideoDependency = (id: string, kind: string) => UseVideoStatus;

interface InitialRequestUrlDependency {
    origin: string;
    host: string;
    protocol: string;
}

interface LogDependency {
    log: (...args: unknown[]) => void;
    error: (...args: unknown[]) => void;
}

interface TestDependenciesInterface {
    JIPT: JIPTDependency;
    graphieMovablesJiptLabels: GraphieMovablesJiptLabelsDependency;
    svgImageJiptLabels: SvgImageJiptLabelsDependency;
    rendererTranslationComponents: RendererTranslationComponentsDependency;
    TeX: TeXDependency;
    staticUrl: StaticUrlFn;
    useVideo: UseVideoDependency;
    InitialRequestUrl: InitialRequestUrlDependency;
    isDevServer: boolean;
    kaLocale: string;
    Log: LogDependency;
}

const testDependencies: TestDependenciesInterface = {
    // JIPT
    JIPT: {
        useJIPT: false,
    },
    graphieMovablesJiptLabels: {
        addLabel: (label: string, useMath: boolean) => {},
    },
    svgImageJiptLabels: {
        addLabel: (label: string, useMath: boolean) => {},
    },
    rendererTranslationComponents: {
        addComponent: (renderer: unknown) => -1,
        removeComponentAtIndex: (index: number) => {},
    },

    TeX: ({children}: TeXDependencyProps) => {
        return <span className="mock-TeX">{children}</span>;
    },

    staticUrl: (str?: string | null) => {
        // We define the interface such that TypeScript can infer calls properly.
        // However, it means that return types are hard to match here in
        // the implementation.
        return `mockStaticUrl(${str})`;
    },

    // video widget
    useVideo: (id: string, kind: string) => {
        // Used by video-transcript-link.jsx.fixture.js
        if (id === "YoutubeId" && kind === "YOUTUBE_ID") {
            return {
                status: "success",
                data: {
                    video: {
                        id: "YoutubeVideo",
                        contentId: "contentId",
                        youtubeId: "YoutubeId",
                        title: "Youtube Video Title",
                        __typename: "Video",
                    },
                },
            };
        }
        if (id === "slug-video-id" && kind === "READABLE_ID") {
            return {
                status: "success",
                data: {
                    video: {
                        title: "Slug Video Title",
                        id: "VideoId",
                        youtubeId: "YoutubeId",
                        contentId: "contentId",
                        __typename: "Video",
                    },
                },
            };
        }

        return {
            status: "loading",
        };
    },

    InitialRequestUrl: {
        origin: "origin-test-interface",
        host: "host-test-interface",
        protocol: "protocol-test-interface",
    },

    isDevServer: false,
    kaLocale: "en",

    Log: LogForTesting,
};

const testDependenciesV2: PerseusDependenciesV2 = {
    analytics: {
        onAnalyticsEvent: async () => {},
    },
    useVideo: () => {
        return {
            status: "success",
            data: {
                video: null,
            },
        };
    },
};


export const TestDependencies: PerseusDependencies = {
    ...testDependencies,
    TeX: TestMathjax,
    staticUrl: (str) => str,
};


export const DependenciesV2: PerseusDependenciesV2 = {
    ...testDependenciesV2,
    // Override if necessary
};

// Initialize Perseus
import * as Perseus from "@khanacademy/perseus";
Perseus.Dependencies.setDependencies(TestDependencies);
Perseus.registerAllWidgetsForTesting();