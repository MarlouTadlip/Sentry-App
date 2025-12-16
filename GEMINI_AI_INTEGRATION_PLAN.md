# Gemini AI Integration Plan for Sentry Crash Detection

## Overview

This document outlines the comprehensive plan for integrating Google Gemini AI API into the Sentry crash detection system. The integration will enhance crash detection accuracy, reduce false positives, and provide intelligent pattern analysis of sensor data.

---

## 🚀 Current Implementation (Do Now)

### 1. Integrate Gemini AI to Server

#### 1.1 Core Configuration Setup

**Location**: `backend/sentry/core/`

**A. Gemini Service in Core App**
- Create `core/ai/gemini_service.py` - Main Gemini AI service class
- Handle API initialization, configuration, and core AI interactions
- Provide reusable methods for all Gemini AI operations

**B. Configuration in Settings**
Add to `sentry/settings/config.py`:
```python
gemini_api_key: str | None = Field(
    default=None,
    description="Google Gemini API key for crash detection AI",
)
gemini_model: str = Field(
    default="gemini-pro",
    description="Gemini model to use",
)
gemini_max_tokens: int = Field(
    default=2048,
    description="Maximum tokens for Gemini responses",
)
gemini_analysis_lookback_seconds: int = Field(
    default=30,
    description="Default lookback period for real-time analysis (seconds)",
)
gemini_temperature: float = Field(
    default=0.2,
    description="Temperature for AI responses (lower = more deterministic)",
)
```

**C. Dependencies**
```bash
pip install google-generativeai>=0.3.0
```

#### 1.2 Gemini Service Implementation

**File**: `core/ai/gemini_service.py`

**Key Methods**:
```python
class GeminiService:
    def __init__(self):
        # Initialize Gemini client with API key from settings
        
    def analyze_crash_data(
        self,
        sensor_data: List[Dict],
        current_reading: Dict,
        context_seconds: int = 30
    ) -> Dict:
        """Analyze sensor data for crash detection.
        
        Returns:
            {
                "is_crash": bool,
                "confidence": float (0.0-1.0),
                "severity": "low" | "medium" | "high",
                "crash_type": str,
                "reasoning": str,
                "key_indicators": List[str],
                "false_positive_risk": float
            }
        """
        
    def format_sensor_data_for_ai(
        self,
        sensor_data: List[Dict],
        include_metrics: bool = True
    ) -> str:
        """Format sensor data into readable text for AI analysis."""
        
    def create_crash_analysis_prompt(
        self,
        formatted_data: str,
        current_reading: Dict
    ) -> str:
        """Create optimized prompt for crash detection analysis."""
```

### 2. Create Controllers and Routes for AI

#### 2.1 Device Controllers (AI-Focused)

**Location**: `backend/sentry/device/controllers/`

**A. Crash Analysis Controller**
**File**: `device/controllers/crash_analysis_controller.py`

**Key Functions**:
```python
def analyze_realtime_crash(
    request: HttpRequest,
    data: RealtimeAnalysisRequest
) -> CrashAnalysisResponse:
    """Analyze current sensor data with recent context for crash detection.
    
    - Retrieves recent sensor data (last 30 seconds by default)
    - Formats data for Gemini AI
    - Calls Gemini service for analysis
    - Returns crash detection results
    
    Query Optimization:
    - Use indexed fields (device_id, timestamp) for filtering
    - Use only() to fetch only necessary sensor data fields
    - Limit queryset size with appropriate time range
    """
    
def analyze_historical_crash(
    request: HttpRequest,
    data: HistoricalAnalysisRequest
) -> HistoricalAnalysisResponse:
    """Analyze historical sensor data within time range.
    
    - Retrieves sensor data for specified time range
    - Applies smart sampling if needed
    - Analyzes patterns and events
    - Returns comprehensive analysis
    
    Query Optimization:
    - Use select_related('device') if device relationship exists
    - Use iterator() for large time ranges to process in chunks
    - Apply database-level filtering before fetching data
    - Use only() to limit fields fetched from database
    """
    
def analyze_crash_patterns(
    request: HttpRequest,
    data: PatternAnalysisRequest
) -> PatternAnalysisResponse:
    """Analyze patterns in sensor data over time.
    
    - Identifies riding patterns
    - Detects anomalies
    - Provides AI-generated insights
    
    Query Optimization:
    - Use database aggregations (annotate/aggregate) instead of Python calculations
    - Prefetch related CrashEvent objects if needed
    - Use select_related() for any ForeignKey relationships
    - Apply smart sampling at database level when possible
    """
```

**Query Optimization Requirements**:
- All data retrieval must use optimized queries (see CrashEvent Model section for best practices)
- No N+1 queries when fetching sensor data or crash events
- Use database indexes effectively (device_id, timestamp fields)
- Limit queryset size and use pagination for large datasets

**B. Update Device Controller**
**File**: `device/controllers/device_controller.py`

**Enhancements**:
- Integrate AI analysis when receiving device data
- Optionally trigger real-time crash analysis on high-impact readings
- Store AI analysis results with sensor data

#### 2.2 Device Routes

**Location**: `backend/sentry/device/router/`

**A. Crash Analysis Router**
**File**: `device/router/crash_analysis_router.py`

**Endpoints**:
```python
# Real-time crash analysis
POST /api/v1/device/analyze/realtime
Body: {
    "device_id": "string",  # Optional, can infer from auth
    "lookback_seconds": 30,  # Optional, default 30
    "include_current": true  # Optional, default true
}
Response: CrashAnalysisResponse

# Historical crash analysis
POST /api/v1/device/analyze/historical
Body: {
    "device_id": "string",
    "start_time": "ISO 8601 timestamp",
    "end_time": "ISO 8601 timestamp",
    "resolution": "full" | "normal" | "low"  # Optional
}
Response: HistoricalAnalysisResponse

# Pattern analysis
POST /api/v1/device/analyze/patterns
Body: {
    "device_id": "string",
    "start_time": "ISO 8601 timestamp",
    "end_time": "ISO 8601 timestamp"
}
Response: PatternAnalysisResponse
```

**B. Update Device Router**
**File**: `device/router/device_router.py`

- Include crash analysis router
- Add optional AI analysis to data receiving endpoint

#### 2.3 Schemas

**Location**: `backend/sentry/device/schemas/`

**A. Crash Analysis Schemas**
**File**: `device/schemas/crash_analysis_schema.py`

```python
class RealtimeAnalysisRequest(Schema):
    device_id: str | None = None
    lookback_seconds: int = 30
    include_current: bool = True

class HistoricalAnalysisRequest(Schema):
    device_id: str
    start_time: datetime
    end_time: datetime
    resolution: str = "normal"  # full, normal, low

class PatternAnalysisRequest(Schema):
    device_id: str
    start_time: datetime
    end_time: datetime

class CrashAnalysisResponse(Schema):
    is_crash: bool
    confidence: float
    severity: str  # low, medium, high
    crash_type: str
    reasoning: str
    key_indicators: List[str]
    false_positive_risk: float
    timestamp: datetime
    analysis_metadata: Dict | None = None

class HistoricalAnalysisResponse(Schema):
    events_detected: List[CrashAnalysisResponse]
    summary: Dict
    time_range: Dict

class PatternAnalysisResponse(Schema):
    patterns: List[Dict]
    insights: List[str]
    risk_assessment: Dict | None = None
```

### 3. Crash Detection Enhancement Methods

#### 3.1 Real-Time Crash Detection

**Purpose**: Analyze incoming sensor data in real-time to detect crashes with high accuracy and low latency.

**Implementation Approach**:

**A. Multi-Factor Detection System**
- Combine acceleration patterns, tilt detection, and motion sequences
- Use Gemini AI to analyze context and reduce false positives
- Provide confidence scores and severity assessment

**B. Detection Triggers**
- **Primary Trigger**: Sudden acceleration spike (>8g threshold)
- **Secondary Trigger**: Abnormal tilt (>90°)
- **Tertiary Trigger**: Pattern anomalies (suspicious sequences)

**C. AI Analysis Input**
```
For each incoming sensor reading:
1. Current reading: {ax, ay, az, roll, pitch, tilt_detected, timestamp}
2. Recent context: Last 10-30 seconds of sensor data (10-60 readings)
3. Calculated metrics:
   - Total G-force: sqrt(ax² + ay² + az²)
   - Acceleration magnitude changes
   - Motion patterns (acceleration vectors)
   - Tilt rate of change
```

**D. Gemini AI Prompt Structure**
```
You are an expert crash detection system for motorcycle/vehicle helmets.

Analyze the following sensor data sequence and determine if a crash occurred:

[Time-series sensor data with timestamps]
- Recent readings (last 30 seconds)
- Current reading (marked)
- Calculated metrics (G-forces, patterns)

Analysis Criteria:
1. Impact Detection: Look for sudden deceleration patterns (rapid negative acceleration spikes >8g)
2. Crash Signatures: Identify impact signatures (sharp spikes in acceleration)
3. Motion Continuity: Check if motion patterns indicate a crash vs. normal activity
4. False Positive Reduction: Distinguish crashes from:
   - Helmet drops
   - Intentional movements (taking off/putting on)
   - Normal riding activities
   - Vibration/noise

Respond with JSON:
{
  "is_crash": boolean,
  "confidence": float (0.0-1.0),
  "severity": "low" | "medium" | "high",
  "crash_type": "head-on" | "side-impact" | "rear-end" | "fall" | "rollover" | "unknown",
  "timestamp": ISO 8601 timestamp,
  "reasoning": "explanation",
  "key_indicators": ["list", "of", "indicators"],
  "false_positive_risk": float (0.0-1.0)
}
```

#### 3.2 Data Formatting Utilities

**Purpose**: Format sensor data for optimal Gemini AI consumption.

**Implementation**:

**A. Time Range Query Interface**
```python
def get_sensor_data_range(
    device_id: str,
    start_time: datetime,
    end_time: datetime,
    max_readings: int = 1000
) -> List[SensorData]
```

**B. Data Formatting for Gemini**
- Convert time-series data to structured format
- Include timestamps, sensor values, and calculated metrics
- Format as readable text for AI consumption

**C. Sample Data Format**
```
Sensor Data Analysis Request
Device ID: ESP32_001
Time Range: 2024-01-15T14:30:00Z to 2024-01-15T14:35:00Z
Total Readings: 300 (5 minutes @ 1 reading/second)

Time Series Data:
--------------------------------------------------
T-300s (14:30:00): ax=0.12, ay=0.05, az=0.98, roll=2.3°, pitch=1.1°, tilt=false, g_force=0.99
T-299s (14:30:01): ax=0.15, ay=0.08, az=0.97, roll=2.5°, pitch=1.2°, tilt=false, g_force=0.98
...
T-5s (14:34:55): ax=0.18, ay=0.06, az=0.96, roll=2.7°, pitch=1.3°, tilt=false, g_force=0.97
T-4s (14:34:56): ax=-2.5, ay=1.2, az=8.3, roll=5.1°, pitch=12.3°, tilt=false, g_force=8.9  [BRAKING]
T-3s (14:34:57): ax=-15.2, ay=3.5, az=18.7, roll=45.2°, pitch=78.5°, tilt=true, g_force=24.3  [IMPACT]
T-2s (14:34:58): ax=-2.1, ay=8.5, az=5.2, roll=92.3°, pitch=105.7°, tilt=true, g_force=10.2  [POST-IMPACT]
T-1s (14:34:59): ax=0.3, ay=0.5, az=0.4, roll=95.1°, pitch=108.2°, tilt=true, g_force=0.7  [STATIONARY]
T-0s (14:35:00): ax=0.1, ay=0.2, az=0.3, roll=96.2°, pitch=109.5°, tilt=true, g_force=0.37  [CURRENT]

Calculated Metrics:
- Max G-force in range: 24.3g (at T-3s)
- G-force spike detected: Yes (T-3s)
- Tilt occurred: Yes (starting at T-3s)
- Duration of impact: ~2 seconds
- Motion pattern: Sudden deceleration → Impact → Stationary
```

#### 3.3 Smart Data Sampling

**Purpose**: Optimize data sent to Gemini by intelligently sampling or summarizing large time ranges.

**Strategies**:

**A. Adaptive Sampling**
- Use full resolution for recent data (last 30 seconds)
- Use statistical summaries for older data (max, min, avg, std dev per 10-second window)
- Focus on anomalous regions with full detail

**B. Event-Based Segmentation**
- Identify significant events (spikes, tilts, anomalies)
- Include full detail around events (±5 seconds)
- Summarize normal periods

**C. Token Optimization**
- Gemini has token limits (~32k tokens)
- Estimate token usage before sending
- Automatically reduce resolution if needed

### 4. File Structure

```
backend/sentry/
├── core/
│   └── ai/
│       ├── __init__.py
│       └── gemini_service.py (new) - Main Gemini AI service
│
└── device/
    ├── models/
    │   └── sensor_data.py (existing)
    ├── services/
    │   ├── __init__.py
    │   └── crash_detector.py (new) - Crash detection logic using Gemini
    ├── controllers/
    │   ├── device_controller.py (update) - Add optional AI analysis
    │   └── crash_analysis_controller.py (new) - AI analysis endpoints
    ├── schemas/
    │   ├── device_schema.py (update)
    │   └── crash_analysis_schema.py (new)
    └── router/
        ├── device_router.py (update) - Include crash analysis routes
        └── crash_analysis_router.py (new) - AI analysis routes
```

---

## 📋 TO DO Next (Near-Term Features)

### 1. Crash Event Model and Storage

#### Purpose
Store detected crash events with AI analysis results for historical tracking and alerts.

#### Implementation

**A. CrashEvent Model**
```python
class CrashEvent(models.Model):
    device_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    crash_timestamp = models.DateTimeField()  # Actual crash time from sensor data
    
    # AI Analysis Results
    is_confirmed_crash = models.BooleanField()
    confidence_score = models.FloatField()
    severity = models.CharField(max_length=20)  # low, medium, high
    crash_type = models.CharField(max_length=50)  # head-on, side-impact, etc.
    ai_reasoning = models.TextField()
    key_indicators = models.JSONField(default=list)
    false_positive_risk = models.FloatField()
    
    # Sensor Data Snapshot
    max_g_force = models.FloatField()
    impact_acceleration = models.JSONField()  # {ax, ay, az} at impact
    final_tilt = models.JSONField()  # {roll, pitch}
    
    # User Feedback
    user_confirmed = models.BooleanField(null=True)  # User verification
    false_positive = models.BooleanField(null=True)  # User marked as false positive
    
    # Alert Status
    alert_sent = models.BooleanField(default=False)
    alert_recipients = models.JSONField(default=list)
    
    class Meta:
        ordering = ['-crash_timestamp']
        indexes = [
            models.Index(fields=['device_id', '-crash_timestamp']),
            models.Index(fields=['user', '-crash_timestamp']),
        ]
```

**B. Query Optimization Requirements**

**Critical**: All controllers using CrashEvent must be query-optimized with no N+1 queries and no unnecessary queries.

**Best Practices**:

1. **Use `select_related()` for ForeignKey relationships**
   ```python
   # ✅ Good: Single query
   crash_events = CrashEvent.objects.select_related('user').filter(device_id=device_id)
   
   # ❌ Bad: N+1 queries
   crash_events = CrashEvent.objects.filter(device_id=device_id)
   for event in crash_events:
       user = event.user  # Additional query per event
   ```

2. **Use `prefetch_related()` for reverse ForeignKey or ManyToMany relationships**
   ```python
   # If CrashEvent has reverse relationships, use prefetch_related
   events = CrashEvent.objects.select_related('user').prefetch_related('related_objects')
   ```

3. **Use `only()` or `defer()` to fetch only needed fields**
   ```python
   # Only fetch necessary fields
   events = CrashEvent.objects.select_related('user').only(
       'id', 'crash_timestamp', 'severity', 'confidence_score', 'user__email'
   )
   ```

4. **Use `annotate()` for aggregations instead of Python-level calculations**
   ```python
   from django.db.models import Count, Avg, Max
   
   # ✅ Good: Database-level aggregation
   stats = CrashEvent.objects.filter(device_id=device_id).aggregate(
       total_crashes=Count('id'),
       avg_confidence=Avg('confidence_score'),
       max_g_force=Max('max_g_force')
   )
   
   # ❌ Bad: Python-level calculation (fetches all records)
   events = CrashEvent.objects.filter(device_id=device_id)
   total = len(events)  # Fetches all records unnecessarily
   ```

5. **Use `exists()` instead of `count()` when checking existence**
   ```python
   # ✅ Good: Stops at first match
   has_crashes = CrashEvent.objects.filter(device_id=device_id).exists()
   
   # ❌ Bad: Counts all matching records
   has_crashes = CrashEvent.objects.filter(device_id=device_id).count() > 0
   ```

6. **Use `iterator()` for large querysets to avoid loading all into memory**
   ```python
   # For large result sets, use iterator to process in chunks
   for event in CrashEvent.objects.select_related('user').iterator(chunk_size=1000):
       process_event(event)
   ```

7. **Use database indexes effectively**
   - Ensure queries use indexed fields (device_id, user, crash_timestamp)
   - Use `filter()` on indexed fields before other operations

8. **Avoid unnecessary queries in loops**
   ```python
   # ✅ Good: Prefetch all related data
   events = CrashEvent.objects.select_related('user').filter(device_id=device_id)
   for event in events:
       # No additional queries needed
       process_event(event, event.user)
   
   # ❌ Bad: Query inside loop
   events = CrashEvent.objects.filter(device_id=device_id)
   for event in events:
       user = User.objects.get(id=event.user_id)  # N+1 query!
       process_event(event, user)
   ```

**Controller Implementation Checklist**:
- [ ] All ForeignKey relationships use `select_related()`
- [ ] All reverse relationships use `prefetch_related()` if needed
- [ ] Only necessary fields are fetched using `only()` or `defer()`
- [ ] Aggregations use `annotate()` or `aggregate()` instead of Python calculations
- [ ] Existence checks use `exists()` instead of `count() > 0`
- [ ] No queries inside loops
- [ ] Large querysets use `iterator()` when appropriate
- [ ] Queries are tested with Django Debug Toolbar or `connection.queries` to verify optimization

### 2. Basic Alert System

#### Purpose
Send alerts to emergency contacts when crashes are detected.

#### Implementation

**A. Alert Triggering**
- Trigger on high-confidence crashes (confidence > 0.7)
- Send Email notifications (using existing Brevo integration)
- Include crash severity and AI reasoning
- Basic alert message template

**B. Alert Escalation**
- Immediate alert for high-severity crashes
- Delayed alert for medium-severity (wait for user response)
- Log-only for low-severity/low-confidence

**C. Alert Message Template**
```
🚨 CRASH DETECTED - Sentry Device

Device: [Device ID]
Time: [Timestamp]
Severity: [High/Medium/Low]
Confidence: [85%]

AI Analysis: [Brief reasoning]
Crash Type: [Head-on collision]

If you receive this and are okay, please dismiss the alert.
```

### 3. User Feedback Loop

#### Purpose
Allow users to confirm or deny crash detections to improve AI accuracy.

#### Implementation

**A. Feedback Endpoint**
```
POST /api/v1/device/events/{event_id}/feedback
Body: {
  "is_crash": bool,  # User confirmation
  "false_positive": bool,  # If false positive
  "comments": "string"  # Optional user comments
}
```

**B. Feedback Learning**
- Store user feedback with crash events
- Track false positive rate
- Adjust confidence thresholds based on feedback

### 4. Batch Analysis for Historical Data

#### Purpose
Analyze historical sensor data to identify patterns, validate past events, and improve detection accuracy.

#### Implementation Approach

**A. Scheduled Batch Jobs**
- Run periodic analysis on recent data (last hour, last 24 hours)
- Identify missed detections or false positives
- Generate insights and patterns

**B. Manual Analysis Endpoint**
- Allow users/admins to request analysis of specific time ranges
- Useful for reviewing incidents and improving system accuracy

---

## 🔮 Future Enhancements (Long-Term/Advanced Features)

### 1. Analytics and Insights Dashboard

#### Purpose
Provide users with insights about their riding patterns and crash risks.

#### Implementation

**A. Riding Statistics**
- Total ride time
- Average speed (if GPS available)
- Crash events count
- False positive rate
- Risk score based on patterns

**B. AI-Generated Insights**
- Weekly/monthly summaries
- Pattern identification (e.g., "You tend to brake hard on Tuesdays")
- Safety recommendations
- Risk assessment trends

**C. Endpoints**
```
GET /api/v1/device/analytics/summary
GET /api/v1/device/analytics/patterns
GET /api/v1/device/analytics/risks
```

### 2. Crash Event Visualization

#### Purpose
Visualize sensor data and crash events for better understanding.

#### Implementation

**A. Event Timeline View**
- Time-series chart of acceleration data
- Mark crash events
- Show G-force spikes
- Show tilt changes

**B. Crash Replay**
- Animate sensor data leading up to crash
- Show acceleration vectors
- Visualize impact pattern

### 3. Multi-Device Support

#### Purpose
Support multiple devices per user and aggregate analysis.

#### Implementation

**A. Device Management**
- Register multiple devices per user
- Device naming and organization
- Active/inactive device status

**B. Aggregated Analysis**
- Analyze patterns across all user devices
- Compare crash patterns between devices
- Fleet-level insights for organizations

### 4. Emergency Services Integration

#### Purpose
Automatically notify emergency services for high-severity crashes.

#### Implementation

**A. Emergency API Integration**
- Integrate with emergency services APIs (if available)
- Send crash location and severity
- Include device owner information

**B. Auto-Dial Emergency**
- For very high-severity crashes, auto-dial emergency services
- Play pre-recorded message with location
- Requires user consent and setup

### 5. Data Privacy and Compliance

#### Purpose
Ensure sensor data and crash events are handled with proper privacy.

#### Implementation

**A. Data Retention Policies**
- Configurable retention periods
- Automatic deletion of old data
- User data export capability

**B. GDPR Compliance**
- User data deletion requests
- Data anonymization options
- Consent management

**C. Encryption**
- Encrypt sensitive sensor data at rest
- Encrypt data in transit
- Secure API key storage

### 6. Advanced AI Features
- Fine-tuned models for specific crash types
- Multi-modal analysis (combine with audio/video if available)
- Predictive crash risk assessment
- Personalized detection based on user patterns

### 7. Integration Possibilities
- GPS data integration for location-based analysis
- Weather data integration for context
- Traffic data integration
- Health monitoring integration

### 8. Machine Learning Pipeline
- Train custom models using collected data
- Continuous learning from user feedback
- A/B testing of different detection strategies
- Model versioning and rollback

---

## 5. Technical Requirements

### 5.1 Dependencies
```
google-generativeai>=0.3.0
```

### 5.2 Configuration
Add to `sentry/settings/config.py`:
```python
gemini_api_key: str | None = Field(
    default=None,
    description="Google Gemini API key for crash detection AI",
)
gemini_model: str = Field(
    default="gemini-pro",
    description="Gemini model to use",
)
gemini_max_tokens: int = Field(
    default=2048,
    description="Maximum tokens for Gemini responses",
)
gemini_analysis_lookback_seconds: int = Field(
    default=30,
    description="Default lookback period for real-time analysis (seconds)",
)
```

### 5.3 File Structure

**Note**: This structure reflects the current implementation focus. See section "4. File Structure" in "Current Implementation" for the complete structure.

---

## 6. Performance Considerations

### 6.1 Response Time
- Real-time analysis: Target <2 seconds
- Historical analysis: Target <10 seconds for 1 hour of data
- Use async processing for non-critical analyses

### 6.2 API Rate Limits
- Gemini API has rate limits (check current limits)
- Implement request queuing and rate limiting
- Cache analysis results when appropriate
- Use batch processing for historical analysis

### 6.3 Cost Optimization
- Only analyze when triggers are detected (acceleration spikes, tilts)
- Use lower-resolution analysis for routine checks
- Cache and reuse analysis for similar patterns
- Implement cost monitoring and alerts

### 6.4 Data Storage
- Store crash events, not all sensor data long-term
- Archive old sensor data
- Use database indexes for fast queries
- Consider time-series database for sensor data if volume is high

---

## 7. Testing Strategy

### 7.1 Unit Tests
- Test Gemini service with mock responses
- Test data formatting utilities
- Test crash detection logic

### 7.2 Integration Tests
- Test full analysis pipeline
- Test time-range data retrieval
- Test alert triggering

### 7.3 Test Data
- Create test datasets with known crash patterns
- Create test datasets with false positives
- Validate AI accuracy on test data

### 7.4 Performance Tests
- Load testing for API endpoints
- Response time benchmarks
- Concurrent request handling

---

## 8. Monitoring and Logging

### 8.1 Metrics to Track
- AI analysis response times
- Crash detection accuracy (true positives, false positives)
- API usage and costs
- Alert delivery success rate
- User feedback statistics

### 8.2 Logging
- Log all AI analysis requests and responses
- Log crash detections with full context
- Log errors and failures
- Log cost-related events

### 8.3 Alerts
- Alert on high false positive rate
- Alert on API failures
- Alert on unusual cost spikes
- Alert on system performance degradation

---

## 10. Success Metrics

### 10.1 Detection Accuracy
- True positive rate > 95%
- False positive rate < 5%
- Average detection latency < 2 seconds

### 10.2 User Experience
- User satisfaction score
- Alert relevance score
- Feature adoption rate

### 10.3 System Performance
- API response time < 2 seconds (p95)
- System uptime > 99.9%
- Cost per analysis < $0.01

---

## Conclusion

This integration plan provides a comprehensive roadmap for adding Gemini AI to the Sentry crash detection system. The plan is organized into three main sections:

1. **Current Implementation**: Core AI integration, controllers, routes, and crash detection methods (do now)
2. **TO DO Next**: Crash event model, basic alerts, user feedback, and batch analysis (near-term)
3. **Future Enhancements**: Advanced features like analytics, visualization, multi-device support, emergency services, and machine learning (long-term)

The phased approach allows for incremental implementation while maintaining system stability. The focus on accuracy, performance, and user experience ensures the AI integration will significantly enhance the crash detection capabilities.

**Immediate Next Steps:**
1. Obtain Gemini API key (student program recommended for free unlimited access)
2. Install `google-generativeai` package
3. Create Gemini service in `core/ai/gemini_service.py`
4. Create crash analysis controllers and routes in `device/` app
5. Implement real-time crash detection analysis
6. Test with sample sensor data

