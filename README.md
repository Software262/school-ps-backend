# Backend - School PS

Welcome to the School PS Backend repository. This is the backend for a school payment clearance (Paz y Salvo) system. This document outlines the essential guidelines and conventions for working with this codebase.

---

## 📋 Naming Conventions

**Establish naming conventions from the start to maintain consistency and organization across the project. ALL team members MUST follow these standards.**

### 🌿 Branch Naming

Use clear, descriptive branch names following this pattern:

```
<type>/<description>
```

**Types:**

- `feature/` - New features
- `fix/` - Bug fixes
- `hotfix/` - Critical fixes for production
- `refactor/` - Code improvements without changing functionality
- `docs/` - Documentation updates
- `test/` - Test additions or improvements

**Examples (School Paz y Salvo Context):**

```
feature/student-balance-tracking
feature/payment-verification-endpoint
feature/certificate-generation
fix/balance-calculation-error
fix/payment-status-update
hotfix/certificate-download-issue
refactor/database-queries-optimization
docs/api-endpoints-documentation
test/payment-processing-unit-tests
```

**✅ DO:**

- Use lowercase letters
- Use hyphens to separate words
- Be descriptive and concise
- Reference issue number when applicable: `feature/PS-123-student-balance`

**❌ DON'T:**

- Use underscores or dots
- Use uppercase letters
- Use vague names like `fix/stuff` or `feature/update`
- Use domain-unrelated examples (this is NOT an ecommerce system)

---

### 🔄 Pull Request Workflow

**⚠️ IMPORTANT FOR DEVELOPERS:**

#### PR Submission Rules:

1. **ALL PRs must be submitted to the `develop` branch ONLY** - Never directly to `main` or `master`
2. **Branches are protected** - Direct commits to main/develop are not allowed
3. **CI/CD Checks Required** - Your PR must pass all automated checks before merging:
   - ✅ Tests must pass
   - ✅ Code linting must pass
   - ✅ Build must succeed
   - ✅ Code coverage requirements must be met (if applicable)
4. **Code Review Required** - At least one team member approval is required
5. **Merge Strategy** - Squash and merge or regular merge (as per team policy)

#### PR Title Format:

```
<type>: <description>
```

**Examples:**

```
feat: add student balance tracking endpoint
feat: implement payment verification logic
fix: correct balance calculation for scholarships
fix: resolve certificate generation issue
refactor: optimize database queries for performance
docs: add API documentation for payment endpoints
test: add unit tests for balance service
```

#### PR Template

The PR template is managed in `.github/pull_request_template.md`. When you create a new PR, the template will be automatically populated with the required sections:

- **Description** - Explain what this PR does and why
- **Type of Change** - Select the appropriate change type
- **Related Issues** - Reference any related issues (e.g., `Fixes #123`)
- **Testing** - Describe how you tested your changes
- **Checklist** - Verify all items before requesting review

---

### 📝 Commit Messages

Follow conventional commit format for clear and organized commit history:

```
<type>(<scope>): <subject>
```

**Types:**

- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code restructuring
- `docs:` - Documentation changes
- `test:` - Test additions/modifications
- `style:` - Code style changes (formatting, etc.)
- `chore:` - Build, dependencies, or other maintenance tasks

**Examples (School Context):**

```
feat: add payment status endpoint
feat(auth): implement admin authentication
fix: correct student balance calculation
fix(certificates): resolve PDF generation error
refactor: simplify payment service logic
docs: update API documentation
test: add unit tests for balance service
chore: update dependencies to latest versions
```

**✅ DO:**

- Start with lowercase
- Be concise but descriptive
- Use present tense
- Include scope when relevant
- Link to issues: `fix: resolve balance issue #45`

**❌ DON'T:**

- Write long, verbose messages
- Use past tense
- Mix multiple unrelated changes in one commit

---

## 🎯 Development Workflow

### Step-by-Step Process:

1. **Create Feature Branch**

   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/student-payment-tracking
   ```

2. **Develop and Commit**

   ```bash
   git add .
   git commit -m "feat: add payment tracking system"
   git commit -m "test: add unit tests for payment service"
   ```

3. **Push to Remote**

   ```bash
   git push origin feature/student-payment-tracking
   ```

4. **Create Pull Request**
   - Go to GitHub/GitLab and create PR to `develop` branch
   - Fill in the PR description template
   - Request review from team members

5. **Address Feedback**
   - Wait for CI/CD checks to pass
   - Fix any linting or test errors
   - Respond to code review comments
   - Add commits to address feedback

6. **Merge to Develop**
   - After approval and all checks pass
   - Delete the feature branch

7. **Release to Production**
   - When ready for release, merge `develop` → `main`
   - Tag with version number

---

## 🛡️ Branch Protection Rules

**All branches are protected with the following rules:**

- ✅ **Direct commits are disabled** - Use branches and PRs only
- ✅ **PRs must be reviewed** - At least 1 approval required
- ✅ **CI/CD checks must pass** - All automated tests and builds must succeed
- ✅ **No force pushes** - Prevents accidental history rewrites
- ✅ **Dismiss stale reviews** - New commits dismiss previous approvals

### Protected Branches:

- `main` - Production branch (release only)
- `develop` - Development branch (PRs only)
- All feature branches are read-only until PR is merged

---

## 👥 Team Internal Rules

**These are human rules that complement GitHub's technical protections. GitHub enforces what it can, but team discipline ensures what it can't.**

### Core Team Agreements:

1. **🚫 No one commits directly to `main`**
   - This is absolute. Even if you think you're a maintainer, use a PR
   - Direct commits to `main` may be rejected or reverted

2. **👥 No self-merges - Peer review is mandatory**
   - You **CANNOT** approve and merge your own PR
   - Your PR must be approved by at least one other team member
   - If your team agrees on mandatory cross-review, then EVERYONE needs approval from someone else
   - This ensures fresh eyes on every change

3. **🎫 Every change must come from an issue or task**
   - Before creating a branch, verify there's a corresponding issue/ticket
   - Reference it in your PR title or description: `fix: resolve #45`
   - This maintains traceability and context for future developers

4. **📦 Every PR should be small and focused**
   - One logical intention per PR
   - Easier to review, test, and revert if needed
   - Target: Keep PRs under 400 lines of code changes

5. **🔪 If a PR exceeds the size limit, split it**
   - Large PRs take longer to review and are harder to understand
   - Split into multiple smaller PRs targeting logical features
   - Example: Instead of "feat: complete payment system", split into:
     - `feat: add payment gateway endpoint`
     - `feat: implement payment validation`
     - `feat: add payment success notification`

6. **⚔️ If there are conflicts, the PR author resolves them**
   - It's the author's responsibility to keep their branch updated
   - Before requesting merge, update your branch with `develop`
   - Fix conflicts yourself before asking for review
   - This prevents bottlenecks and keeps the process flowing

7. **👀 Reviewers must actually validate the code**
   - **Don't approve "blindly"** - this defeats the purpose of code review
   - Reviewers should:
     - ✅ Read and understand the code
     - ✅ Run tests locally (when possible)
     - ✅ Verify the changes work as intended
     - ✅ Check for security issues
     - ✅ Ask questions if anything is unclear
   - Approval is a professional commitment, not a checkbox

---

## 🤝 Conflict Prevention & Resolution

**Conflicts are reduced dramatically with discipline and coordination. Here's how to minimize and handle them:**

### Prevention Strategy:

**1. Keep branches short-lived**

- Features should be completed and merged within 1-3 days
- The longer a branch exists, the more likely conflicts arise
- Quick, frequent merges to `develop` reduce integration problems

**2. Always work from the latest `develop`**

- Before starting a branch: `git pull origin develop`
- Before requesting merge: `git pull origin develop` (again)
- Before merging: Ensure your branch is up-to-date
- GitHub can enforce this rule, but manual discipline helps too

**3. Don't leave branches open for days**

- Abandoned branches cause stale PRs
- If you need to pause, communicate it in the PR
- Other developers shouldn't have to wait for your branch

**4. Coordinate if working on related modules**

- If two team members will work on the same file/module, discuss it first via an issue
- Assign tasks clearly in your issue tracker
- Prevent overlapping work before it happens
- Example:
  - Dev A: "I'm doing payment validation logic"
  - Dev B: "I'll do payment endpoint routing"
  - Agreed: Coordinate via PR before merge

### GitHub's Enforcement:

- ✅ **Require branches to be up-to-date before merge** - GitHub setting enabled
- ✅ **This automatically detects conflicts** before entering `main`
- ✅ **Force push disabled** - Prevents accidental history rewrites

### Handling Conflicts When They Occur:

1. **Author receives a conflict notification**

   ```bash
   # Update your branch
   git fetch origin
   git merge origin/develop

   # Manually resolve conflicts (editor will show them)
   # Then commit the merge
   git add .
   git commit -m "merge: resolve conflicts with develop"
   git push origin feature/your-feature
   ```

2. **Review the conflict carefully**
   - Don't just delete code blindly
   - Understand what changed in `develop` vs your branch
   - Test after resolving to ensure nothing broke

3. **Re-request review**
   - Add a comment: "Conflicts resolved, ready for re-review"
   - Wait for approval again if needed

### ⏰ Ideal Workflow Timeline

| Stage     | Time    | Action                  |
| --------- | ------- | ----------------------- |
| Create PR | Day 1   | Open PR, request review |
| Review    | Day 1-2 | Reviewer tests locally  |
| Feedback  | Day 2   | Address comments        |
| Merge     | Day 2-3 | PR merged to `develop`  |
| Close     | Day 3   | Branch deleted          |

**Total time per PR: 1-3 days maximum**

### 🚨 Conflict Resolution Example

Scenario: You and a teammate both modified a core service file

```bash
# 1. Fetch latest
git fetch origin

# 2. Try to rebase
git rebase origin/develop

# Output:
# CONFLICT (content): Merge conflict in src/services/student.service
# error: could not apply abc123... feat: add payment retry logic

# 3. Edit the file, look for markers:
# <<<<<<<< HEAD
# Your changes here
# ========
# Teammate's changes here
# >>>>>>> origin/develop

# 4. Decide what to keep, remove markers:
# Final version with both changes merged properly

# 5. Mark as resolved and continue
git add src/services/student.service
git rebase --continue

# 6. Push (with lease to be safe)
git push origin feature/student-retry --force-with-lease

# 7. PR is now clean and ready to merge
```

### 📋 Conflict Checklist

Before pushing after resolving conflicts:

- [ ] Conflict markers are completely removed
- [ ] Code compiles/lints without errors
- [ ] Tests pass locally
- [ ] Functionality works as expected
- [ ] Both sets of changes are preserved (if applicable)
- [ ] Teammate notified (if their code was involved)

---

## 📊 Quick Reference Guide

| Element   | Pattern                | Example                              |
| --------- | ---------------------- | ------------------------------------ |
| Branch    | `<type>/<description>` | `feature/payment-verification`       |
| Commit    | `<type>: <message>`    | `feat: add balance endpoint`         |
| PR Title  | `<type>: <message>`    | `feat: add student balance tracking` |
| PR Target | Always `develop`       | Never directly to `main`             |

---

## ⚠️ Critical Reminders for All Developers

1. **⛔ NEVER commit directly to main or develop** - Branch protection is enabled
2. **✅ ALL PRs to develop branch ONLY** - PRs to other branches will be rejected
3. **✅ ALL checks must pass** - Failing tests or linting blocks merging
4. **✅ Code review required** - No self-merging, always wait for approval
5. **✅ Use atomic commits** - One logical change per commit
6. **✅ Consistency is mandatory** - No exceptions to naming conventions
7. **❓ Questions?** - Ask the tech lead before pushing

---

## 🚀 Getting Started

### Prerequisites

- Git
- Your preferred development environment setup (tech stack will be defined separately)

### Initial Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd school-ps/backend
   ```

2. **Configure Git**

   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

3. **Create develop branch locally** (if not already present)

   ```bash
   git checkout -b develop origin/develop
   ```

4. **Follow project setup documentation** - Refer to the project's tech-specific setup guide for environment configuration and dependencies

---

## 📝 Notes

- This is a Paz y Salvo (payment clearance) system for schools
- All examples should reflect school/payment context
- Branch protection is in place for safety and quality assurance
- CI/CD pipeline ensures code quality before production
- Technology stack details are documented in separate setup guides

---

## 📞 Support

For questions about this workflow or branch protection rules, reach out to the tech lead or team.

---

**Last Updated:** 2026
**Repository:** School PS Backend
**Team:** Development Team
