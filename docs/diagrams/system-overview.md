# System Overview Diagram

```mermaid
flowchart LR

A[Developer Workstation (macOS)] --> B[VS Code Terminal]
B --> C{Shell}
C -->|zsh| D[.zshrc]
C -->|bash| E[No pyenv init]

D --> F[pyenv]
F --> G[Python 3.9 (runtime)]
F --> H[Python 3.10 (pre-commit)]

G --> I[.venv (project)]
H --> J[pre-commit hook envs]

I --> K[pi-log application]
J --> L[ansible-lint hook]

K --> M[Raspberry Pi 3 Deployment]
```
