# Security and privacy

## Supported versions

Security fixes are provided for the latest released minor version.

## Report a vulnerability

Do not open a public issue containing credentials, confidential manuscripts, patient information, controlled-access data, or an exploitable vulnerability. Use GitHub's private vulnerability reporting feature for this repository.

## Sensitive-data boundary

The repository ignores `inputs/`, `runs/`, and `work/` contents by default. Keep real manuscripts and generated findings out of version control. This is a safeguard, not a substitute for checking staged files before every commit.

`biomethodlens review` transmits extracted manuscript text to the selected provider. Review the provider's current data controls and your institutional obligations before use. `plan`, `demo`, and `validate` do not make provider calls.

The project never needs your API key in a file. Use an environment variable or approved secret manager.
