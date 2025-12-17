export const Colors = {
  // Primary Green Colors (Main Theme)
  green: {
    50: "#eff6ff", // Very light green background, page backgrounds
    100: "#dbeafe", // Light green background, card backgrounds, hover states
    200: "#bfdbfe", // Card borders, dividers
    300: "#93c5fd", // Button borders, hover borders
    400: "#2563eb", // Header gradient start
    500: "#1e40af", // Primary brand color, icons, active navigation, badges, buttons
    600: "#1e3a8a", // Button hover states, emphasized text, active riding badge
    700: "#172554", // Dark green text in light backgrounds
    800: "#0f172a", // Darker text in green info cards
  },

  // Emerald Colors (Secondary Accent)
  emerald: {
    200: "#bae6fd", // Map background gradient
    500: "#0284c7", // Header gradient end
  },

  // Semantic color mappings for easy reference
  primary: "#1e40af", // green-500
  primaryHover: "#1e3a8a", // green-600
  background: "#eff6ff", // green-50
  cardBackground: "#dbeafe", // green-100
  border: "#bfdbfe", // green-200
  borderHover: "#93c5fd", // green-300

  gray: { 100: "#6b7280", 200: "#4b5563" },
  red: "#dc2626",
} as const;

// Dark theme colors
export const DarkColors = {
  // Primary Green Colors (Main Theme) - adjusted for dark mode
  green: {
    50: "#070b14", // Very dark green background, page backgrounds
    100: "#0b1220", // Dark green background, card backgrounds
    200: "#162645", // Card borders, dividers
    300: "#1e3a8a", // Button borders, hover borders
    400: "#1d4ed8", // Header gradient start
    500: "#3b82f6", // Primary brand color, icons, active navigation, badges, buttons
    600: "#60a5fa", // Button hover states, emphasized text
    700: "#bfdbfe", // Light green text in dark backgrounds
    800: "#dbeafe", // Lighter text in green info cards
  },

  // Emerald Colors (Secondary Accent)
  emerald: {
    200: "#082f49", // Dark map background gradient
    500: "#0284c7", // Header gradient end
  },

  // Semantic color mappings for dark theme
  primary: "#3b82f6", // green-400 (lighter for dark mode)
  primaryHover: "#60a5fa", // green-300
  background: "#070b14", // green-50 (dark)
  cardBackground: "#0b1220", // green-100 (dark)
  border: "#162645", // green-200 (dark)
  borderHover: "#1e3a8a", // green-300 (dark)

  gray: { 100: "#9ca3af", 200: "#d1d5db" }, // Lighter grays for dark mode
  red: "#ef4444", // Brighter red for dark mode
} as const;

export type ColorKey = keyof typeof Colors;
