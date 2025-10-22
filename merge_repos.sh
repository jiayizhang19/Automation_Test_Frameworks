#!/bin/bash
set -e  # Exit immediately on error

# === CONFIGURATION ===
TARGET_REPO_URL="https://github.com/jiayizhang19/Automation_Test_Frameworks.git"
REPOS=(
    "https://github.com/jiayizhang19/Selenium_Pytest_Framework.git"
    "https://github.com/jiayizhang19/Requests_Pytest_Framework.git"
    "https://github.com/jiayizhang19/Airtest_Pytest_Framework.git"
    "https://github.com/jiayizhang19/browser_use_test_automation.git"
    "https://github.com/jiayizhang19/Selenium_TestNG_Framework.git"
)
# ======================

echo "🚀 Cloning target repository..."

# Clean up any existing local folder
if [ -d "Automation_Test_Frameworks" ]; then
    echo "🧹 Removing old Automation_Test_Frameworks folder..."
    rm -rf Automation_Test_Frameworks
fi

git clone "$TARGET_REPO_URL" Automation_Test_Frameworks
cd Automation_Test_Frameworks

# Ensure at least one branch exists
if ! git rev-parse --verify main >/dev/null 2>&1; then
    if git rev-parse --verify master >/dev/null 2>&1; then
        git checkout master
        git branch -M main
    else
        echo "⚙️ No main or master branch found, creating main..."
        git checkout --orphan main
        git commit --allow-empty -m "Initial empty commit"
    fi
fi

git checkout main

# Merge each repo one by one
count=0
for REPO in "${REPOS[@]}"; do
    FOLDER_NAME=$(basename "$REPO" .git)
    echo "=============================="
    echo "🔄 Merging $REPO into $FOLDER_NAME"
    echo "=============================="

    git remote add "temprepo$count" "$REPO"
    git fetch "temprepo$count"

    git checkout -b "temprepo$count-branch" "temprepo$count/master" || \
    git checkout -b "temprepo$count-branch" "temprepo$count/main" || \
    { echo "❌ Could not find main/master in $REPO"; continue; }

    mkdir -p "$FOLDER_NAME"

    # ✅ Move all files (including hidden) except .git into the folder
    find . -mindepth 1 -maxdepth 1 ! -name ".git" ! -name "$FOLDER_NAME" -exec mv {} "$FOLDER_NAME"/ \;

    git add .
    git commit -m "Move $REPO files into $FOLDER_NAME"

    git checkout main
    git merge --allow-unrelated-histories -m "Merge $REPO into main" "temprepo$count-branch"

    git remote remove "temprepo$count"
    count=$((count+1))
done

echo "✅ All repositories merged successfully!"

# === 🪄 AUTO PUSH TO GITHUB ===
echo "🚀 Pushing merged changes to GitHub..."
git push -u origin main
echo "✅ All repositories are now live on GitHub!"

