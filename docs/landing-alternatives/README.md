# Landing page alternatives

`rak-redesign-index.html` is the landing page as it stood at commit `7c297a9`, before
Shantanu's globe hero (`cf2465d`) replaced it on 2026-09-06. It is kept here as a plain file so
it can be read without git.

The same page, with the whole of that session's work around it, is on the branch
`backup/rak-landing-redesign`. To put it back:

    git checkout backup/rak-landing-redesign -- web/index.html

What it was: a 1320 px shell, a full-bleed hero on a chrome-free water render, the hero built
around the 0.19 / 1.01 residual comparison rather than a metric strip, a snapping rail of 14
feature cards each opening one shared dialog, and no section eyebrows.

Nothing in this folder is part of the build. `vite.config.ts` names its four entries explicitly.
