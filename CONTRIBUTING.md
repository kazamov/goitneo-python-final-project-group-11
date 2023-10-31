# How to contribute to Neoassistant

## Prerequisites

- Install Python >= 3.11.0
- Install VS Code
- Install Git

## Setup environment

- Clone the repository
- Open the project in the VS Code
- Install suggested extensions
- Create a virtual environment using the VS Code command interface (`Ctrl + Shift + P` - on Windows) with command "Python: Create environment..." -> Choose Venv -> Choose Python distribution -> Check `dev` option to install dev dependencies also. It will create a virtual environment and install the dependencies.

## Debug project

To debug a project there is a launch configuration for the VS Code named "Python: Neoversity". Set a break point in the entrypoint file or in any other file and run the debug using the interface button or press F5 (on Windows).

## Submitting a PR

- Create a branch from `main`. Name it using template: `Feature-ZN-AddEmailField` where `ZN` - is the initials, and `AddEmailField` - is a short title of the feature.
- Push the changes
- Create a PR and ask for code review
