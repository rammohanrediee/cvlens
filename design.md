# Design — ResumeAI

## Direction
Modern-minimal, functional Workbench. The user explicitly replaced the Long Document direction with a product workspace. The attached brief is a functional sketch, not a pixel template. Green identity stays; cream, continuous report sections and editorial numbering go.

## Shared system
Cool gray canvas, white task surfaces, forest-green actions. IBM Plex Sans leads headings, labels and prose; upright Newsreader appears only in the wordmark and score. Named OKLCH tokens live in tokens.css and web/src/tokens.css. Motion is off; focus and pressed states appear immediately. Navigation: N1 compact two-destination product bar. Footer: Ft2 inline credit. No enrichment or fabricated metrics.

## Upload
Compact product header, three real stages (upload, analysis, review), short heading, PDF attachment area, optional role context and one prominent Analyze resume action. No feature-card marketing grid.

## Results
Document identity and score/priority summary precede a tabbed workspace. Overview, ATS, Suggestions and Keywords are true exclusive tab panels with keyboard navigation. Wide desktop uses a flexible main area and a 17rem context rail; tablet stacks it; mobile uses a compact two-by-two tab selector. Score and priority remain before analysis content.

ATS checks are grouped into needs-attention and passed, with native expandable details. No invented critical severity. Suggestions support selection, an editable local draft, copying and skipping with undo; edits never silently alter the uploaded PDF. On phones, selecting a suggestion opens a full-screen editor with Done and Escape dismissal. Hidden tab panels keep drafts while switching tabs; drafts also survive returning to upload inputs. Reanalysis resets that review's drafts.

## Document and role context
PDF opens in a large native dialog; small screens use a full-screen dialog with an open-document link. No permanent tiny PDF. Role matching uses a pasted job description and the existing backend; no job-URL fetching.

## Product boundaries
Existing PDF extraction, analysis and report contracts stay intact. No accounts, templates, resource pages, job-URL import or rewritten-PDF export are fabricated. The shell exposes Analyze and Job match only. Workflow numbers describe actual stages, not nonexistent automatic improvement. Score labels distinguish structure checks from role similarity and never promise hiring outcomes.

## Implementation and verification
App.jsx owns request/session state. UploadView, ResultsView and AppHeader retain their ownership. Workspace.css is active; previous stylesheets remain unused and are not deleted. Verify 320/375/414/768/1280/1440 widths, tabs, disclosures, local draft interactions, preview, replacement and real upload-to-report flow. Documentation must distinguish verified from pending.

## Exports

### Canonical CSS
```css
/* Hallmark · macrostructure: Workbench (functional app) · genre: modern-minimal
 * design-system: design.md · designed-as-app · theme: custom green product
 * nav: N1 compact two-destination · footer: Ft2 · enrichment: none
 */
:root {
  --color-paper: oklch(97.19% 0.0025 228.78);
  --color-paper-deep: oklch(94.45% 0.0066 160.07);
  --color-surface: oklch(100.00% 0.0000 89.88);
  --color-surface-strong: oklch(98.33% 0.0025 165.08);
  --color-ink: oklch(23.28% 0.0161 160.52);
  --color-ink-soft: oklch(38.29% 0.0284 160.37);
  --color-muted: oklch(49.59% 0.0212 160.51);
  --color-rule: oklch(91.32% 0.0084 157.08);
  --color-rule-strong: oklch(65.55% 0.0261 158.79);
  --color-accent: oklch(47.33% 0.0895 161.01);
  --color-accent-strong: oklch(39.98% 0.0758 160.95);
  --color-accent-soft: oklch(96.15% 0.0083 157.09);
  --color-accent-ink: oklch(100.00% 0.0000 89.88);
  --color-focus: oklch(51% 0.13 45);
  --color-success: oklch(38% 0.08 155);
  --color-success-surface: oklch(94% 0.025 155);
  --color-warning: oklch(47% 0.105 65);
  --color-warning-ink: oklch(38% 0.075 65);
  --color-warning-surface: oklch(95% 0.035 85);
  --color-error: oklch(46% 0.15 28);
  --color-error-surface: oklch(95% 0.022 28);
  --color-info: oklch(40% 0.06 155);
  --color-info-surface: oklch(95% 0.02 155);
  --color-backdrop: oklch(24% 0.018 155 / 0.5);

  --font-display: 'IBM Plex Sans', sans-serif;
  --font-body: 'IBM Plex Sans', sans-serif;
  --font-wordmark: 'Newsreader', 'Times New Roman', serif;
  --space-3xs: 0.25rem;
  --space-2xs: 0.5rem;
  --space-xs: 0.75rem;
  --space-sm: 1rem;
  --space-md: 1.5rem;
  --space-lg: 2rem;
  --space-xl: 3rem;
  --space-2xl: 4rem;
  --space-3xl: 6rem;

  --text-xs: 0.875rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-md: 1.125rem;
  --text-lg: 1.5rem;
  --text-xl: 2rem;
  --text-2xl: 2.5rem;
  --text-display: clamp(1.75rem, 3vw, 2.5rem);
  --text-score: clamp(3.5rem, 6vw, 5rem);
  --radius-control: 0.5rem;
  --radius-card: 0.25rem;
  --radius-panel: 0.75rem;
  --radius-pill: 999px;
  --rule-thin: 1px;
  --rule-strong: 2px;
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in: cubic-bezier(0.7, 0, 0.84, 0);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --dur-micro: 120ms;
  --dur-short: 220ms;
  --dur-long: 420ms;
  --z-base: 1;
  --z-raised: 10;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-modal: 400;
  --z-toast: 500;
  --z-tooltip: 600;
  --page-max: 82rem;
  --page-gutter: clamp(1rem, 4vw, 3rem);
}
```

### Tailwind v4
```css
@theme {
  --color-paper: oklch(97.19% 0.0025 228.78);
  --color-paper-deep: oklch(94.45% 0.0066 160.07);
  --color-surface: oklch(100.00% 0.0000 89.88);
  --color-surface-strong: oklch(98.33% 0.0025 165.08);
  --color-ink: oklch(23.28% 0.0161 160.52);
  --color-ink-soft: oklch(38.29% 0.0284 160.37);
  --color-muted: oklch(49.59% 0.0212 160.51);
  --color-rule: oklch(91.32% 0.0084 157.08);
  --color-rule-strong: oklch(65.55% 0.0261 158.79);
  --color-accent: oklch(47.33% 0.0895 161.01);
  --color-accent-strong: oklch(39.98% 0.0758 160.95);
  --color-accent-soft: oklch(96.15% 0.0083 157.09);
  --color-accent-ink: oklch(100.00% 0.0000 89.88);
  --color-focus: oklch(51% 0.13 45);
  --color-success: oklch(38% 0.08 155);
  --color-success-surface: oklch(94% 0.025 155);
  --color-warning: oklch(47% 0.105 65);
  --color-warning-ink: oklch(38% 0.075 65);
  --color-warning-surface: oklch(95% 0.035 85);
  --color-error: oklch(46% 0.15 28);
  --color-error-surface: oklch(95% 0.022 28);
  --color-info: oklch(40% 0.06 155);
  --color-info-surface: oklch(95% 0.02 155);
  --color-backdrop: oklch(24% 0.018 155 / 0.5);
  --font-display: 'IBM Plex Sans', sans-serif;
  --font-body: 'IBM Plex Sans', sans-serif;
  --font-wordmark: 'Newsreader', 'Times New Roman', serif;
  --spacing-3xs: 0.25rem;
  --spacing-2xs: 0.5rem;
  --spacing-xs: 0.75rem;
  --spacing-sm: 1rem;
  --spacing-md: 1.5rem;
  --spacing-lg: 2rem;
  --spacing-xl: 3rem;
  --spacing-2xl: 4rem;
  --spacing-3xl: 6rem;
  --text-xs: 0.875rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-md: 1.125rem;
  --text-lg: 1.5rem;
  --text-xl: 2rem;
  --text-2xl: 2.5rem;
  --text-display: clamp(1.75rem, 3vw, 2.5rem);
  --text-score: clamp(3.5rem, 6vw, 5rem);
  --radius-control: 0.5rem;
  --radius-card: 0.25rem;
  --radius-panel: 0.75rem;
  --radius-pill: 999px;
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in: cubic-bezier(0.7, 0, 0.84, 0);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
}
```

### DTCG
```json
{
  "color-paper": {
    "$type": "color",
    "$value": "oklch(97.19% 0.0025 228.78)"
  },
  "color-paper-deep": {
    "$type": "color",
    "$value": "oklch(94.45% 0.0066 160.07)"
  },
  "color-surface": {
    "$type": "color",
    "$value": "oklch(100.00% 0.0000 89.88)"
  },
  "color-surface-strong": {
    "$type": "color",
    "$value": "oklch(98.33% 0.0025 165.08)"
  },
  "color-ink": {
    "$type": "color",
    "$value": "oklch(23.28% 0.0161 160.52)"
  },
  "color-ink-soft": {
    "$type": "color",
    "$value": "oklch(38.29% 0.0284 160.37)"
  },
  "color-muted": {
    "$type": "color",
    "$value": "oklch(49.59% 0.0212 160.51)"
  },
  "color-rule": {
    "$type": "color",
    "$value": "oklch(91.32% 0.0084 157.08)"
  },
  "color-rule-strong": {
    "$type": "color",
    "$value": "oklch(65.55% 0.0261 158.79)"
  },
  "color-accent": {
    "$type": "color",
    "$value": "oklch(47.33% 0.0895 161.01)"
  },
  "color-accent-strong": {
    "$type": "color",
    "$value": "oklch(39.98% 0.0758 160.95)"
  },
  "color-accent-soft": {
    "$type": "color",
    "$value": "oklch(96.15% 0.0083 157.09)"
  },
  "color-accent-ink": {
    "$type": "color",
    "$value": "oklch(100.00% 0.0000 89.88)"
  },
  "color-focus": {
    "$type": "color",
    "$value": "oklch(51% 0.13 45)"
  },
  "color-success": {
    "$type": "color",
    "$value": "oklch(38% 0.08 155)"
  },
  "color-success-surface": {
    "$type": "color",
    "$value": "oklch(94% 0.025 155)"
  },
  "color-warning": {
    "$type": "color",
    "$value": "oklch(47% 0.105 65)"
  },
  "color-warning-ink": {
    "$type": "color",
    "$value": "oklch(38% 0.075 65)"
  },
  "color-warning-surface": {
    "$type": "color",
    "$value": "oklch(95% 0.035 85)"
  },
  "color-error": {
    "$type": "color",
    "$value": "oklch(46% 0.15 28)"
  },
  "color-error-surface": {
    "$type": "color",
    "$value": "oklch(95% 0.022 28)"
  },
  "color-info": {
    "$type": "color",
    "$value": "oklch(40% 0.06 155)"
  },
  "color-info-surface": {
    "$type": "color",
    "$value": "oklch(95% 0.02 155)"
  },
  "color-backdrop": {
    "$type": "color",
    "$value": "oklch(24% 0.018 155 / 0.5)"
  },
  "font-display": {
    "$type": "fontFamily",
    "$value": "'IBM Plex Sans', sans-serif"
  },
  "font-body": {
    "$type": "fontFamily",
    "$value": "'IBM Plex Sans', sans-serif"
  },
  "font-wordmark": {
    "$type": "fontFamily",
    "$value": "'Newsreader', 'Times New Roman', serif"
  }
}
```

### shadcn/ui
```css
:root {
  --background: oklch(97.19% 0.0025 228.78);
  --foreground: oklch(23.28% 0.0161 160.52);
  --card: oklch(100.00% 0.0000 89.88);
  --card-foreground: oklch(23.28% 0.0161 160.52);
  --primary: oklch(47.33% 0.0895 161.01);
  --primary-foreground: oklch(100.00% 0.0000 89.88);
  --secondary: oklch(98.33% 0.0025 165.08);
  --secondary-foreground: oklch(23.28% 0.0161 160.52);
  --muted: oklch(94.45% 0.0066 160.07);
  --muted-foreground: oklch(49.59% 0.0212 160.51);
  --accent: oklch(96.15% 0.0083 157.09);
  --accent-foreground: oklch(47.33% 0.0895 161.01);
  --border: oklch(91.32% 0.0084 157.08);
  --input: oklch(65.55% 0.0261 158.79);
  --ring: oklch(51% 0.13 45);
  --destructive: oklch(46% 0.15 28);
  --radius: 0.5rem;
}
```
