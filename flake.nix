{
  description = "A nix dev shell";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
  outputs = all@{ self, nixpkgs, ... }:
  let
    pkgs = import nixpkgs { 
      system="x86_64-linux";
      config.allowUnfree = true;};
    model = pkgs.fetchurl {
      url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/danny/low/en_US-danny-low.onnx?download=true";
      hash = "sha256-VqmulJnpYVFPBgqsKGbLMjoh5ZiVkvxPII5W/cMjq2Q=";
    };
    model-config = pkgs.fetchurl {
      url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/danny/low/en_US-danny-low.onnx.json?download=true.json";
      hash = "sha256-GR3qG6mGMZnYyi6QSPg7IZIZ+0UPYnZ+4C8bxFaM5PQ=";
    };
  in 
  {
    # Utilized by `nix develop`
    devShell.x86_64-linux = 
    pkgs.mkShell {
      packages = [
        (pkgs.python3.withPackages (python-pkgs: [
          python-pkgs.requests
          python-pkgs.beautifulsoup4
          python-pkgs.python-dotenv
        ]))
        pkgs.piper-tts
        pkgs.sox
      ];
      shellHook = ''
        export MODELFILE=${model}
        export MODELCONFIG=${model-config}
      '';
    };
  };
}
