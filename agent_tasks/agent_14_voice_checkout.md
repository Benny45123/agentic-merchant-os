# AGENT_14_VOICE_CHECKOUT

## Objective

Build Voice-Activated Hands-Free In-App Conversational Shopping & Checkout for the Next.js Buyer Chat interface using the browser's native Web Speech API (`webkitSpeechRecognition` / `SpeechRecognition`).

## Scope

- `frontend/src/app/(buyer)/chat/page.tsx`: Microphone button (`🎙️`), live speech recognition state, audio wave pulse animation
- Natural voice command parsing (e.g. *"Add wireless headphones and extended warranty to my cart"*, *"Proceed to checkout"*)
- Visual recording indicator with live speech transcript streaming

## Interaction Flow

1. Buyer clicks `🎙️` button in the chat input bar.
2. Browser requests microphone permission and starts speech listening.
3. Pulse indicator activates (`🔴 Listening...`).
4. Buyer speaks: *"Add the AeroSound headphones and 1-year warranty"*.
5. Speech-to-text transcript is automatically populated into the input bar.
6. Automatically submits the conversational turn to `/agent/chat`.
7. Assistant responds via text and updates the live cart on the right-hand panel.

## Acceptance Criteria

- [ ] Microphone button toggles speech recording on supported browsers (Chrome, Safari, Edge).
- [ ] Speech transcript appears smoothly and submits seamlessly to the Commerce Agent.
- [ ] Graceful fallback if speech recognition is unsupported or permission is denied.
