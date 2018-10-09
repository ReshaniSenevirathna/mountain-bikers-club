# Contributing to Mountain Bikers Club
:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

This project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code. Please report unacceptable
behavior to hello+conduct@mountainbikers.club.

The following is a set of guidelines for contributing to Mountain Bikers Club.
These are just guidelines, not rules, use your best judgment and feel free to
propose changes to this document in a pull request.

## Report a security issue
Found a security issue? Please disclose it responsibly. You can send an email to
hello+security@mountainbikers.club.

## Contributing to translations
- You can found the translation files into the `/locale/` directory.
- English is the default common language, used as keys for the `gettext` tool.
- Edit only the `.po` files and don't change the `msgid` keys even if they
  contain mistakes. It will break the translation system.
- The English language can be improved or corrected in the english `.po` file.
- If you think that the `msgid` is wrong, report it in a new issue. The python
  code and/or the template code need to be modified accordingly.

## Contributing to the code
- The `master` branch is the currently released code running on mountainbikers.club.
  All development should be done in dedicated branches. **Do not submit PRs against
  the `master` branch.** (except during the alpha phase)
- Checkout a topic branch from the relevant branch, e.g. `develop`, and merge back
  against that branch.
- It's OK to have multiple small commits as you work on the Pull Request - we will
  let GitHub automatically squash it before merging.
- If adding new feature, provide convincing reason to add this feature. Ideally
  you should open a suggestion issue first and have it greenlighted before working on it.
- If fixing a bug:
  - If you are resolving a special issue, add `(fix #xxx[,#xxx])` (#xxx is the issue id)
    in your PR title for a better release log, e.g. `update entities encoding/decoding (fix #3899)`.
  - Provide detailed description of the bug in the PR.
  - Add appropriate test coverage if applicable.
  
### Project structure
- `dashbord` is a Django app. It's everything under the `/dashboard/` url.
- `discover` is a Django app. It's everything under the `/discover/` url and
  the home page.
- `locale` is the folder where the translations files are saved and compiled.
- `member` is a Djando app. It's the Django's User management modified for
  Mountain Bikers Club as well as the `/@user`'s pages.
- `mountainbikers` is the Django Project where the site is configured.
- `shell` is a Django app but the main goal is to manage the whole frontend
  (JavaScript and CSS) and the base templates with reusable template tags.
- `trail` is a Django app. It's everything under the `/trail/` url.
  
##  Before Submitting A Bug Report
- Perform a cursory search to see if the problem has already been reported.
  If it has and the issue is still open, add a comment to the existing issue instead
  of opening a new one.
