"""
Auto-generate data files for knowledge base
"""
from pathlib import Path

def create_file(filepath: str, content: str):
    """Create file with content"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {filepath}")

# Create directories
Path("data/knowledge_base").mkdir(parents=True, exist_ok=True)
Path("data/prompts").mkdir(parents=True, exist_ok=True)

# ============================================
# FILE 1: gucci_context.txt
# ============================================

gucci_context = """# Gucci Group Company Context

## About Gucci Group
Gucci Group is a luxury fashion conglomerate that operates 9 iconic brands:
1. Gucci - Italian luxury fashion house founded 1921
2. Saint Laurent (YSL) - French luxury brand founded 1961
3. Balenciaga - Spanish luxury fashion house founded 1919
4. Bottega Veneta - Italian leather goods brand founded 1966
5. Alexander McQueen - British luxury fashion house founded 1992
6. Brioni - Italian menswear founded 1945
7. Boucheron - French luxury jewelry founded 1858
8. Pomellato - Italian jewelry founded 1967
9. Qeelin - Asian-inspired jewelry founded 2004

## Company Mission
To be the world's leading luxury group, fostering creativity and craftsmanship 
while respecting each brand's unique DNA and heritage.

## Core Values
- Creativity and Innovation: Pushing boundaries in fashion and design
- Excellence and Quality: Uncompromising standards in craftsmanship
- Heritage and Craftsmanship: Honoring traditional techniques
- Sustainability and Responsibility: Environmental and social impact
- Diversity and Inclusion: Global perspectives and representation
"""

create_file("data/knowledge_base/gucci_context.txt", gucci_context)

# ============================================
# FILE 2: competency_framework.txt
# ============================================

competency_framework = """# The 4 Pillars Leadership Framework

## PILLAR 1: VISION
Forward-thinking strategic mindset that anticipates change.

Junior Level: Understands team goals, asks about future direction
Mid Level: Develops strategic plans, communicates vision to inspire
Senior Level: Shapes organizational strategy, influences industry

## PILLAR 2: ENTREPRENEURSHIP
Innovation, calculated risk-taking, and driving change.

Junior Level: Suggests improvements, experiments with new approaches
Mid Level: Leads innovation projects, champions change
Senior Level: Drives transformation, makes bold strategic bets

## PILLAR 3: PASSION
Emotional connection to craft and brand that inspires others.

Junior Level: Shows pride in work quality, demonstrates brand knowledge
Mid Level: Inspires others, tells compelling brand stories
Senior Level: Embodies brand values, cultivates organizational passion

## PILLAR 4: TRUST
Integrity, collaboration, and psychological safety.

Junior Level: Keeps commitments, communicates honestly
Mid Level: Creates safe feedback environment, coaches with empathy
Senior Level: Builds organizational trust, models transparency
"""

create_file("data/knowledge_base/competency_framework.txt", competency_framework)

# ============================================
# FILE 3: hr_best_practices.txt
# ============================================

hr_best_practices = """# HR Best Practices - 360 Feedback

## Rater Selection
- Manager (mandatory)
- 3-5 Peers at same level
- 3-5 Direct reports (for managers)
- Self-assessment

## Survey Design
- 30-50 behavioral questions
- Frequency scales (Never to Always)
- Anonymous peer/direct report responses
- Available in all corporate languages

## Coaching Program
- 6 sessions over 6 months
- 90 minutes each session
- Focus: Process feedback, develop behaviors, measure progress

## Rollout Strategy
Train-the-trainer model: Group HR → Regional leads → Local HR → Brands
"""

create_file("data/knowledge_base/hr_best_practices.txt", hr_best_practices)

# ============================================
# FILE 4: age_adapted_prompts.json
# ============================================

import json

age_prompts = {
    "chro": {
        "age_8_12": {
            "vocabulary_replacements": {
                "competency": "skill",
                "framework": "plan",
                "assessment": "check-up"
            }
        }
    }
}

with open("data/prompts/age_adapted_prompts.json", 'w') as f:
    json.dump(age_prompts, f, indent=2)
print("✅ Created: data/prompts/age_adapted_prompts.json")

# ============================================
# FILE 5: accessibility_prompts.json
# ============================================

accessibility_prompts = {
    "visual_impairment": {
        "acronym_expansions": {
            "HR": "H R",
            "CEO": "C E O"
        }
    }
}

with open("data/prompts/accessibility_prompts.json", 'w') as f:
    json.dump(accessibility_prompts, f, indent=2)
print("✅ Created: data/prompts/accessibility_prompts.json")

print("\n🎉 All data files created successfully!")
