"""Gemini AI service for crash analysis."""

import json
import logging
from typing import Any

try:
    import google.genai as genai
except ImportError:
    genai = None  # type: ignore

from sentry.settings.config import settings as app_settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini AI."""

    def __init__(self) -> None:
        """Initialize Gemini service."""
        self.client = None
        self.model_name = app_settings.gemini_model

        if genai is None:
            logger.warning("google-genai package not installed")
            return

        if not app_settings.gemini_api_key:
            logger.warning("Gemini API key not configured")
            return

        # Initialize client with API key
        try:
            self.client = genai.Client(api_key=app_settings.gemini_api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None

    def format_sensor_data_for_ai(
        self,
        sensor_data: list[dict[str, Any]],
        current_reading: dict[str, Any],
        include_metrics: bool = True,
    ) -> str:
        """Format sensor data for AI analysis.

        Args:
            sensor_data: List of sensor readings from database
            current_reading: Current sensor reading that triggered alert
            include_metrics: Whether to include calculated metrics

        Returns:
            Formatted string for AI prompt
        """
        lines = ["=== SENSOR DATA CONTEXT ==="]

        # Add recent sensor data
        if sensor_data:
            lines.append(f"\nRecent sensor readings ({len(sensor_data)} readings):")
            for reading in sensor_data[-10:]:  # Last 10 readings
                lines.append(
                    f"  - Time: {reading.get('timestamp', 'N/A')}, "
                    f"Accel: ({reading.get('ax', 0):.2f}, {reading.get('ay', 0):.2f}, {reading.get('az', 0):.2f}), "
                    f"Tilt: roll={reading.get('roll', 0):.1f}°, pitch={reading.get('pitch', 0):.1f}°"
                )

        # Add current reading (the one that triggered alert)
        lines.append("\n=== CURRENT READING (ALERT TRIGGER) ===")
        lines.append(
            f"Acceleration: ({current_reading.get('ax', 0):.2f}, "
            f"{current_reading.get('ay', 0):.2f}, {current_reading.get('az', 0):.2f})"
        )
        lines.append(
            f"Tilt: roll={current_reading.get('roll', 0):.1f}°, pitch={current_reading.get('pitch', 0):.1f}°"
        )
        lines.append(f"Tilt detected: {current_reading.get('tilt_detected', False)}")

        if include_metrics:
            # Calculate G-force for current reading
            ax = current_reading.get("ax", 0)
            ay = current_reading.get("ay", 0)
            az = current_reading.get("az", 0)
            g_force = (ax**2 + ay**2 + az**2) ** 0.5 / 9.81
            lines.append(f"Calculated G-force: {g_force:.2f}g")

        return "\n".join(lines)

    def analyze_crash_data(
        self,
        sensor_data: list[dict[str, Any]],
        current_reading: dict[str, Any],
        context_seconds: int = 30,
    ) -> dict[str, Any]:
        """Analyze crash data using Gemini AI.

        Args:
            sensor_data: List of sensor readings from database
            current_reading: Current sensor reading that triggered alert
            context_seconds: Number of seconds of context to analyze

        Returns:
            Dictionary containing AI analysis results:
            {
                'is_crash': bool,
                'confidence': float (0-1),
                'severity': 'low'|'medium'|'high',
                'crash_type': str,
                'reasoning': str,
                'key_indicators': list[str],
                'false_positive_risk': float (0-1)
            }
        """
        if not app_settings.gemini_api_key:
            logger.error("Gemini API key not configured")
            return self._default_response()

        try:
            # Format sensor data
            formatted_data = self.format_sensor_data_for_ai(
                sensor_data=sensor_data,
                current_reading=current_reading,
                include_metrics=True,
            )

            # Create prompt
            prompt = f"""You are analyzing sensor data from a motorcycle helmet crash detection system. 
A threshold alert was triggered (G-force or tilt exceeded limits).

{formatted_data}

Analyze this data and determine if this represents an actual crash event or a false positive (e.g., sudden braking, helmet removal, normal riding).

Respond with a JSON object containing:
{{
    "is_crash": boolean,
    "confidence": float (0.0 to 1.0),
    "severity": "low" | "medium" | "high",
    "crash_type": string (e.g., "frontal_impact", "side_impact", "fall", "false_positive"),
    "reasoning": string (brief explanation),
    "key_indicators": array of strings (e.g., ["high_g_force", "sudden_tilt", "sustained_acceleration"]),
    "false_positive_risk": float (0.0 to 1.0)
}}

Important considerations:
- High G-force alone might be sudden braking (false positive)
- Sustained tilt might indicate actual crash or helmet removal
- Look at the pattern over time, not just the current reading
- Consider motorcycle riding context (acceleration, braking, cornering)

Respond with ONLY the JSON object, no additional text."""

            # Call Gemini API
            if self.client is None:
                logger.error("Gemini client not initialized")
                return self._default_response()

            # Log comprehensive AI analysis request
            logger.info(
                f"🤖 Calling Gemini AI for crash analysis | model={self.model_name} | "
                f"sensor_data_points={len(sensor_data)} | context_seconds={context_seconds} | "
                f"current_reading: ax={current_reading.get('ax', 0):.2f}, "
                f"ay={current_reading.get('ay', 0):.2f}, az={current_reading.get('az', 0):.2f} | "
                f"roll={current_reading.get('roll', 0):.1f}°, pitch={current_reading.get('pitch', 0):.1f}° | "
                f"tilt_detected={current_reading.get('tilt_detected', False)} | prompt_length={len(prompt)}"
            )

            # Generate content using the new API
            # Note: The exact API structure for google.genai may vary
            # Please refer to the official documentation: https://github.com/google-gemini/generative-ai-python
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )

            # Parse response - access text from the response object
            # The exact structure may vary between API versions, so we handle multiple formats
            response_text = ""
            if hasattr(response, 'text'):
                response_text = response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                # Handle candidate-based response structure
                if hasattr(response.candidates[0], 'content'):
                    if hasattr(response.candidates[0].content, 'parts'):
                        response_text = response.candidates[0].content.parts[0].text.strip()
                    elif hasattr(response.candidates[0].content, 'text'):
                        response_text = response.candidates[0].content.text.strip()
            elif hasattr(response, 'content'):
                # Handle direct content attribute
                if hasattr(response.content, 'text'):
                    response_text = response.content.text.strip()
                elif hasattr(response.content, 'parts'):
                    response_text = response.content.parts[0].text.strip()
            
            if not response_text:
                # Fallback: try to extract text from response string representation
                logger.warning("Could not extract text from response, using string representation")
                response_text = str(response).strip()

            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            # Parse JSON
            result = json.loads(response_text)

            # Validate and sanitize response
            ai_result = {
                "is_crash": bool(result.get("is_crash", False)),
                "confidence": float(result.get("confidence", 0.5)),
                "severity": result.get("severity", "low"),
                "crash_type": str(result.get("crash_type", "unknown")),
                "reasoning": str(result.get("reasoning", "Analysis completed")),
                "key_indicators": result.get("key_indicators", []),
                "false_positive_risk": float(result.get("false_positive_risk", 0.5)),
            }

            # Log comprehensive AI analysis result
            logger.info(
                f"✅ Gemini AI analysis complete | model={self.model_name} | "
                f"is_crash={ai_result['is_crash']} | confidence={ai_result['confidence']:.2f} | "
                f"severity={ai_result['severity']} | crash_type={ai_result['crash_type']} | "
                f"false_positive_risk={ai_result['false_positive_risk']:.2f} | "
                f"key_indicators={len(ai_result['key_indicators'])} | "
                f"reasoning_length={len(ai_result['reasoning'])} | "
                f"reasoning={ai_result['reasoning'][:150]}..."
            )

            return ai_result

        except json.JSONDecodeError as e:
            logger.error(
                f"❌ Failed to parse Gemini response as JSON | model={self.model_name} | "
                f"error={str(e)} | response_text_length={len(response_text)} | "
                f"response_preview={response_text[:200]}..."
            )
            return self._default_response()
        except Exception as e:
            logger.error(
                f"❌ Error calling Gemini API | model={self.model_name} | "
                f"error={str(e)} | error_type={type(e).__name__}",
                exc_info=True,
            )
            return self._default_response()

    def _default_response(self) -> dict[str, Any]:
        """Return default response when AI fails.

        Returns:
            Default response dictionary
        """
        return {
            "is_crash": False,
            "confidence": 0.5,
            "severity": "low",
            "crash_type": "unknown",
            "reasoning": "AI analysis unavailable - defaulting to false positive",
            "key_indicators": [],
            "false_positive_risk": 0.8,
        }

