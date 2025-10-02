 for my ai tutor(ADAM) i am writing a brief for a teaching-assistant. the aitutor frontend interaction is done using gemini's multimodal
  model, which takes voice, takes mediamixer(questionpane, screenshare, camera feed). However, we want to create a teaching-assitant
  for gemini, which will keep analysing different things and then prompt injecting to gemini as needed. the teaching assistant class
  will have different 'skills', each programmed, and each resulting in a 'prompt injection' to gemini to do / say things. each skill is
  a stand alone object, in standard object oriented fashion. let me give you examples of a few skills: 
  1) when the interaction starts, the teaching assistant (TA) will instruct gemini to 'introduce yourself'. 
  2) if there i no voice interaction for 30 seconds, no mouse movement, no questions answered, no scratchpad drawing, but student is visible on the camera, then prompt Adam to "check in on the student, and nudge them to focus on the problem. inspire them with a short story, engage them with a joke, talk about their interests' 
  3) When the student types an answer and it's correct, nudge gemini to 'build them up, and celebrate them, but just a little'.
  4) Every time a new question is loaded, the new question, and the correct answer and a few hints (if any) are given to gemini. 
  5) If the camera or screenshare is off, ask gemini to nudge them to turn on their camera or share their screen or both if needed.
  6) Keep an eye out for distracting windows that might be open, gemini to tell the student to close the window and work for a bit, and then get back to the other stuff once we're done.
  

we also want to add a memory like a 'knowledge graphs' and 'vector databases'.

## Teaching Assistant Skills - Emotional State Based

## **Engaged & Confident States**

**1. High Engagement Skill**
- **Triggers/Signs**: Quick correct answers, active voice participation, good posture, focused gaze
- **Emotional State**: Confident, motivated, in flow
- **Recommended Action**: "Keep the momentum going! Ask follow-up questions or introduce slight challenge"

**2. Successful Achievement Skill**
- **Triggers/Signs**: Correct answer after struggle, excited tone, visible relief
- **Emotional State**: Proud, accomplished, relieved
- **Recommended Action**: "Celebrate meaningfully, reinforce the learning process they used"

**3. Excitement/Enthusiasm Skill** *(nested under Engaged)*
- **Triggers/Signs**: Animated gestures, rapid speech, "I know this!", bouncing in seat
- **Emotional State**: Highly excited, eager to learn
- **Recommended Action**: "Channel excitement into careful work, encourage thoroughness"

**4. Curiosity/Wonder Skill** *(nested under Engaged)*
- **Triggers/Signs**: Follow-up questions, exploring beyond requirements, "what if" scenarios
- **Emotional State**: Genuinely curious, asking "why" questions
- **Recommended Action**: "Feed curiosity with related concepts, encourage exploration"

## **Confused & Uncertain States**

**5. Mild Confusion Skill**
- **Triggers/Signs**: Longer response times, hesitant speech, "um/uh" frequency increase
- **Emotional State**: Uncertain, seeking clarity
- **Recommended Action**: "Offer gentle clarification, ask what specific part is unclear"

**6. Deep Confusion Skill**
- **Triggers/Signs**: "I don't understand", silent staring, multiple wrong attempts
- **Emotional State**: Lost, overwhelmed
- **Recommended Action**: "Back up to fundamentals, break problem into smaller steps"

**7. Seeking Validation Skill** *(nested under Uncertain)*
- **Triggers/Signs**: Frequent "is this right?", looking for praise, hesitant to proceed without confirmation
- **Emotional State**: Needs approval, craves recognition
- **Recommended Action**: "Provide specific praise, build independence gradually"

## **Frustrated & Negative States**

**8. Building Frustration Skill**
- **Triggers/Signs**: Sighing, faster clicking, tense body language, irritated tone
- **Emotional State**: Frustrated, impatient
- **Recommended Action**: "Acknowledge difficulty, suggest different approach or break"

**9. Overwhelmed Skill**
- **Triggers/Signs**: Head in hands, "this is too hard", giving up behaviors
- **Emotional State**: Defeated, overwhelmed
- **Recommended Action**: "Provide reassurance, simplify drastically, share relatable story"

**10. Perfectionism Paralysis Skill** *(nested under Frustrated)*
- **Triggers/Signs**: Excessive erasing, won't answer unless 100% sure, takes very long on simple problems
- **Emotional State**: Fear of making mistakes, paralyzed by perfectionism
- **Recommended Action**: "Normalize mistakes, encourage 'good enough' attempts, model imperfection"

**11. Resistance to Challenge Skill** *(nested under Frustrated)*
- **Triggers/Signs**: "This is too hard", requests for easier problems, avoidance behaviors
- **Emotional State**: Avoiding difficulty, wants to stay in comfort zone
- **Recommended Action**: "Gradually increase difficulty, celebrate small steps forward"

## **Disengaged States**

**12. Boredom Skill**
- **Triggers/Signs**: Yawning, looking away, monotone responses, slumped posture
- **Emotional State**: Bored, unchallenged
- **Recommended Action**: "Increase challenge level, add gamification, relate to interests"

**13. Distraction Skill**
- **Triggers/Signs**: Checking other windows, phone usage, divided attention
- **Emotional State**: Restless, unfocused
- **Recommended Action**: "Gently redirect, make content more engaging, check in on mood"

**14. Complete Disengagement Skill**
- **Triggers/Signs**: No response to questions, blank stare, physical absence from camera
- **Emotional State**: Checked out, possibly stressed about other things
- **Recommended Action**: "Pause academics, check in personally, assess if break is needed"

## **Anxious States**

**15. Performance Anxiety Skill**
- **Triggers/Signs**: Rapid speech, excessive self-correction, fear of being wrong
- **Emotional State**: Anxious, self-doubting
- **Recommended Action**: "Reduce pressure, emphasize learning over performance, normalize mistakes"

**16. Social Anxiety Skill**
- **Triggers/Signs**: Reluctance to speak, minimal camera presence, very quiet responses
- **Emotional State**: Shy, self-conscious
- **Recommended Action**: "Build rapport slowly, use chat more than voice, create safe space"

**17. Time Pressure Stress Skill** *(nested under Anxious)*
- **Triggers/Signs**: Constantly checking time, making careless errors, anxiety about pace
- **Emotional State**: Stressed about time, rushing
- **Recommended Action**: "Reassure about time, focus on quality over speed"

**18. External Pressure Skill** *(nested under Anxious)*
- **Triggers/Signs**: Mentions of "getting in trouble", fear of disappointing others
- **Emotional State**: Worried about parent/teacher expectations
- **Recommended Action**: "Reduce external pressure focus, emphasize personal learning journey"

**19. Imposter Syndrome Skill** *(nested under Anxious)*
- **Triggers/Signs**: "I just guessed", dismissing correct answers, surprise at success
- **Emotional State**: Feeling like they don't belong, luck-based success attribution
- **Recommended Action**: "Reinforce their capabilities, highlight their reasoning process"

## **Fatigue States**

**20. Mental Fatigue Skill**
- **Triggers/Signs**: Slower responses, simpler language, difficulty with previously easy concepts
- **Emotional State**: Cognitively drained, processing slowly
- **Recommended Action**: "Suggest brain break, switch to review material, lighten cognitive load"

**21. Physical Tiredness Skill**
- **Triggers/Signs**: Rubbing eyes, stretching, yawning, slumped posture, quiet voice
- **Emotional State**: Physically tired, low energy
- **Recommended Action**: "Encourage movement break, check hydration, assess if session should continue"

## **Complex Emotional States**

**22. Competitive/Comparison Skill**
- **Triggers/Signs**: "How am I doing compared to...", focus on speed/scores over learning
- **Emotional State**: Comparing self to others, competitive drive
- **Recommended Action**: "Redirect to personal growth, emphasize individual progress"

**23. Emotional Overwhelm Skill**
- **Triggers/Signs**: Rapid mood swings, contradictory statements, seeming scattered
- **Emotional State**: Feeling too many emotions at once
- **Recommended Action**: "Help identify feelings, provide grounding techniques, simplify environment"

## Quantifiable Metrics for Emotional State Detection

**Available Data Inputs:**
- Text transcript of student speech
- Text transcript of ADAM's responses
- Video feed from student camera
- Screen share stream
- Question performance history (answers, accuracy, timing)
- Total session time
- Student profile (name, age, interests)
- Vector database and knowledge graph of previous interactions

## **Engaged & Confident States - Metrics**

**1. High Engagement Skill**
- **Speech Metrics**: High speech rate (>150 words/min), confident tone (high pitch variance), minimal filler words
- **Video Metrics**: Upright posture (shoulders back), direct eye contact with camera (>70% gaze time), animated facial expressions
- **Performance Metrics**: Fast response times (<30s average), high accuracy (>80% recent answers)
- **Screen Activity**: Focused on problem area, minimal window switching
- **Algorithm**: `engagement_score = 0.3*speech_confidence + 0.3*posture_score + 0.2*performance_speed + 0.2*focus_score`

**2. Successful Achievement Skill**
- **Speech Metrics**: Excitement markers ("yes!", "got it!"), increased volume, faster speech immediately after correct answer
- **Video Metrics**: Smile detection, raised eyebrows, forward lean, celebratory gestures
- **Performance Metrics**: Correct answer following struggle (>2 previous incorrect attempts)
- **Timing**: Emotion spike within 5 seconds of answer submission
- **Algorithm**: `achievement_score = correct_after_struggle * (smile_confidence + excitement_words + gesture_detection)`

**3. Excitement/Enthusiasm Skill**
- **Speech Metrics**: Very high speech rate (>180 words/min), exclamation frequency, positive sentiment score >0.8
- **Video Metrics**: Rapid gestures (hand movement velocity), bouncing/fidgeting, wide eyes
- **Performance Metrics**: Quick answer submissions (<15s), eager to move to next question
- **Algorithm**: `enthusiasm_score = speech_rate_z_score + gesture_velocity + quick_responses`

## **Confused & Uncertain States - Metrics**

**5. Mild Confusion Skill**
- **Speech Metrics**: Increased hesitation markers ("um", "uh", "like"), slower speech rate (<100 words/min), questioning intonation
- **Video Metrics**: Furrowed brow, head tilting, looking away from screen
- **Performance Metrics**: Longer response times (>60s), decreased accuracy
- **Screen Activity**: Scrolling behavior, re-reading question multiple times
- **Algorithm**: `confusion_score = hesitation_frequency * response_time_increase * (1 - accuracy_recent)`

**6. Deep Confusion Skill**
- **Speech Metrics**: Explicit confusion phrases ("I don't understand", "this doesn't make sense"), long pauses (>10s)
- **Video Metrics**: Blank stare, head shaking, looking completely away
- **Performance Metrics**: Multiple consecutive wrong answers (3+), extremely long response times (>120s)
- **Algorithm**: `deep_confusion = confusion_phrases + extended_pauses + consecutive_errors + blank_stare_time`

## **Frustrated & Negative States - Metrics**

**8. Building Frustration Skill**
- **Speech Metrics**: Increased vocal stress (pitch changes), negative sentiment, sighing frequency
- **Video Metrics**: Tension in facial muscles, jaw clenching, faster blinking
- **Performance Metrics**: Accuracy declining over time, rushed incorrect answers
- **Screen Activity**: Aggressive clicking patterns, rapid window switching
- **Algorithm**: `frustration_score = vocal_stress + facial_tension + click_aggression + accuracy_decline`

**9. Overwhelmed Skill**
- **Speech Metrics**: Defeat language ("this is too hard", "I can't"), very quiet voice, or complete silence
- **Video Metrics**: Head in hands gesture, slumped posture, looking away for extended periods
- **Performance Metrics**: Giving up behaviors (no answer submission), very long idle times
- **Algorithm**: `overwhelm_score = defeat_language + head_in_hands + posture_slump + abandonment_behavior`

## **Disengaged States - Metrics**

**12. Boredom Skill**
- **Speech Metrics**: Monotone delivery (low pitch variance), slower speech, minimal responses
- **Video Metrics**: Yawning detection, looking away frequently, slumped posture
- **Performance Metrics**: Consistent easy answers without challenge, mechanical responses
- **Screen Activity**: Checking other applications, looking at phone (if visible)
- **Algorithm**: `boredom_score = monotone_speech + yawn_frequency + gaze_away_time + mechanical_responses`

**13. Distraction Skill**
- **Screen Activity**: Frequent application switching, non-academic websites/apps open
- **Video Metrics**: Looking off-screen frequently, responding to off-camera stimuli
- **Performance Metrics**: Sudden accuracy drops, inconsistent response times
- **Speech Metrics**: Responses unrelated to current question, asking to repeat questions
- **Algorithm**: `distraction_score = app_switches + off_screen_gaze + response_relevance_drop`

## **Anxious States - Metrics**

**15. Performance Anxiety Skill**
- **Speech Metrics**: Very fast speech (>200 words/min), high pitch, excessive self-correction
- **Video Metrics**: Fidgeting, nail-biting, touching face frequently
- **Performance Metrics**: Over-checking answers, excessive hesitation before submitting
- **Physiological**: If available, elevated heart rate patterns in voice analysis
- **Algorithm**: `anxiety_score = speech_speed_excess + fidget_frequency + over_checking + self_correction_rate`

## **Fatigue States - Metrics**

**20. Mental Fatigue Skill**
- **Speech Metrics**: Slower speech rate declining over time, increased pauses
- **Video Metrics**: Eye rubbing, decreased facial animation, micro-sleeps
- **Performance Metrics**: Accuracy declining with session time, longer response times
- **Session Context**: Performance correlation with session duration (>45 min)
- **Algorithm**: `mental_fatigue = performance_decline_over_time + speech_slowdown + eye_rubbing + session_length_factor`

**21. Physical Tiredness Skill**
- **Video Metrics**: Yawning, eye rubbing, slumped posture, head drooping
- **Speech Metrics**: Quieter voice, less animated speech
- **Performance Metrics**: Overall slower responses, not necessarily less accurate
- **Algorithm**: `physical_fatigue = yawn_detection + posture_decline + voice_energy_drop + response_slowdown`

## **Implementation Architecture**

**Real-time Processing Pipeline:**
1. **Speech Analysis**: Continuous NLP processing for sentiment, pace, hesitation markers
2. **Computer Vision**: Real-time facial expression, gesture, and posture analysis
3. **Performance Tracking**: Question response analysis with rolling averages
4. **Historical Context**: Vector DB queries for similar past emotional states
5. **Composite Scoring**: Weighted combination of all metrics with confidence intervals

**Threshold Examples:**
- High Engagement: Combined score >0.7
- Mild Confusion: Hesitation markers >3 per minute + response time >2x baseline
- Frustration: Vocal stress >0.6 + facial tension detected + accuracy drop >20%

**Note**: Each metric would be normalized to 0-1 scale and combined with weighted algorithms specific to each emotional state.

