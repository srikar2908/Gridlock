import { create } from "zustand";

interface CopilotState {
  isSpeaking: boolean;
  setSpeaking: (value: boolean) => void;
}

export const useCopilotStore = create<CopilotState>((set) => ({
  isSpeaking: false,
  setSpeaking: (isSpeaking) => set({ isSpeaking }),
}));
