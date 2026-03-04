---
name: git-worktree
description: Advanced git worktree management. Create isolated working directories for parallel development on different branches without switching contexts.
metadata:
  openclaw:
    emoji: 🌳
    requires:
      bins:
        - git
    install:
      - id: homebrew
        kind: brew
        formula: git
        bins:
          - git
        label: "Install Git (brew)"
      - id: linux
        kind: apt
        package: git
        bins:
          - git
        label: "Install Git (apt)"
---

## Purpose

Use git worktrees to manage multiple branches simultaneously in separate directories. Work on feature development, hotfixes, and experiments without context switching or stashing changes.

## When to Use

- Develop multiple features in parallel without switching branches
- Create temporary workspaces for testing or experimentation
- Maintain clean working directories for CI/testing
- Review code on one branch while developing on another
- Handle urgent hotfixes without interrupting feature work

## When Not to Use

- Single-branch workflows (use regular git checkout)
- When collaborators expect linear, branched development history
- If your repository has frequent submodule operations

## Setup

### Prerequisites

- Git 2.7+ installed (worktree feature added in 2.7)
- Existing git repository

### Installation

**macOS (Homebrew):**
```bash
brew install git
```

**Linux (apt):**
```bash
sudo apt-get install git
```

**Verify:**
```bash
git worktree --version  # Should show "git version 2.7.0" or later
```

## Commands

### Create Worktree

Create a new worktree for a branch:

```bash
git-worktree create <path> <branch-name>          # Create for existing branch
git-worktree create <path> -b <new-branch>        # Create and branch from HEAD
git-worktree create <path> -b <new-branch> <ref>  # Create branch from specific commit
```

**Use case**: Isolated directory for a feature branch

### List Worktrees

Show all worktrees in the repository:

```bash
git-worktree list
git-worktree list --porcelain  # Machine-readable format
```

**Use case**: See what worktrees exist and their branches

### Switch to Worktree

Navigate to a worktree directory:

```bash
cd $(git-worktree root main)    # Go to main branch worktree
cd $(git-worktree root feature) # Go to feature worktree
```

**Use case**: Move between parallel work contexts

### Remove Worktree

Delete a worktree and its directory:

```bash
git-worktree remove <path>        # Normal removal
git-worktree remove <path> --force # Force removal (loses uncommitted changes)
git-worktree prune                 # Clean up stale worktree data
```

**Use case**: Clean up finished work

### Lock/Unlock Worktree

Prevent accidental operations on a worktree:

```bash
git-worktree lock <path>           # Lock it
git-worktree unlock <path>         # Unlock it
git-worktree lock <path> --reason "Testing hotfix"
```

**Use case**: Protect worktrees from being accidentally pruned

### Get Worktree Path

Find the path to a branch's worktree:

```bash
git-worktree root <branch-name>
```

**Use case**: Script automation, CD into worktrees

## Examples

### Example 1: Parallel Feature Development

```bash
# Main development work on feature branch
git-worktree create ../my-app-feature -b feature/user-auth
cd ../my-app-feature
# ... make changes, test, commit ...

# Switch to main worktree to work on another feature
cd ../my-app-main
git-worktree create ../my-app-payment -b feature/payment-integration
cd ../my-app-payment
# ... work on payment feature in parallel ...

# List all active work
git-worktree list
```

Output:
```
/path/to/my-app       (bare)
/path/to/my-app-feature  feature/user-auth
/path/to/my-app-payment  feature/payment-integration
```

### Example 2: Handle Urgent Hotfix While Working on Feature

```bash
# Currently working on feature
cd ../my-app-feature

# Urgent production bug found, create hotfix worktree
git-worktree create ../my-app-hotfix -b hotfix/critical-bug main
cd ../my-app-hotfix

# Fix the bug
# ... edit, test, commit ...
git push origin hotfix/critical-bug

# Create PR, merge to main
# Once merged, remove the worktree
git-worktree remove ../my-app-hotfix

# Back to feature work
cd ../my-app-feature
```

### Example 3: Code Review in Separate Worktree

```bash
# Maintain clean main branch for review
git-worktree create ../review-branch -b review/pr-123 origin/pr-123
cd ../review-branch

# Review code while others keep working
git log --oneline -10
git diff main

# Once approved, remove
cd ../my-app-main
git-worktree remove ../review-branch
```

### Example 4: Test Multiple Branches in Parallel

```bash
# Test compatibility across branches
git-worktree create ../test-v1 -b release/1.0.x
git-worktree create ../test-v2 -b release/2.0.x

# Run tests in parallel
(cd ../test-v1 && npm test) &
(cd ../test-v2 && npm test) &
wait

# Both test suites run simultaneously without conflicts
```

### Example 5: Automated CI Verification

```bash
#!/bin/bash
# Test current branch and main without switching

WORK_DIR=$(mktemp -d)
MAIN_WORK="$WORK_DIR/main"
FEATURE_WORK="$WORK_DIR/feature"

# Create worktrees for both
git-worktree create "$MAIN_WORK" -b _ci_main main
git-worktree create "$FEATURE_WORK" -b _ci_feature HEAD

# Run tests
(cd "$MAIN_WORK" && npm test) > /tmp/main-tests.log
(cd "$FEATURE_WORK" && npm test) > /tmp/feature-tests.log

# Compare results
if diff /tmp/main-tests.log /tmp/feature-tests.log; then
  echo "Tests consistent"
else
  echo "Test results differ"
fi

# Cleanup
git-worktree remove "$MAIN_WORK" --force
git-worktree remove "$FEATURE_WORK" --force
```

### Example 6: Protected Long-Running Worktrees

```bash
# Create stable worktree for integration tests
git-worktree create ../integration-tests -b integration-suite
git-worktree lock ../integration-tests --reason "Long-running integration tests"

# List shows lock status
git-worktree list

# When done
git-worktree unlock ../integration-tests
git-worktree remove ../integration-tests
```

## Worktree Anatomy

When you create a worktree, git creates:

```
original-repo/
├── .git/
│   ├── worktrees/
│   │   ├── my-feature/
│   │   │   ├── HEAD
│   │   │   ├── index
│   │   │   └── ...
│   │   └── my-hotfix/
│   │       ├── HEAD
│   │       └── ...
│   └── ...
├── worktree1/
│   ├── .git -> .git file (points to main .git)
│   ├── source files...
│   └── ...
└── worktree2/
    ├── .git -> .git file
    ├── source files...
    └── ...
```

Each worktree:
- Has its own working directory
- Shares the main `.git` repository
- Can have different branches checked out simultaneously
- Has independent index and HEAD

## Git Worktree Internals

```bash
# View worktree metadata
cat .git/worktrees/my-feature/gitdir

# Show all tracked files in a worktree
git ls-files ../my-feature-worktree

# Prune stale worktree references
git worktree prune --verbose
```

## Common Issues

### Worktree "locked"

```bash
git-worktree unlock <path>
```

### Stale worktree references

```bash
git worktree prune
git worktree list  # See which are still referenced
```

### Branch already checked out in another worktree

Git prevents checking out the same branch in multiple worktrees:
```
fatal: 'feature/x' is already checked out at '../other-worktree'
```

Solution: Create a new branch or use a different branch name

## Best Practices

1. **Naming Convention**: Use descriptive directory names
   ```bash
   ../my-app-{branch-name}
   ../my-app-{feature}
   ../test-{purpose}
   ```

2. **Keep Main Clean**: Use main/master worktree only for integration
   ```bash
   git-worktree create ../work -b feature/xyz
   # Keep original directory clean for rebase, pull, etc.
   ```

3. **Lock Important Worktrees**: Prevent accidental removal
   ```bash
   git-worktree lock ../stable-test --reason "Nightly test suite"
   ```

4. **Cleanup Regularly**: Remove finished worktrees
   ```bash
   git worktree prune  # Clean up metadata
   ```

5. **Use for Temporary Work**: Great for short-lived tasks
   - Hotfixes
   - Code reviews
   - Testing specific commits
   - Parallel feature work

## Git Worktree vs. Git Clone

| Aspect | Worktree | Clone |
|--------|----------|-------|
| Setup | Fast | Slow (copies objects) |
| Storage | Shared .git | Separate .git |
| Collaboration | Single repo | Independent |
| Submodules | Shared state | Independent |
| Best for | Local parallel work | Distributed teams |

## Notes

- Worktrees share git history; changes in one appear in all
- Use `git push` to share worktree changes with remote
- Deleting a worktree doesn't delete the branch
- Each worktree can have uncommitted changes
- Submodule state is shared across worktrees (may cause issues)
