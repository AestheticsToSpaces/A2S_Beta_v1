// Note: This service previously relied on backend API endpoints
// With Supabase-only architecture, these features need to be reimplemented
// Options: Supabase Edge Functions, or direct Gemini API calls from frontend

const NO_KEY_MESSAGE = "AI features require backend implementation. Coming soon!";

class GeminiService {

    isAvailable() {
        // AI Consultant features are temporarily unavailable in Supabase-only mode
        return false;
    }

    async getDesignAdvice(userQuery, context) {
        // Mock response for now
        return "I've analyzed your space. To maximize energy flow, try positioning your main seating area towards the East. Would you like specifics on color palettes?";
    }

    async performVastuAudit(roomType, layoutDescription) {
        // Realistic mock based on input
        await new Promise(r => setTimeout(r, 1500)); // Simulate thinking

        const score = 7 + Math.floor(Math.random() * 3);
        return {
            score,
            summary: `This ${roomType} has a strong foundation with some minor alignment issues. The current object placement allows for decent energy flow, but a few adjustments could significantly enhance the space's Harmony.`,
            pros: [
                "Main entrance/access point is clear of obstructions",
                "Central space is well-defined and spacious",
                "Furniture height is balanced across the room"
            ],
            cons: [
                "Consider moving heavy items to the South-West corner for stability",
                "Electronic items (like TVs) perform best in the South-East quadrant",
                "Ensure there is a small gap (2-3cm) between furniture and walls"
            ]
        };
    }
}

export const geminiService = new GeminiService();
