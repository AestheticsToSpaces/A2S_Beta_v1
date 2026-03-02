// Placeholder images from Picsum
const MOCK_IMAGES = {
    livingModern: "https://picsum.photos/id/10/1200/800",
    livingBoho: "https://picsum.photos/id/11/1200/800",
    bedLuxury: "https://picsum.photos/id/12/1200/800",
    sofa: "https://picsum.photos/id/20/400/400",
    lamp: "https://picsum.photos/id/21/400/400",
    paint: "https://picsum.photos/id/22/400/400",
    table: "https://picsum.photos/id/23/400/400"
};

const PRODUCTS_DB = [
    {
        id: "p1",
        name: "Berkeley 3-Seater Sofa",
        brand: "Pepperfry",
        category: "Furniture",
        price: 28999,
        dimensions: "84\"W x 38\"D x 34\"H",
        color: "Forest Green",
        colorHex: "#2D4F1E",
        material: "Performance Velvet",
        vendor: "Pepperfry",
        alternativeVendor: { name: "Urban Ladder", price: 31000 },
        affiliateLink: "#",
        image: MOCK_IMAGES.sofa
    },
    {
        id: "p2",
        name: "Olive Grove Emulsion",
        brand: "Asian Paints",
        category: "Paint",
        price: 3200,
        color: "Olive Grove",
        colorHex: "#556B2F",
        vendor: "Asian Paints",
        affiliateLink: "#",
        image: MOCK_IMAGES.paint
    },
    {
        id: "p3",
        name: "LACK Coffee Table",
        brand: "IKEA",
        category: "Furniture",
        price: 2499,
        dimensions: "90x55 cm",
        color: "White",
        colorHex: "#FFFFFF",
        vendor: "IKEA",
        affiliateLink: "#",
        image: MOCK_IMAGES.table
    },
    {
        id: "p4",
        name: "Arteriors Floor Lamp",
        brand: "Kapoor Lights",
        category: "Lighting",
        price: 5500,
        color: "Brass",
        colorHex: "#B5A642",
        vendor: "Amazon India",
        affiliateLink: "#",
        image: MOCK_IMAGES.lamp
    },
    {
        id: "p5",
        name: "Jaipuri Hand-Knotted Rug",
        brand: "Jaipur Rugs",
        category: "Decor",
        price: 12000,
        dimensions: "5x8 ft",
        color: "Beige",
        colorHex: "#F5F5DC",
        vendor: "Jaipur Rugs",
        affiliateLink: "#",
        image: "https://picsum.photos/id/24/400/400"
    }
];

export const DESIGNS_DATA = [
    {
        id: "d1",
        title: "Urban Zen Sanctuary",
        description: "A modern minimalist living room optimized for small Indian apartments under ₹50k.",
        image: "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?q=80&w=2000&auto=format&fit=crop",
        roomType: "Living Room",
        style: "Modern",
        totalCost: 34698,
        tags: ["Compact", "Budget Friendly", "Green Accents"],
        products: [PRODUCTS_DB[0], PRODUCTS_DB[1], PRODUCTS_DB[2]]
    },
    {
        id: "d2",
        title: "Bohemian Rhapsody",
        description: "Vibrant colors and textures for a lively family space.",
        image: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?q=80&w=2000&auto=format&fit=crop",
        roomType: "Living Room",
        style: "Boho",
        totalCost: 55000,
        tags: ["Colorful", "Textured", "Artistic"],
        products: [PRODUCTS_DB[0], PRODUCTS_DB[4], PRODUCTS_DB[3]]
    },
    {
        id: "d3",
        title: "Minimalist Nordic Bedroom",
        description: "Calm tones and functional furniture for deep rest.",
        image: "https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?q=80&w=2000&auto=format&fit=crop",
        roomType: "Bedroom",
        style: "Minimal",
        totalCost: 42000,
        tags: ["Peaceful", "White", "Wood"],
        products: [PRODUCTS_DB[2], PRODUCTS_DB[3]]
    },
    {
        id: "d4",
        title: "Heritage Luxury Dining",
        description: "Traditional Indian aesthetics meeting modern comfort.",
        image: "https://images.unsplash.com/photo-1617806118233-18e1de247200?q=80&w=2000&auto=format&fit=crop",
        roomType: "Dining",
        style: "Traditional",
        totalCost: 85000,
        tags: ["Royal", "Wood", "Ornate"],
        products: [PRODUCTS_DB[3], PRODUCTS_DB[4]]
    },
    {
        id: "d5",
        title: "Modern Loft Kitchen",
        description: "Open concept kitchen with industrial touches.",
        image: "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?q=80&w=2000&auto=format&fit=crop",
        roomType: "Kitchen",
        style: "Industrial",
        totalCost: 120000,
        tags: ["Industrial", "Open", "Grey"],
        products: [PRODUCTS_DB[1], PRODUCTS_DB[2]]
    }
];

export const INITIAL_FILTER_STATE = {
    minPrice: 0,
    maxPrice: 200000,
    styles: [],
    roomTypes: []
};
