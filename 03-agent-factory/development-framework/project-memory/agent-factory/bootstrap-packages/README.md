# Bootstrap Packages

## What are Bootstrap Packages?
Bootstrap packages provide the exact kickoff instructions and context reading sequences needed to start a fresh agent session. They serve as a bridge between the reusable templates in the framework and the specific project/artifact context stored in the living memory.

## How they differ from templates
Templates (located in `docs/templates/`) are generic, fill-in-the-blank structures that apply to any project using AFDF. Bootstrap packages are highly specific, pre-filled instances of those templates tailored for a single artifact, eliminating the need to manually reconstruct context prompts.

## How they differ from artifacts
Bootstrap packages are purely instructional markdown text used *before* development begins. They do not contain any runtime code, implementation tests, or infrastructure associated with the actual artifact being built.

## How to create a package for another project/artifact later
1. Identify the new project or artifact.
2. Review the core AFDF templates and living project memory.
3. Create a new directory here (e.g., `artifact-08-new-agent/`).
4. Generate `README.md`, `context-load-order.md`, role-specific kickoffs, safety boundaries, and inspection instructions mimicking the existing packages.
5. Store the package here to ensure future sessions start cleanly.

## Existing Packages
- `artifact-07-github-repo-steward/` - The first real use of AFDF to bootstrap an upcoming artifact.
