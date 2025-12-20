# Roadmap

## Hints across formats

### Goal
Support multiple, separate hints per item across all formats with predictable
fallbacks when a format has limited hint support.

### Behavior notes
- QTI 2.1 hints cannot be hidden; they are always available to the learner and
  are commonly rendered as a hint button in LMS interfaces.
- The common request to “ask for a hint instead of submitting an answer” can be
  modeled in QTI 2.1 using the `endAttemptInteraction` path.
- Non-QTI formats should surface hints consistently (for example, a toggle or
  a hint block), even if the underlying format has no formal hint element.

### Plan
1. Add `hints: list[str]` to assessment item data (default `[]`).
2. Validate each hint string as HTML-safe content.
3. Define a stable hint syntax for text-based formats (BBQ/text2qti).
4. Writers:
   - QTI 1.2: map hints to item feedback or the closest available structure.
   - QTI 2.1: map hints to modal feedback / interaction-linked feedback; always
     visible as per spec.
   - HTML self-test: add a hint toggle per item.
   - Human-readable: render a labeled hint block.
5. Readers:
   - Parse hints when present and store them in `hints`.
6. Add smoke tests for round-tripping items with multiple hints.

### References
- QTI 2.1 spec: [1EdTech QTI 2.1](https://www.1edtech.org/standards/qti/index#QTI21)
- QTI 1.2 spec: [1EdTech QTI 1.2](https://www.1edtech.org/standards/qti/index#QTI%201.2)
- QTI 2.1 hint path: [endAttemptInteraction element](https://www.imsglobal.org/question/qtiv2p1/imsqti_infov2p1.html#element10402)

### Risks
- Hints in QTI 2.1 cannot be hidden; some LMS UI behavior may differ.
- Text formats may lose hint granularity unless a strict syntax is enforced.

### Open questions
- Should hints affect CRC / uniqueness of items?
- Should hints include optional “cost” or scoring metadata?
- Preferred hint syntax for BBQ and text2qti inputs?

## Feedback across formats

### Goal
Support overall feedback plus per-choice/distractor feedback with predictable
fallbacks when a format cannot represent all feedback types.

### Plan
1. Add optional feedback fields to item data:
   - `feedback_correct` and `feedback_incorrect`.
   - `choice_feedback` for MC/MA (keyed by choice text or a stable choice id).
2. Validate feedback strings for HTML safety and minimum content.
3. Define a stable feedback syntax for text-based formats (BBQ/text2qti).
4. Writers:
   - QTI 1.2: map to `itemfeedback` and `respcondition` where available.
   - QTI 2.1: map to `modalFeedback` and response processing outcomes.
   - HTML self-test: render per-choice and overall feedback in the UI.
   - Human-readable: render labeled feedback blocks.
5. Readers:
   - Parse per-choice feedback when present and store it in the item model.
6. Add smoke tests that round-trip per-choice feedback for MC/MA.

### Risks
- Some formats/LMSes may ignore per-choice feedback.
- Choice text keys can break if choices are transformed; consider stable IDs.
- Mixed feedback types need a clear precedence rule.

### Open questions
- Should feedback keys be stable IDs rather than choice text?
- Should per-choice feedback apply per selection in MA or as a combined response?
