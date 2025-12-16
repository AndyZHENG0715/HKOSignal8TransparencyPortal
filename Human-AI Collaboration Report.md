# Human-AI Collaboration Report
## GCAP 3226: Empowering Citizens through Data

**Student Name:** Hong Kam Yin
**Course:** GCAP 3226
**Date:** November 2025

---

### 1. Executive Summary

Throughout this course, my collaboration with AI tools, specifically Cursor (powered by models like Claude and Gemini) and GitHub Copilot, functioned less like a student-tutor relationship and more like a senior engineer managing a capable but occasionally literal-minded junior developer. Having used generative AI daily since 2023 for computer science tasks, I entered this project with a high degree of familiarity with these tools. However, this project required a shift in my usual workflow. Instead of using AI merely to generate code snippets that I would quickly verify and paste, I adopted a managerial "project responsible" persona. I delegated entire implementation modules—such as the data preprocessing pipeline and the visualization layer—while I retained strict control over the domain logic, specifically the Hong Kong Observatory's (HKO) intricate Signal No. 8 criteria. This partnership allowed me to build a complex transparency portal rapidly, but it also revealed that while AI is an accelerator for implementation, it requires rigorous human oversight for domain-specific logic and edge-case handling.

### 2. AI Usage Overview

My usage of AI tools during this semester can be categorized into three distinct phases: architectural planning, implementation delegation, and critical auditing. Initially, I used Cursor to help structure the project's requirements, transforming the HKO's PDF documentation into a machine-readable Product Requirements Document (PRD). This phase was collaborative; I provided the official standards, and the AI helped formalize them into a 3-tier classification system. As the project moved to implementation, I leveraged the tool's ability to act as an autonomous agent. I issued high-level directives—such as "build a CSV to JSON pipeline" or "create a timeline visualization"—and allowed the AI to draft the Python and JavaScript code. Finally, the usage pattern shifted to rigorous auditing. When discrepancies appeared in the data visualization, specifically regarding the "verification tiers" for typhoons Talim and Ragasa, I used the AI not to write code, but to cross-reference its own logic against the raw data files, effectively treating it as a reasoning engine to debug complex system behavior. This evolution from coder to auditor marked a significant maturity in my engagement with the technology.

### 3. Chat History Portfolio

**Theme 1: Project Management & Role Reversal (The "Architect" Phase)**
*   **Prompt Strategy:** Instead of asking the AI to write code immediately, I assigned it a "Project Responsible" role to prevent context saturation and maintain high-level oversight.
*   **Key Excerpt:**
    > *Me:* "I don't want you to be in charge of implementation, but instead I want you to be my project responsible. I want you to draft prompts to assign tasks to other agents... because when you work on both direction and implementation, your context window will soon be filled and details may be lost."
*   **Annotation:** I asked this because I noticed in previous projects that LLMs lose coherence when juggling too many files. By forcing this separation of concerns, I used the information (task briefs) to direct specific "worker" instances of the AI. This validated my hypothesis that LLMs perform better with narrow, scoped tasks. I learned that managing AI requires treating it like a team of specialists rather than a single generalist.

**Theme 2: Critical Debugging & Logic Validation (The "Auditor" Phase)**
*   **Prompt Strategy:** When visual data (charts) contradicted the expected "Tier" classifications, I didn't ask the AI to "fix it." I asked it to *investigate* the discrepancy between the old and new codebases.
*   **Key Excerpt:**
    > *Me:* "Can you draft a prompt to ask another AI to verify this? I can't trust any AI's one shot now, too stupid that error was. ... Verify if the bug really exists? Or it's both or the new and old algorithm bugged? Can you draft a prompt for another agent with no prior context?"
*   **Annotation:** I asked this because the "verified" status for Typhoon Talim seemed scientifically impossible based on the raw wind data I reviewed. I used the AI's subsequent "investigation report" to confirm that the legacy code was incorrectly counting non-reference stations. This modified our entire deployment strategy—we had to hotfix the old repository immediately before the demo. This taught me that "working code" is not the same as "correct logic."

**Theme 3: Visual QA & Domain Constraints (The "User" Phase)**
*   **Prompt Strategy:** Identifying visual bugs that code linters miss. The AI insisted the chart code was correct, but the visual output was truncating data.
*   **Key Excerpt:**
    > *Me:* "But why am I seeing this? ... [Timestamp logs] ... Can you verify if this is designed to be like this or mistake? If you don't have background feel free to draft me a prompt to ask the AI that was in charge of this."
*   **Annotation:** I asked this to force the AI to look at the *output* (the rendered chart) rather than just the *input* (the JSON data). The AI initially claimed the timeline was fine, but my persistence revealed that the raw CSV files for some typhoons simply stopped early. I validated that this was a data completeness issue, not a rendering bug. I learned that human visual intuition is still far superior to AI self-diagnosis for UI/UX issues.

### 4. Reflection on Human-AI Collaboration

The most distinct aspect of my collaboration was the unique contribution of domain context and visual validation, which the AI could not provide on its own. While the AI was highly proficient at writing Python scripts to parse CSV files, it lacked the "common sense" judgment regarding the Hong Kong Observatory's standards until I explicitly programmed those constraints. For instance, when analyzing the wind data for Typhoon Talim, the AI initially hallucinated a "verified" status in the legacy code because it was counting all weather stations, not just the official eight reference stations. My role was to inject that specific domain constraint—that only the eight reference stations matter—into the AI's reasoning process. Without this human intervention, the project would have produced technically functional code that outputted scientifically invalid results.

Furthermore, I utilized the AI as a reasoning engine to validate its own outputs, a technique that proved crucial for quality assurance. When the chart axes displayed inconsistent time intervals, I challenged the AI to "look" at the data again rather than rewriting the code myself. I asked it to simulate the perspective of a user viewing the chart, which forced the model to break down the rendering logic step-by-step. This dynamic was challenging; it is often frustrating when the AI confidently asserts a falsehood or misses a visual bug that is obvious to a human eye. However, it was also rewarding. By forcing me to articulate *why* a result was wrong, I deepened my own understanding of the underlying data structures. The collaboration was not about the AI replacing my effort, but rather shifting my effort from syntax generation to logic verification. I became the architect and quality assurance lead, while the AI served as the construction crew.

### 5. Learning Outcomes and Transferable Skills

Through this project, I developed a robust skill set in "AI-assisted systems engineering," specifically in the art of prompting for debugging and validation. In familiar domains like pure coding, I found that AI sometimes slowed me down because I would fall into the trap of copy-pasting code I thought I understood, only to spend more time fixing subtle integration errors later. However, in this new domain of meteorological data analysis, the AI significantly accelerated my learning. Because I lacked deep background knowledge in wind patterns, I was forced to read the AI's outputs critically and ask probing questions to verify the results. This taught me that AI is most powerful when used as a tutor in unfamiliar territory, provided one maintains a healthy skepticism. In my future career, I will apply this "managerial" workflow—delegating implementation while retaining strict control over requirements and validation—to tackle large-scale systems that would be too time-consuming to build entirely by hand. I learned that the limitation of AI is not in its coding ability, but in its lack of intent and context; it can build anything, but it doesn't know *what* matters unless a human explicitly tells it.
