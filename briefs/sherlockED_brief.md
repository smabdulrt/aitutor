\\\\ MOST IMPORTANTLY: The LLM brief that has been created, and attached with this brief, is for outline only. The developer should read through it, agree / disagree with it, eventually own it. We have not written this document, an LLM has, and therefore, him doing his diligence is key. \\\\


# SherlockED Widget System - TLDR Brief

## What is SherlockED?
A Python-based system that renders Khan Academy-style interactive educational questions. Think of it as our own version of Khan Academy's Perseus platform that will integrate seamlessly with the AI Tutor.
Github Repo: https://github.com/Khan/perseus

## The Plan: MVP First, Then Expand

### MVP Phase (3-4 weeks) 🚀
**Goal**: Prove the concept works with real questions

**What we'll build**:
- Standalone web app that displays your actual 16 Khan Academy questions
- 5 widget types that cover 100% of your current questions:
  - `radio` - Multiple choice (8 questions)
  - `numeric-input` - Number entry (12 questions) 
  - `image` - Static images (49 instances)
  - `dropdown` - Select options (1 question)
  - `matcher` - Drag-and-drop matching (2 questions)
- Integration with AI Tutor's question pane (replaces current QuestionDisplay)

**Success looks like**:
- ✅ All 16 Khan Academy questions render perfectly
- ✅ Students can interact and get correct/incorrect feedback
- ✅ Works inside AI Tutor with existing DASH skill tracking
- ✅ LaTeX math expressions display properly
- ✅ Mobile-friendly interface

### After MVP: Full Perseus Compatibility

#### Phase 1: Core Expansion (4-6 weeks)
Add 5 more essential widgets: `expression`, `free-response`, `categorizer`, `label-image`, `input-number`

#### Phase 2: Interactive Graphics (6-8 weeks) 
Add graphing widgets: `interactive-graphs`, `grapher`, `plotter`, `number-line`

#### Phase 3: Specialized Widgets (4-6 weeks)
Add advanced widgets: `matrix`, `molecule`, `cs-program`, `video`, etc.

#### Phase 4: Polish & Integration (4-6 weeks)
Performance optimization, accessibility, full AI Tutor integration

## Technical Stack
- **Backend**: Python + FastAPI (serves questions from your JSON files)
- **Frontend**: React + TypeScript (leverages existing AI Tutor setup)
- **Math**: MathJax/KaTeX for LaTeX expressions
- **Interactions**: React DnD for drag-and-drop

## Why This Approach?
1. **Immediate Value**: MVP uses your real questions, not dummy data
2. **Risk Reduction**: Proves integration works before building 36+ widgets  
3. **Fast Feedback**: See results in 3-4 weeks vs 6+ months
4. **Incremental Growth**: Each phase adds more capability

## Timeline
```
MVP Phase:     3-4 weeks   ←  You get working system with your questions
Phase 1:       4-6 weeks   ←  Core widget expansion
Phase 2:       6-8 weeks   ←  Interactive graphics  
Phase 3:       4-6 weeks   ←  Specialized widgets
Phase 4:       4-6 weeks   ←  Polish & optimization
─────────────────────────
Total:         21-30 weeks (5-7.5 months)
```

## Success Metrics
- **MVP**: All your Khan Academy questions work in AI Tutor
- **Phase 1**: 10+ widget types supported
- **Phase 2**: Interactive graphing capabilities
- **Phase 3**: 30+ widget types (full Perseus compatibility)
- **Phase 4**: < 200ms load times, accessibility compliant

## Team Needed
- 1 Senior Python Developer (backend, widget logic)
- 1 Frontend Developer (React components)
- 1 Full-Stack Developer (integration, testing)
- 0.5 UX/UI Designer (design consistency)

## Key Benefits
- **Educational Quality**: Pixel-perfect rendering like Khan Academy
- **AI Tutor Integration**: Seamless with existing DASH system
- **Extensible**: Easy to add new widget types
- **Mobile-Friendly**: Works on all devices
- **Real Questions**: Uses actual Khan Academy content from day one

## Bottom Line
SherlockED gives AI Tutor world-class question rendering capabilities. The MVP approach means you'll see real value with your actual questions in just 3-4 weeks, with a clear path to full Perseus compatibility over 5-7 months.

---

\\\\ MOST IMPORTANTLY: The LLM brief that has been created, and attached with this brief, is for outline only. The developer should read through it, agree / disagree with it, eventually own it. We have not written this document, an LLM has, and therefore, him doing his diligence is key. \\\\
