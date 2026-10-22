---
name: explain-systematically
description: Create concise, temporary HTML explainers with a causal story, ELI5, visual map, and interactive glossary, saved under /tmp by default.
---

# Explain Systematically

This skill makes temporary explainers, not permanent documentation or a website. Use it when someone wants to understand a topic systematically through an HTML lesson. Teach why each idea is needed, how it works, and what question it raises next.

## Orient the learner before the story

Assume a curious beginner unless the user specifies otherwise. Before the tabs and the first story beat, place a compact **Context** block under the page title. In a few short lines, orient the learner: where the topic fits, why it matters, what they should understand by the end, and what prior knowledge (if any) the explanation assumes. Name a useful connection to the surrounding system—what this builds on or what it enables. Leave out items that do not help orient this topic. Keep the block brief; it is a starting map, not another summary or a preamble to the story.

If the explanation relies on a meaningful prerequisite, bridge it briefly before depending on it. If there is none, say so in one short line rather than adding a prerequisite lesson.

## Lead with the short story

Assume a curious beginner unless the user names another audience. Choose one concrete running example and trace the topic in dependency order:

1. Show the real friction or question.
2. Introduce the smallest useful concept as the response.
3. Explain what it solves, then reveal the next limitation.
4. Continue until the main system or idea fits together.

Put this narrative in the first, default **Short story** tab. Write it in the direct, memorable style of a colleague explaining a system at a whiteboard: short paragraphs, plain words, concrete stakes, and explicit cause-and-effect transitions. Aim for about 100–180 words for an ordinary overview, with one to three short sentences per beat; treat that as a guide, not a cap. Let the story run longer when needed to explain a key mechanism or preserve a necessary cause-and-effect step. Keep the causal links; cut repeated definitions, setup prose, marketing language, and tangents. Do not turn it into a jargon list.

Inside the story tab, add a one-sentence setup immediately after the **The story** label and before its opening heading. Name the specific part of the topic and frame the concrete problem behind the opening question. This bridges the page-wide context to the narrative; keep it distinct from the first story beat, and do not answer the question in advance.

When a concrete example or small diagram would clarify a story beat, place it in a supporting column beside that beat on wide screens. Use this selectively; other beats can remain text-only. On narrow screens, stack each visual beneath its associated beat. Keep visuals explanatory rather than decorative, and give each one a concise text equivalent.

Include a small, clearly labeled **ELI5** callout near the start of the story: one or two sentences using a familiar analogy or everyday language to give the learner an instant mental model. Keep the analogy faithful to the mechanism; briefly name its limit when it could mislead. Do not repeat the whole story in simpler words.

## Add a compact visual view

Provide a second tab such as **Visual map** or **How it works**. Use it to show relationships, sequence, or one essential distinction—not to repeat the story as another long essay. Prefer a simple labeled diagram, timeline, or comparison when it makes the mental model faster to grasp. Add brief annotations and, when helpful, one retrieval question with an answer the learner can reveal.

Use the map to make important connections visible: what depends on what, what works together, and what is an alternative. Do not leave the learner with a list of adjacent terms; explain the link between them.

Add a **Glossary** tab after the visual tab. Include only the key terms needed to follow this lesson, usually 4–8. Define each in one short, plain-language sentence; avoid turning it into an encyclopedia. Highlight those same terms when they first matter in the story and visual walkthrough, including a compact recap if present. Each highlighted term must reveal its definition on pointer hover and keyboard focus, and remain usable on touch (focus after tap); the Glossary tab provides the persistent readable definitions. Use a visible highlight treatment and an associated tooltip (`aria-describedby`, `role="tooltip"`) so the definition is available to assistive technology as well as visually. Keep tooltip text concise and ensure it does not obscure essential neighboring content.

Use animation only when it explains change or order, such as a signal moving through a pipeline. Keep it subtle, optional, and useful without motion; honor `prefers-reduced-motion`. Do not animate merely for decoration. Every visual must have a readable text equivalent.

## Keep the lesson accurate and lean

For each core concept, preserve the minimum needed to understand why it exists, how it works, how it connects to neighboring concepts, and its boundary. When the topic affects a practical choice, also say when it is useful and when another approach fits better. Use examples to make an abstract mechanism concrete. Label analogies and their limits. Distinguish a conceptual teaching sequence from actual history; never invent an origin story. Verify current or version-sensitive claims against authoritative sources and link them near the claim.

When explaining a technical tool or workflow, include a short, copyable command or code example when it materially helps the learner use the concept. Briefly explain what each line does. Put review steps before commands that can change or delete real resources, and state their important side effects. Do not force commands into topics where none are useful; verify command syntax and behavior against current official documentation.

Keep the story and visual walkthrough lean; a typical first-pass lesson should stay around 200–350 words before glossary definitions and sources. Go longer only when accuracy requires it or the user requests depth. Keep optional detail behind a reveal control instead of crowding the main path.

## Build the HTML

Create a finished, standalone `.html` file for temporary use. Save every explainer under `/tmp` by default, using a descriptive filename, and provide a clickable link. Do not save generated explainers in the repository or workspace root. If the user explicitly names another output path, honor that path.

The file's temporary storage is an operational detail: do not call it temporary or disposable in the page copy, footer, title, or metadata. Give the explainer a polished, self-contained presentation.

- Use semantic HTML, responsive styling, readable type, visible focus states, and a clear heading hierarchy. Prefer a calm, low-distraction reading palette: warm or neutral light surfaces, dark text, restrained blue or blue-green for structure, and one limited accent color. Prioritize clear contrast over presumed universal color psychology; do not rely on color alone to convey meaning.
- Check contrast in context: colors that work on the page background may fail inside a dark diagram card. Give labels and emphasized terms a readable card-specific color, and keep each diagram label visibly separated from its explanatory text.
- Implement three real, keyboard-accessible tabs—**Short story**, **Visual map**, and **Glossary**—using `tablist`, `tab`, and `tabpanel` semantics, selected state, and arrow keys plus Home/End. Keep all sections readable if JavaScript is unavailable; reveal the tab controls only after the behavior is ready.
- Keep the complete story visible at once; do not add a stepper or story-specific keyboard navigation by default. Use numbered beats, short paragraphs, spacing, and clear cause-and-effect transitions to support comprehension. Add extra navigation only when the user asks for it or the content clearly needs it.
- Keep CSS and any small tab or animation script inline. Avoid libraries, CDNs, and other external assets so the file works offline.
- Make diagrams self-explanatory with labels and a textual description. Keep essential meaning available to screen readers.
- Cite sources with direct links in the HTML. Do not imply a sourced historical timeline when the sequence is only a teaching model.

Give the user a brief note on the lesson's scope. Do not add a long prose recap when the story and visual map already explain the topic.
