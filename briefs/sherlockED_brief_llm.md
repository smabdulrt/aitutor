# SherlockED Widget System - Product Development Brief

## Executive Summary

**SherlockED** is a Python-based educational widget rendering system designed to replicate and extend the functionality of Khan Academy's Perseus platform. Following an MVP-first approach, we will build a minimal viable product using actual Khan Academy questions to validate core concepts and integration before expanding to full Perseus compatibility.
Github Repo: https://github.com/Khan/perseus

**Target**: Create a standalone Python web application that can parse Perseus JSON format and render all widget types with full interactivity, then integrate with the AI Tutor platform.

## Project Vision & Goals

### Primary Goals
1. **Complete Perseus Compatibility**: Support all 36+ Perseus widget types with pixel-perfect rendering
2. **Python-Native Architecture**: Build using modern Python web frameworks (FastAPI + React/Vue frontend)
3. **Extensible Widget System**: Modular architecture allowing easy addition of custom widgets
4. **AI Tutor Integration**: Seamless integration with existing DASH knowledge tracking system

### Success Metrics
- 100% widget type coverage (36+ widgets)
- < 200ms rendering time for complex questions
- Mobile-responsive design (tablet/phone compatibility)
- WCAG 2.1 AA accessibility compliance
- 95% Perseus JSON compatibility

## Technical Architecture Analysis

### Perseus JSON Structure (Reference)
Based on analysis of Khan Academy's Perseus system:

```json
{
  "question": {
    "content": "Question text with [[☃ widget-type id]] placeholders",
    "images": {"url": {"width": 400, "height": 300}},
    "widgets": {
      "widget-type id": {
        "type": "widget-type",
        "graded": true,
        "alignment": "default",
        "options": { /* widget-specific configuration */ },
        "version": {"major": 1, "minor": 0}
      }
    }
  },
  "hints": [
    {
      "content": "Hint text",
      "images": {},
      "widgets": {}
    }
  ],
  "answerArea": {
    "calculator": false,
    "chi2Table": false,
    "periodicTable": false,
    "tTable": false,
    "zTable": false
  }
}
```

### Widget Categories (36+ Identified Types)

#### **Tier 1: Core Input Widgets** (8 widgets)
1. **radio** - Multiple choice (single/multi-select)
2. **numeric-input** - Number entry with validation
3. **input-number** - Basic number input
4. **expression** - Mathematical expression input
5. **free-response** - Text area input
6. **dropdown** - Select from options
7. **matrix** - Matrix/table input
8. **table** - Data table input

#### **Tier 2: Interactive Graphing** (6 widgets)
9. **interactive-graphs** - Advanced graphing tool
10. **grapher** - Function plotting
11. **plotter** - Point/line plotting
12. **number-line** - Number line interactions
13. **image** - Interactive images
14. **label-image** - Image labeling

#### **Tier 3: Categorization & Ordering** (6 widgets)
15. **categorizer** - Drag items into categories
16. **matcher** - Match pairs of items
17. **orderer** - Reorder items in sequence
18. **sorter** - Sort items by criteria
19. **graded-group** - Grouped questions
20. **graded-group-set** - Sets of grouped questions

#### **Tier 4: Specialized Content** (8 widgets)
21. **molecule** - 3D molecular structures
22. **cs-program** - Code execution environment
23. **python-program** - Python code runner
24. **phet-simulation** - Physics simulations
25. **video** - Video player with interactions
26. **iframe** - Embedded content
27. **passage** - Reading comprehension
28. **passage-ref** - Reference to passages

#### **Tier 5: Layout & Presentation** (8+ widgets)
29. **group** - Widget grouping
30. **explanation** - Solution explanations
31. **definition** - Term definitions
32. **interaction** - Custom interactions
33. **measurer** - Measurement tools
34. **deprecated-standin** - Legacy support
35. **passage-ref-target** - Passage targets
36. **mock-widgets** - Testing utilities

## Development Roadmap

### MVP Phase: Proof of Concept & Integration (3-4 weeks)
**Goal**: Create a working prototype using actual Khan Academy questions that renders in both standalone mode and integrates with AI Tutor

#### Sprint MVP.1: Minimal Viable SherlockED System (2 weeks)
**Deliverables**:
- Basic Python FastAPI backend serving actual Khan Academy questions
- Simple React component for widget rendering  
- Support for 5 widget types: `radio`, `numeric-input`, `image`, `dropdown`, `matcher`
- Standalone web application with all 16 Khan Academy questions from `/CurriculumBuilder/khan_academy_json/`

**Implementation Tasks**:
```python
# MVP components to build
/sherlocked/
├── backend/
│   ├── khan_questions_loader.py   # Load from /CurriculumBuilder/khan_academy_json/
│   ├── perseus_parser.py          # Parse Perseus JSON format
│   ├── widget_renderer.py         # Basic widget rendering logic
│   └── main.py                    # FastAPI with /questions endpoint
├── frontend/
│   ├── SherlockEDWidget.tsx       # Main widget component
│   ├── widgets/
│   │   ├── RadioWidget.tsx        # Multiple choice widget
│   │   ├── NumericInputWidget.tsx # Number input widget  
│   │   ├── ImageWidget.tsx        # Static image display widget
│   │   ├── DropdownWidget.tsx     # Dropdown selection widget
│   │   └── MatcherWidget.tsx      # Drag-and-drop matching widget
│   └── App.tsx                    # Standalone application
└── tests/
    └── test_khan_questions.py
```

**Real Khan Academy Questions Analysis**:
Based on analysis of `/CurriculumBuilder/khan_academy_json/` files:
- **numeric-input** (12 instances) - Number input with validation  
- **radio** (8 instances) - Multiple choice questions
- **image** (34+15 instances) - Static image display
- **dropdown** (1 instance) - Dropdown selection
- **matcher** (2 instances) - Drag-and-drop matching between columns

**Unit Tests**:
- [ ] Khan Academy questions load correctly from JSON files
- [ ] Radio widget renders multiple choice options and handles selection  
- [ ] Numeric input accepts numbers and validates against correct answers
- [ ] Image widget displays static images with proper alt text
- [ ] Dropdown widget shows options and handles selection
- [ ] Matcher widget enables drag-and-drop matching between left/right columns
- [ ] Perseus content parsing handles LaTeX math expressions
- [ ] Widget placeholder replacement works with [[☃ widget-type id]] format
- [ ] Answer validation returns correct/incorrect feedback for all widget types

**Acceptance Criteria**:
- [ ] Standalone web app runs on localhost:3000
- [ ] Backend API serves all 16 Khan Academy questions on localhost:8000/questions
- [ ] Displays all question types with 5 widget types functioning correctly
- [ ] User can interact with all widgets and see correct/incorrect feedback
- [ ] Clean, simple UI that resembles Perseus/Khan Academy style
- [ ] LaTeX math expressions render correctly (using MathJax or KaTeX)
- [ ] Images display properly with correct dimensions and alt text
- [ ] Mobile responsive (works on phone/tablet)

#### Sprint MVP.2: AI Tutor Integration (1-2 weeks)
**Target**: Replace existing QuestionDisplay component with SherlockED

**Deliverables**:
- SherlockED React component integrated into AI Tutor frontend
- Bridge between AI Tutor question format and SherlockED format
- Khan Academy questions displaying in AI Tutor question pane
- Answer submission flowing through existing DASH system

**Implementation Tasks**:
```typescript
// Integration components
/aitutor/frontend/src/components/SherlockED/
├── SherlockEDRenderer.tsx         # Replaces QuestionDisplay
├── QuestionFormatBridge.ts        # Converts curriculum.json to Perseus-like format
└── widgets/
    ├── RadioWidget.tsx            # Copy from standalone version
    ├── NumericInputWidget.tsx     # Copy from standalone version
    ├── ImageWidget.tsx            # Copy from standalone version
    ├── DropdownWidget.tsx         # Copy from standalone version
    └── MatcherWidget.tsx          # Copy from standalone version
```

**Integration Tests**:
- [ ] SherlockED component loads in AI Tutor frontend without errors
- [ ] Khan Academy questions display correctly in AI Tutor question pane
- [ ] User interactions trigger AI Tutor's existing answer submission flow
- [ ] DASH system receives and processes answers correctly
- [ ] Navigation between questions works seamlessly
- [ ] No regressions in other AI Tutor functionality

**Acceptance Criteria**:
- [ ] AI Tutor loads with SherlockED replacing old question display
- [ ] All 16 Khan Academy questions render properly in question pane
- [ ] User can answer questions and get correct/incorrect feedback via DASH
- [ ] System integrates with existing user progress tracking
- [ ] MediaMixer and other AI Tutor components continue working
- [ ] Performance is acceptable (no noticeable slowdown)

**MVP Success Metrics**:
- [ ] Standalone SherlockED app demonstrates core concept
- [ ] AI Tutor integration proves technical feasibility  
- [ ] 5 widget types work end-to-end with real user interactions
- [ ] Foundation architecture ready for rapid widget expansion
- [ ] User feedback validates educational value and usability

---

### Phase 1: Perseus JSON Parser & Core Widgets Expansion (4-6 weeks)
**Goal**: Build proper Perseus JSON compatibility and expand widget support

#### Sprint 1.1: Perseus JSON Compatibility (2 weeks)
**Target**: Full Perseus JSON parsing and validation system

**Deliverables**:
- Perseus JSON parser handling real Khan Academy question format
- Widget registry system for extensible widget management
- Support for Perseus content markdown with widget placeholders
- Enhanced LaTeX/MathJax integration

**Unit Tests**:
- [ ] Perseus JSON parsing accuracy (95+ compatibility)
- [ ] Widget registry registration/lookup
- [ ] Complex content rendering with mixed widgets
- [ ] Math expression parsing and rendering

#### Sprint 1.2: Expand Core Widget Set (2-3 weeks)
**Target**: Add 5 more essential widgets

**New Widgets**: `expression`, `input-number`, `free-response`, `categorizer`, `label-image`

**Deliverables**:
- Mathematical expression parsing and validation
- Enhanced drag-and-drop categorization widget
- Image-based interaction widgets
- Text input widgets with validation

**Unit Tests**:
- [ ] Expression widget: Mathematical expression parsing
- [ ] Free response: Text input with character limits
- [ ] Categorizer: Drag items into categories
- [ ] Label-image: Interactive image labeling
- [ ] Input-number: Enhanced number input functionality

#### Sprint 1.3: Advanced Interactions (1-2 weeks)
**Target**: Mobile touch interactions and accessibility

**Deliverables**:
- Touch-friendly drag-and-drop for mobile
- WCAG 2.1 AA accessibility compliance
- Keyboard navigation support
- Screen reader compatibility

**Quality Tests**:
- [ ] Mobile touch interaction support
- [ ] Accessibility testing with screen readers
- [ ] Keyboard navigation functionality
- [ ] Color contrast and focus management

---

### Phase 2: Interactive & Graphical Widgets (6-8 weeks)
**Goal**: Add complex graphing and visualization widgets

#### Sprint 2.1: Interactive Graphing (3-4 weeks)
**Target**: `interactive-graphs`, `grapher`, `plotter`, `number-line`

**Deliverables**:
- Advanced graphing capabilities using plotting libraries (D3.js/Plotly)
- Interactive coordinate system with touch support
- Function plotting and manipulation tools
- Number line interactions

**Unit Tests**:
- [ ] Graph rendering accuracy vs Perseus reference
- [ ] Point plotting and coordinate capture
- [ ] Function graphing with mathematical expressions
- [ ] Mobile touch interaction support for graphs

#### Sprint 2.2: Advanced Categorization (2-3 weeks) 
**Target**: `orderer`, `sorter`, `graded-group`, `graded-group-set`

**Deliverables**:
- Sequence ordering mechanisms
- Advanced sorting interfaces
- Nested question group structures
- Complex validation systems

**Unit Tests**:
- [ ] Order sequence validation
- [ ] Sort criteria accuracy checking
- [ ] Grouped question functionality
- [ ] Nested scoring mechanisms

#### Sprint 2.3: Visual & Media Widgets (2-3 weeks)
**Target**: `video`, `iframe`, `passage`, `passage-ref`

**Deliverables**:
- Video player with educational controls
- Secure iframe embedding system
- Reading passage presentation
- Cross-reference management system

**Unit Tests**:
- [ ] Video playback controls and interaction tracking
- [ ] Iframe security and sandboxing
- [ ] Passage text rendering and highlighting
- [ ] Reference linking accuracy

---

### Phase 3: Specialized & Advanced Widgets (4-6 weeks)
**Goal**: Add domain-specific educational widgets

#### Sprint 3.1: Mathematical Widgets (2-3 weeks)
**Target**: `matrix`, `table`, `measurer`

**Deliverables**:
- Matrix input and validation systems
- Data table input interfaces
- Measurement tools for geometry

**Unit Tests**:
- [ ] Matrix input validation and formatting
- [ ] Table data entry and validation
- [ ] Measurement tool accuracy

#### Sprint 3.2: Science & Programming Widgets (2-3 weeks)
**Target**: `molecule`, `cs-program`, `python-program`, `phet-simulation`

**Deliverables**:
- 3D molecular structure viewer
- Code execution environments (sandboxed)
- Physics simulation embedding
- Code syntax highlighting and validation

**Unit Tests**:
- [ ] 3D molecular rendering accuracy
- [ ] Code execution safety and sandboxing
- [ ] Python code validation and output capture
- [ ] Simulation embedding and interaction

---

### Phase 4: Integration & Polish (4-6 weeks)

#### Sprint 4.1: Advanced AI Tutor Integration (2-3 weeks)
**Target**: Full integration with existing AI Tutor system

**Deliverables**:
- Complete SherlockED component integration in AI Tutor frontend
- DASH system compatibility for all widget types
- Curriculum.json format bridging
- User progress tracking integration

**Integration Tests**:
- [ ] All widget types work in AI Tutor environment
- [ ] Answers process through DASH system correctly
- [ ] Skill tracking updates for all question types
- [ ] User interface maintains consistency

#### Sprint 4.2: Performance & Accessibility (2-3 weeks)
**Deliverables**:
- Performance optimization (caching, lazy loading)
- Full WCAG 2.1 AA compliance across all widgets
- Mobile optimization for all interactions
- Browser compatibility testing

**Quality Tests**:
- [ ] Load times under 200ms for complex questions
- [ ] Accessibility testing with screen readers for all widgets
- [ ] Mobile responsiveness on 5+ devices
- [ ] Cross-browser compatibility (Chrome, Firefox, Safari, Edge)

## Testing Strategy

### Automated Testing Approach

#### Unit Tests (Target: 90% coverage)
```python
# Example test structure for each widget
class TestRadioWidget:
    def test_single_select_functionality(self):
        # Test single selection behavior
        pass
    
    def test_multiple_select_functionality(self):
        # Test multi-select behavior
        pass
    
    def test_perseus_json_compatibility(self):
        # Test parsing Perseus JSON format
        pass
    
    def test_answer_validation(self):
        # Test correct/incorrect answer checking
        pass

class TestMatcherWidget:
    def test_drag_drop_functionality(self):
        # Test drag and drop between columns
        pass
    
    def test_matching_validation(self):
        # Test correct pair matching
        pass
```

#### Integration Tests
- [ ] End-to-end question rendering for all widget types
- [ ] Widget interaction workflows
- [ ] Answer submission and processing through DASH
- [ ] Cross-widget dependencies and interactions

#### Performance Tests
- [ ] Load testing with 100+ concurrent users
- [ ] Memory usage profiling with complex questions
- [ ] Rendering speed benchmarking for all widgets
- [ ] Mobile performance validation

#### Accessibility Tests
- [ ] Screen reader compatibility for all widgets
- [ ] Keyboard navigation support
- [ ] Color contrast validation
- [ ] Focus management testing

### Manual Testing Protocol

#### Phase Acceptance Testing
Each phase requires manual verification:

1. **Widget Functionality Testing**
   - [ ] All widgets render correctly
   - [ ] User interactions work as expected
   - [ ] Mobile touch interactions function properly
   - [ ] Answer validation provides correct feedback

2. **Perseus Compatibility Testing**
   - [ ] Load sample Perseus JSON questions
   - [ ] Verify visual similarity to Khan Academy rendering
   - [ ] Test edge cases and complex question structures
   - [ ] Validate mathematical notation rendering

3. **Integration Testing**
   - [ ] AI Tutor frontend integration
   - [ ] DASH system answer processing
   - [ ] User progress tracking accuracy
   - [ ] System performance under load

## Technical Requirements

### Backend Requirements
```python
# Technology Stack
- Python 3.9+
- FastAPI (high-performance web framework)
- Pydantic (data validation)
- SQLAlchemy (database ORM)
- Redis (caching layer)
- Celery (async task processing)
```

### Frontend Requirements
```javascript
// Technology Stack
- React 18+ (leveraging existing AI Tutor setup)
- TypeScript (type safety)
- Tailwind CSS or Material-UI (styling)
- D3.js or Plotly (data visualization)
- MathJax or KaTeX (math rendering)
- React DnD (drag and drop)
```

### Infrastructure Requirements
- Docker containerization
- PostgreSQL database
- Redis cache
- CDN for static assets
- WebSocket support for real-time interactions

## Risk Assessment & Mitigation

### High-Risk Items
1. **Mathematical Expression Parsing**: Complex math input validation
   - *Mitigation*: Use proven libraries (SymPy, MathJS), extensive testing
   
2. **Mobile Touch Interactions**: Drag-and-drop on mobile devices
   - *Mitigation*: Progressive enhancement, touch-first design
   
3. **Performance with Complex Widgets**: Interactive graphs and simulations
   - *Mitigation*: Lazy loading, caching, performance monitoring

4. **Security with Code Execution**: CS-program and Python-program widgets
   - *Mitigation*: Sandboxed execution environments, strict input validation

### Medium-Risk Items
1. **Browser Compatibility**: Ensuring consistent behavior across browsers
2. **Accessibility Compliance**: Meeting WCAG standards for all widgets
3. **Integration Complexity**: Seamless AI Tutor system integration

## Success Metrics & KPIs

### Technical Metrics
- **Widget Coverage**: 100% of Perseus widget types (36+ widgets)
- **Performance**: < 200ms average rendering time
- **Compatibility**: 95%+ Perseus JSON parsing success rate
- **Test Coverage**: 90%+ automated test coverage

### User Experience Metrics
- **Accessibility**: WCAG 2.1 AA compliance (100%)
- **Mobile Support**: Responsive design on all major devices
- **Browser Support**: Chrome, Firefox, Safari, Edge (latest versions)

### Business Metrics
- **AI Tutor Integration**: Seamless question delivery through SherlockED
- **User Engagement**: Comparable interaction rates to original Perseus
- **System Reliability**: 99.9% uptime during peak usage

## Budget & Resource Allocation

### Development Team Structure
- **1 Senior Python Developer** (Backend architecture, widget logic)
- **1 Frontend Developer** (React/Vue.js, widget UI components)
- **1 Full-Stack Developer** (Integration, testing, deployment)
- **0.5 UX/UI Designer** (Widget design consistency, accessibility)

### Timeline Summary
- **MVP Phase**: 3-4 weeks (Proof of Concept with Khan Academy questions)
- **Phase 1**: 4-6 weeks (Perseus Compatibility & Core Expansion)
- **Phase 2**: 6-8 weeks (Interactive & Graphical Widgets)
- **Phase 3**: 4-6 weeks (Specialized Widgets)
- **Phase 4**: 4-6 weeks (Integration & Polish)

**Total Duration**: 21-30 weeks (5-7.5 months)

## Conclusion

SherlockED represents a significant technical undertaking that will provide the AI Tutor system with world-class educational widget capabilities. The MVP-first approach ensures early validation with real Khan Academy questions, while the phased expansion ensures comprehensive Perseus compatibility.

The comprehensive testing strategy and risk mitigation plans provide confidence in the project's feasibility, while the modular architecture ensures long-term maintainability and extensibility for future educational innovations.

Success will be measured not just by feature completion, but by user engagement and educational effectiveness in the integrated AI Tutor platform.

---

*This brief serves as the definitive guide for SherlockED development and should be reviewed and updated quarterly as the project progresses.*