<!-- repo-skillopt-meta
canonical_version: 0.1.0
adapter: generic
-->

# RepoSkillOpt — System-prompt activation fragment

Paste the following into your harness's system message (or developer message) so the RepoSkillOpt skill is loaded and activated on the right triggers. Replace `<absolute path>` with the path where you have placed `skill.md`.

```
You have access to a skill called repo-skillopt at <absolute path>/skill.md.

Activate this skill when the user asks to understand, map, document, onboard
to, refactor, modify, or assess a repository (or uses recognizable
equivalents of those verbs). When the skill activates, follow its workflow
verbatim: triage, identify, inspect, map, trace, produce a Repository
Specification with all 19 required sections, and identify risks/unknowns.

Every major claim in the output carries one of these label prefixes:
**[fact]**, **[inference]**, **[unknown]**, or **[human]**. Every
**[fact]** is followed by at least one citation in the form
`path/to/file.ext:line` (or :start-end, or :Symbol). Write working
artifacts under `.reposkillopt/{specs,feedback,rollouts,proposals}/` at
the target repository's root.
```

Verify that the path you reference matches the actual `skill.md` location and that the `canonical_version` in `skill.md` matches the canonical `version:` in the RepoSkillOpt project's `skills/repo-skillopt/SKILL.md`.
