// API configuration  
// Use relative path so Vite dev proxy can handle routing
// This works in both development and production (via ngrok)
const API_BASE_URL = '';

export { API_BASE_URL };

export interface KOL {
    id: string;
    name: string;
    style: string;
    display_name: string;
}

export interface OutfitItem {
    role: string;
    image_url: string;
    id: string;
}

export interface Outfit {
    id: string;
    items: OutfitItem[];
    score: number;
    style_fit: number;
    coherence: number;
    explanation: {
        style: string;
        influence: string;
        confidence: string;
    };
}

export interface GenerateResponse {
    outfits: Outfit[];
    alpha: number;
    beta: number;
    beta_used: number;
    pref: number;
    conf: number;
    step: number;
}

export interface FeedbackResponse {
    updated: boolean;
    reward: number;
    pref: number;
    conf: number;
    beta: number;
}

export const apiClient = {
    async createSession(): Promise<string> {
        const response = await fetch(`${API_BASE_URL}/api/session/create`, {
            method: 'POST',
        });
        const data = await response.json();
        return data.session_id;
    },

    async setGender(sessionId: string, gender: 'male' | 'female'): Promise<void> {
        await fetch(`${API_BASE_URL}/api/session/${sessionId}/gender`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ gender }),
        });
    },

    async selectKOL(sessionId: string, kolId: string): Promise<void> {
        await fetch(`${API_BASE_URL}/api/session/${sessionId}/kol`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ kol_id: kolId }),
        });
    },

    async uploadImages(sessionId: string, files: File[]): Promise<void> {
        const formData = new FormData();
        files.forEach((file) => {
            formData.append('files', file);
        });

        const response = await fetch(`${API_BASE_URL}/api/session/${sessionId}/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
    },

    async generateEmbeddings(sessionId: string): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/api/session/${sessionId}/embed`, {
            method: 'POST',
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Embedding generation failed');
        }
    },

    async generateOutfits(
        sessionId: string,
        options?: {
            autoLearn?: boolean;
            manualAlpha?: number;
            manualBeta?: number;
            diversity?: boolean;
        }
    ): Promise<GenerateResponse> {
        // Build query params
        const params = new URLSearchParams();
        if (options?.autoLearn !== undefined) {
            params.append('auto_learn', String(options.autoLearn));
        }
        if (options?.manualAlpha !== undefined) {
            params.append('manual_alpha', String(options.manualAlpha));
        }
        if (options?.manualBeta !== undefined) {
            params.append('manual_beta', String(options.manualBeta));
        }
        if (options?.diversity !== undefined) {
            params.append('diversity', String(options.diversity));
        }

        const url = `${API_BASE_URL}/api/session/${sessionId}/generate${params.toString() ? '?' + params.toString() : ''}`;
        const response = await fetch(url, {
            method: 'POST',
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Outfit generation failed');
        }
        return await response.json();
    },

    async submitFeedback(
        sessionId: string,
        selectedIndices: number[],
        outfits: any[]
    ): Promise<FeedbackResponse> {
        const response = await fetch(`${API_BASE_URL}/api/session/${sessionId}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                selected_indices: selectedIndices,
                outfits: outfits,
            }),
        });
        return await response.json();
    },
};
