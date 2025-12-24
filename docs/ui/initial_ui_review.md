# UI Review (Current Screenshot)

These notes are based on the current desktop UI screenshot and focus on clarity, hierarchy, and feedback.

## What Works
- Clear left navigation with recognizable icons and labels.
- Overall layout is simple and easy to scan.
- Primary flow (select file -> process -> results) is straightforward.

## Issues Observed
- Low contrast on headings and drop-zone text makes the main intent hard to read.
- The "Saved to ..." line is visually heavy and competes with the primary actions.
- Drop-zone looks disabled; it needs stronger affordance for click/drag.
- Button hierarchy is unclear: "Browse Video" and "Process Video" have similar weight.
- Results card and header are low contrast; it reads as disabled or inactive.
- Sidebar and content backgrounds are close in value but not aligned, which feels slightly unintentional.

## Suggested Adjustments
### Typography and Contrast
- Increase heading contrast (use a darker neutral for titles).
- Use a medium neutral for secondary text, not a very light lavender/grey.
- Reserve accent color for small highlights and active states.

### Drop-Zone
- Increase border contrast and give a subtle hover state.
- Darken the icon and primary drop-zone label.
- Long file names should wrap or truncate with an ellipsis.

### Buttons
- Make "Process Video" the single primary action (filled, strongest contrast).
- Make "Browse Video" secondary (outline or text).
- Consider spacing to separate "Browse" from the primary CTA to reduce confusion.

### Save Feedback
- Keep the UI on the same screen.
- Show a smaller confirmation line with the file name, not the full path.
- Add a small "Open" or "Reveal in Finder" action for quick access.
- Keep full path in tooltip or copy action if needed.

### Results Area
- Use a clearer "Results" header (higher contrast).
- Give the results container a subtle card background and padding.
- Hide or collapse results when empty to reduce visual noise.

## Optional Enhancements
- Add a progress state with a subtle spinner or animated progress text.
- Consider a summary pill at the top of results with key stats (elapsed time, cost).
- Add a small file badge near the title to reinforce the selected file.
