export interface OutfitItem {
    id: string;
    top?: string;
    bottom?: string;
    shoes: string;
    dress?: string;
    explanation: {
        style: string;
        influence: string;
        confidence: string;
    };
    style: string;
    influence: string;
    confidence: string;
}

export const MOCK_OUTFITS: OutfitItem[] = [
    {
        id: "outfit-1",
        top: "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=400&h=400&fit=crop",
        bottom: "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=400&h=400&fit=crop",
        shoes: "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop",
        style: "Smart Casual",
        influence: "Daniel Simmons",
        confidence: "94%",
        explanation: {
            style: "Smart Casual",
            influence: "Daniel Simmons",
            confidence: "94%",
        },
    },
    {
        id: "outfit-2",
        dress: "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400&h=600&fit=crop",
        shoes: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400&h=400&fit=crop",
        style: "Elegant Evening",
        influence: "Sofia Martinez",
        confidence: "91%",
        explanation: {
            style: "Elegant Evening",
            influence: "Sofia Martinez",
            confidence: "91%",
        },
    },
    {
        id: "outfit-3",
        top: "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=400&h=400&fit=crop",
        bottom: "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=400&h=400&fit=crop",
        shoes: "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=400&h=400&fit=crop",
        style: "Streetwear Urban",
        influence: "Marcus Reed",
        confidence: "89%",
        explanation: {
            style: "Streetwear Urban",
            influence: "Marcus Reed",
            confidence: "89%",
        },
    },
    {
        id: "outfit-4",
        top: "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400&h=400&fit=crop",
        bottom: "https://images.unsplash.com/photo-1473691955023-da1c49c95c78?w=400&h=400&fit=crop",
        shoes: "https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=400&h=400&fit=crop",
        style: "Minimalist Modern",
        influence: "Emma Chen",
        confidence: "93%",
        explanation: {
            style: "Minimalist Modern",
            influence: "Emma Chen",
            confidence: "93%",
        },
    },
    {
        id: "outfit-5",
        top: "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400&h=400&fit=crop",
        bottom: "https://images.unsplash.com/photo-1582418702059-97ebafb35d09?w=400&h=400&fit=crop",
        shoes: "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=400&h=400&fit=crop",
        style: "Classic Professional",
        influence: "James Liu",
        confidence: "96%",
        explanation: {
            style: "Classic Professional",
            influence: "James Liu",
            confidence: "96%",
        },
    },
    {
        id: "outfit-6",
        dress: "https://images.unsplash.com/photo-1596783074918-c84cb06531ca?w=400&h=600&fit=crop",
        shoes: "https://images.unsplash.com/photo-1603808033176-edd8361b7d8c?w=400&h=400&fit=crop",
        style: "Chic Contemporary",
        influence: "Ava Thompson",
        confidence: "88%",
        explanation: {
            style: "Chic Contemporary",
            influence: "Ava Thompson",
            confidence: "88%",
        },
    },
    {
        id: "outfit-7",
        top: "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=400&h=400&fit=crop",
        bottom: "https://images.unsplash.com/photo-1550614000-4895a10e1bfd?w=400&h=400&fit=crop",
        shoes: "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop",
        style: "Sporty Active",
        influence: "Tyler Brooks",
        confidence: "92%",
        explanation: {
            style: "Sporty Active",
            influence: "Tyler Brooks",
            confidence: "92%",
        },
    },
    {
        id: "outfit-8",
        top: "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&h=400&fit=crop",
        bottom: "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=400&h=400&fit=crop",
        shoes: "https://images.unsplash.com/photo-1560343090-f0409e92791a?w=400&h=400&fit=crop",
        style: "Refined Casual",
        influence: "Mia Davis",
        confidence: "90%",
        explanation: {
            style: "Refined Casual",
            influence: "Mia Davis",
            confidence: "90%",
        },
    },
];
