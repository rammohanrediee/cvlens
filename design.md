# Design — cvLens

## Direction

cvLens is a quiet, task-focused resume workspace. The interface uses a cool gray canvas, restrained white surfaces, forest-green actions, and clear typographic hierarchy. It avoids marketing panels, fabricated metrics, and decorative UI that does not help the review.

## Upload

The upload screen presents three real stages: upload, analysis, and review. It asks for one PDF and, optionally, a job description. The primary action stays disabled until a valid PDF is selected.

## Results

Document identity and the score/priority summary precede a tabbed workspace. Overview, Checks, Suggestions, and Job match are exclusive panels with keyboard navigation. Desktop uses a main workspace and narrow context rail; tablet stacks the context; mobile uses a compact tab grid.

Checks are grouped into needs-attention and passed. Optional sections do not lower the structure score. Suggestions support a local editable draft, copying, and skipping with undo; they never alter the uploaded PDF. Job matching only appears when the user supplies a job description.

## Theme and accessibility

Semantic OKLCH light and dark tokens live in `web/src/tokens.css`. The first visit follows the operating-system preference, a header control switches themes, and the choice persists locally. Focus states are visible, controls meet touch-target guidance, and reduced-motion preferences are respected.

## Product boundaries

The product supports PDF extraction, resume checks, bullet feedback, job-description comparison, and report download. It does not imply accounts, templates, job URL imports, rewritten-PDF export, or hiring outcomes.

## Implementation

`App.jsx` owns request and session state. `UploadView`, `ResultsView`, and `AppHeader` retain component ownership. `Workspace.css` is the active layout stylesheet; obsolete alternatives and duplicate token exports have been removed.
