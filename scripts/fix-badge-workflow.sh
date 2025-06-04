#!/bin/bash
# Script to fix the build-and-test.yml workflow
# This will replace the problematic badge update section

cat > badge-update-section.txt << 'EOF'
    - name: Update README badge directly
      if: github.ref == 'refs/heads/main' && github.event_name == 'push'
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        echo "Updating README badge directly on main branch..."
        
        # Configure git
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        
        # Create badge URL using shields.io
        BADGE_URL="https://img.shields.io/github/actions/workflow/status/${{ github.repository }}/build-and-test.yml?branch=main&label=tests&style=for-the-badge"
        
        # Check if badge already exists with correct URL
        if grep -q "$BADGE_URL" README.md; then
          echo "Badge already exists with correct URL. No update needed."
          exit 0
        fi
        
        # Update README with badge
        if ! grep -q "<!-- test-status-badge -->" README.md; then
          # Add badge section at the top if it doesn't exist
          CONTENT=$(<README.md)
          {
            echo "<!-- test-status-badge -->"
            echo "[![Tests]($BADGE_URL)](https://github.com/${{ github.repository }}/actions)"
            echo ""
            echo "$CONTENT"
          } > README.md
          echo "Added new badge to README"
        else
          # Update existing badge
          perl -i -pe 's|<!-- test-status-badge -->.*?(?=\n)|<!-- test-status-badge -->\n[![Tests]('$BADGE_URL')](https://github.com/${{ github.repository }}/actions)|s' README.md
          echo "Updated existing badge in README"
        fi
        
        # Check if there are actual changes
        if git diff --quiet README.md; then
          echo "No changes to README.md needed after update attempt"
          exit 0
        fi
        
        # Commit directly to main
        git add README.md
        git commit -m "Update test status badge [skip ci]"
        
        # Push directly to main
        git push origin main || {
          echo "Failed to push badge update. This is not critical."
          echo "The badge will be updated on the next successful push to main."
        }
EOF

echo "Badge update section saved to badge-update-section.txt"
echo ""
echo "To apply this fix:"
echo "1. Edit .github/workflows/build-and-test.yml"
echo "2. Find the 'Create PR for README badge update' step"
echo "3. Replace it with the content in badge-update-section.txt"
echo ""
echo "Or run: sed -i '/- name: Create PR for README badge update/,/fi$/d' .github/workflows/build-and-test.yml"
echo "Then insert the new section from badge-update-section.txt"
