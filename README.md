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

#### PR Description Template:

```markdown
## Description

Brief description of what this PR does and why.

## Type of Change

- [ ] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Related Issues

Fixes #123

## Testing

Describe the tests you performed and how to verify them.

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] All new and existing tests pass
- [ ] No new warnings generated
```

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
- `style:` - Code style changes (formatting, semicolons, etc.)
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
7. **❓ Questions?** - Ask the full-stack before pushing

---

## 🚀 Getting Started

### Prerequisites

- Git

### Installation

```bash
git clone <repository-url> backend
cd school-ps/backend
```

---

## 📝 Notes

- This is a Paz y Salvo (payment clearance) system for schools
- All examples should reflect school/payment context
- Branch protection is in place for safety and quality assurance
- CI/CD pipeline ensures code quality before production

---

**Last Updated:** 2026
**Repository:** School PS Backend
**Team:** Development Team
