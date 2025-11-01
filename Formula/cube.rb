# Homebrew Formula for Agent Cube CLI
# To install from a custom tap:
#   brew tap aetheronhq/cube
#   brew install cube

class Cube < Formula
  desc "Agent Cube CLI - Orchestrate parallel LLM coding workflows"
  homepage "https://github.com/aetheronhq/aetheron-connect-v2"
  url "https://github.com/aetheronhq/aetheron-connect-v2/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "YOUR_SHA256_HERE"
  license "MIT"
  version "1.0.0"

  depends_on "jq"

  def install
    # Install all scripts
    libexec.install "scripts"
    
    # Install documentation
    doc.install "AGENT_CUBE.md" if File.exist?("AGENT_CUBE.md")
    doc.install "AGENT_CUBE_AUTOMATION.md" if File.exist?("AGENT_CUBE_AUTOMATION.md")
    
    # Create wrapper script that sets up environment
    (bin/"cube").write <<~EOS
      #!/bin/bash
      export PATH="$HOME/.local/bin:$PATH"
      exec "#{libexec}/scripts/cube" "$@"
    EOS
    
    chmod 0755, bin/"cube"
  end

  def caveats
    <<~EOS
      Agent Cube CLI has been installed!

      Prerequisites:
        1. Install cursor-agent CLI:
           npm install -g @cursor/cli

        2. Authenticate with Cursor:
           cursor-agent login

      Get started:
        cube --help        Show all commands
        cube version       Show version info

      Documentation:
        #{doc}/AGENT_CUBE.md
        #{doc}/AGENT_CUBE_AUTOMATION.md
    EOS
  end

  test do
    assert_match "1.0.0", shell_output("#{bin}/cube version")
  end
end

