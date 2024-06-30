# less-stupid-chatbot

This is a talking chatbot that uses a local LLM (for example [llama-cpp](https://github.com/ggerganov/llama.cpp)) and [PiperTTS](https://github.com/rhasspy/piper).\
On a decently sized GPU this enables a real-time conversation with the model.

## Installation

Dependencies are set up automatically by a [Nix](https://nixos.org/) devShell.
The OpenAI API compatible local LLM server must be installed and run separately.