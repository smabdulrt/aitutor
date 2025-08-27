import {
  ChangeEvent,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import "./settings-dialog.scss";
import { useLiveAPIContext } from "../../contexts/LiveAPIContext";
import VoiceSelector from "./VoiceSelector";
import ResponseModalitySelector from "./ResponseModalitySelector";
import { FunctionDeclaration, LiveConnectConfig, Tool } from "@google/genai";

type FunctionDeclarationsTool = Tool & {
  functionDeclarations: FunctionDeclaration[];
};

export default function SettingsDialog() {
  const [open, setOpen] = useState(false);
  const { config, setConfig, connected } = useLiveAPIContext();
  const [basePrompt, setBasePrompt] = useState("");
  const [userPrompt, setUserPrompt] = useState("");

  const functionDeclarations: FunctionDeclaration[] = useMemo(() => {
    if (!Array.isArray(config.tools)) {
      return [];
    }
    return (config.tools as Tool[])
      .filter((t: Tool): t is FunctionDeclarationsTool =>
        Array.isArray((t as any).functionDeclarations)
      )
      .map((t) => t.functionDeclarations)
      .filter((fc) => !!fc)
      .flat();
  }, [config]);

  useEffect(() => {
    const fetchPrompt = async () => {
      try {
        const response = await fetch('/ai_tutor_system_prompt.md');
        const promptText = await response.text();
        setBasePrompt(promptText);
        setConfig({
          ...config,
          systemInstruction: promptText,
        });
      } catch (error) {
        console.error('Error fetching system prompt:', error);
      }
    };

    fetchPrompt();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleUserPromptChange = useCallback(
    (event: ChangeEvent<HTMLTextAreaElement>) => {
      const newUserPrompt = event.target.value;
      setUserPrompt(newUserPrompt);
      const combinedPrompt = `${basePrompt}\n${newUserPrompt}`;
      const newConfig: LiveConnectConfig = {
        ...config,
        systemInstruction: combinedPrompt.trim(),
      };
      setConfig(newConfig);
    },
    [basePrompt, config, setConfig]
  );

  const updateFunctionDescription = useCallback(
    (editedFdName: string, newDescription: string) => {
      const newConfig: LiveConnectConfig = {
        ...config,
        tools:
          config.tools?.map((tool) => {
            const fdTool = tool as FunctionDeclarationsTool;
            if (!Array.isArray(fdTool.functionDeclarations)) {
              return tool;
            }
            return {
              ...tool,
              functionDeclarations: fdTool.functionDeclarations.map((fd) =>
                fd.name === editedFdName
                  ? { ...fd, description: newDescription }
                  : fd
              ),
            };
          }) || [],
      };
      setConfig(newConfig);
    },
    [config, setConfig]
  );

  return (
    <div className="settings-dialog">
      <button
        className="action-button material-symbols-outlined"
        onClick={() => setOpen(!open)}
      >
        settings
      </button>
      <dialog className="dialog" style={{ display: open ? "block" : "none" }}>
        <div className={`dialog-container ${connected ? "disabled" : ""}`}>
          {connected && (
            <div className="connected-indicator">
              <p>
                These settings can only be applied before connecting and will
                override other settings.
              </p>
            </div>
          )}
          <div className="mode-selectors">
            <ResponseModalitySelector />
            <VoiceSelector />
          </div>

          <h3>System Instructions</h3>
          <textarea
            className="system"
            onChange={handleUserPromptChange}
            value={userPrompt}
            placeholder="Add additional instructions for the model..."
          />
          <h4>Function declarations</h4>
          <div className="function-declarations">
            <div className="fd-rows">
              {functionDeclarations.map((fd, fdKey) => (
                <div className="fd-row" key={`function-${fdKey}`}>
                  <span className="fd-row-name">{fd.name}</span>
                  <span className="fd-row-args">
                    {Object.keys(fd.parameters?.properties || {}).map(
                      (item, k) => (
                        <span key={k}>{item}</span>
                      )
                    )}
                  </span>
                  <input
                    key={`fd-${fd.description}`}
                    className="fd-row-description"
                    type="text"
                    defaultValue={fd.description}
                    onBlur={(e) =>
                      updateFunctionDescription(fd.name!, e.target.value)
                    }
                  />
                </div>
              ))}
            </div>
          </div>
        </div>
      </dialog>
    </div>
  );
}
