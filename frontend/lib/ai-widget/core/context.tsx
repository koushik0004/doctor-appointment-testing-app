"use client";

import {
  createContext,
  useContext,
  useMemo,
  useReducer,
  type Dispatch,
} from "react";

import {
  aiWidgetReducer,
  createInitialAiWidgetState,
  type AiWidgetAction,
} from "@/lib/ai-widget/core/state";
import type { AiWidgetProviderProps, AiWidgetState } from "@/lib/ai-widget/types";

type AiWidgetContextValue = {
  state: AiWidgetState;
  dispatch: Dispatch<AiWidgetAction>;
};

const AiWidgetContext = createContext<AiWidgetContextValue | null>(null);

export function AiWidgetProvider({
  children,
  config,
}: AiWidgetProviderProps) {
  const [state, dispatch] = useReducer(
    aiWidgetReducer,
    config,
    createInitialAiWidgetState,
  );

  const value = useMemo(
    () => ({
      state,
      dispatch,
    }),
    [state],
  );

  return (
    <AiWidgetContext.Provider value={value}>
      {children}
    </AiWidgetContext.Provider>
  );
}

export function useAiWidget() {
  const context = useContext(AiWidgetContext);

  if (!context) {
    throw new Error("useAiWidget must be used inside AiWidgetProvider.");
  }

  return context;
}
