# Issue S12-022: Mermaid Diagram Lightbox with Zoom and Pan

Status: Proposed (Post-Run)
Priority: P2
Sprint: 2026-12
Date Opened: 2026-05-21

## Summary

The current Mermaid diagram preview surface renders diagrams inline at a fixed size.
Complex or large diagrams are unreadable at that size and there is no mechanism for the
analyst to zoom in, pan, or scroll the rendered diagram.

This issue delivers a click-to-expand lightbox/dialog for the Mermaid rendered preview.
When the analyst clicks the diagram preview, a full-viewport dialog opens containing the
rendered diagram with:
- Mouse-wheel zoom in/out.
- Keyboard `+` and `-` zoom in/out.
- Clickable `+` and `-` zoom controls in the dialog.
- Click-and-drag pan.
- Directional scroll controls (up/down/left/right) for non-drag navigation.

The inline preview in the main viewer panel remains unchanged; the dialog is additive.

## Motivation

Large Level 1 or Level 2 Mermaid diagrams rendered inline at panel width are too small
to read component labels, edge annotations, and trust boundary markers. Forcing analysts
to export the diagram and open it in an external viewer breaks workflow context and is not
acceptable for a primary review surface.

## Affected Requirements

- GUI-020 in Requirements/10_GUI_Requirements.md
  (Mermaid Diagram Viewer — must be extended to include the lightbox interaction model)
- GUI-034 in Requirements/10_GUI_Requirements.md
  (Mermaid Multi-Diagram Review Workspace — currently covers selector, split/text modes,
  and position indicator; the lightbox is a new capability on top of this)
- RHMI-010 in Requirements/11_React_HMI_Refactor_Requirements.md
  (React Mermaid viewer requirement — same extension scope as GUI-034)

## Scope

### Click-to-Open Lightbox

- The rendered Mermaid diagram in the preview panel shows a visual affordance (cursor:
  zoom-in or magnifier icon overlay) indicating it is clickable.
- Clicking the preview opens a full-viewport MUI Dialog containing the rendered diagram.
- The dialog has a close button (or Escape key) to dismiss.

### Zoom

- Mouse-wheel scrolling on the diagram zooms in and out smoothly.
- Keyboard `+` and `-` zoom in and out while the dialog is focused.
- Visible `+` and `-` buttons are provided and can be clicked with the mouse.
- Zoom is centered on the cursor position.
- Zoom limits: minimum 25 %, maximum 500 % (or a similar practical range).
- A reset-zoom action or button returns the diagram to fit-to-dialog.

### Pan

- Click-and-drag on the diagram pans the canvas.
- Panning is constrained or allowed to overflow with scroll bars as appropriate for
  the implementation approach.
- Directional pan buttons are provided (`Up`, `Down`, `Left`, `Right`) for users who do
  not want to click-and-drag.

### Out of Scope

- Editing the Mermaid source from within the lightbox (existing split/text mode handles this).
- Saving the zoom/pan state across dialog open/close cycles.
- Touch/pinch-zoom support (desktop-only for this issue).

## Acceptance Criteria

- [ ] Clicking a Mermaid diagram preview opens a full-viewport dialog.
- [ ] The dialog renders the same diagram as the inline preview without quality loss.
- [ ] Mouse-wheel zoom in/out works within the dialog.
- [ ] Keyboard `+` and `-` zoom in/out work while the dialog has focus.
- [ ] Clickable `+` and `-` controls are visible and functional in the dialog.
- [ ] Click-and-drag pan works within the dialog.
- [ ] Directional pan controls (`Up`, `Down`, `Left`, `Right`) are visible and functional.
- [ ] A reset button or double-click returns the diagram to fit-to-dialog (or 100 %).
- [ ] Escape or the close button dismisses the dialog.
- [ ] The inline preview panel is visually unchanged after the dialog is dismissed.
- [ ] The lightbox works for all diagrams available in the selector (Level 0, Level 1, Level 2).

## Implementation Notes

- The zoom/pan interaction can be implemented with a lightweight transform wrapper
  (CSS transform: scale + translate managed by React state + event handlers) rather than
  a full SVG or canvas library, since Mermaid renders SVG inside a div.
- An alternative is to embed the SVG in an `<object>` or `<img>` with overflow scroll;
  however, zoom on SVG requires explicit scale handling.
- The MUI Dialog with `fullScreen` or `maxWidth="xl"` and `fullWidth` provides a suitable
  container.
- Control layout guidance: place zoom (`+`/`-`) and directional controls in a persistent
  control bar so mouse-only users can operate without drag gestures.
- No new npm dependencies are required if a pure React/CSS transform approach is used.
  If a pan/zoom library is considered (e.g., react-zoom-pan-pinch), add a dependency
  review note to the implementation PR.

## Expected Primary Files

- frontend/src/components/ArtifactsViewer.tsx
- frontend/src/components/MermaidLightbox.tsx (new component, or inline in ArtifactsViewer)
- frontend/src/components/ArtifactsViewer.test.tsx
- Requirements/10_GUI_Requirements.md (GUI-020 extension note)

## Validation Plan

- frontend: npm run test -- --run src/components/ArtifactsViewer.test.tsx
- manual: open a completed run with multiple Mermaid diagrams, click each, verify dialog
  opens, verify zoom and pan, verify close returns to inline view unchanged

## GitHub Tracking

- Repository issue: TBD

## Deferment Note

- Implementation is intentionally deferred until the current active pipeline run is complete.
